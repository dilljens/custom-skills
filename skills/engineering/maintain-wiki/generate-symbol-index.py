#!/usr/bin/env python3
"""
Generate a machine-readable symbol index from source files.

Output: JSON array of {name, kind, file, line} objects.
Supports C/C++, Python, TypeScript, Go, Rust.

Usage:
  python generate-symbol-index.py --lang cpp appSrc/**/*.{cpp,h,hpp} > symbol-index.json
  python generate-symbol-index.py --lang py --exclude tests/ mcp_server/**/*.py >> symbol-index.json
"""

import argparse
import json
import os
import re
import sys
from datetime import date
from glob import glob
from typing import Optional


def scan_cpp(filepath: str) -> list[dict]:
    symbols = []
    with open(filepath) as f:
        source = f.read()
    source_no_block = re.sub(r'/\*.*?\*/', '', source, flags=re.DOTALL)
    lines = source_no_block.split("\n")

    depth = 0           # brace depth: 0 = file scope
    in_enum = False
    enum_name = None
    enum_brace = 0
    last_fn_name = None  # track the last function name so we can skip its locals

    for i, line in enumerate(lines):
        stripped = line.strip()
        lineno = i + 1

        if not stripped or stripped.startswith("//") or stripped.startswith("*"):
            continue

        # Track brace depth for scope detection
        # Count braces in this line (before matching anything else)
        line_opens = stripped.count("{")
        line_closes = stripped.count("}")
        if depth > 0 and not in_enum:
            # Inside a function/class body — skip globals, only look for inner classes
            depth = depth + line_opens - line_closes
            if depth == 0 and "}" in stripped:
                last_fn_name = None  # left function scope
            continue

        # --- depth == 0 only from here ---

        # #define MACRO
        m = re.match(r'#\s*define\s+(\w+)', stripped)
        if m:
            symbols.append({"name": m.group(1), "kind": "macro", "file": filepath, "line": lineno})
            continue

        # extern type name[;]
        m = re.match(r'extern\s+(volatile\s+)?(const\s+)?([\w:]+)\s+\**\s*(\w+)', stripped)
        if m and m.group(3) not in ("C", "CXX", "ASM"):
            symbols.append({"name": m.group(4), "kind": "extern", "file": filepath, "line": lineno})
            continue

        # class|struct|union Name
        m = re.match(r'(template\s*<[^>]+>\s+)?(class|struct|union)\s+(\w+)', stripped)
        if m:
            symbols.append({"name": m.group(3), "kind": m.group(2), "file": filepath, "line": lineno})
            continue

        # enum [class] Name
        m = re.match(r'enum\s+(class\s+)?(\w+)', stripped)
        if m:
            symbols.append({"name": m.group(2), "kind": "enum", "file": filepath, "line": lineno})
            in_enum = True
            enum_name = m.group(2)
            enum_brace = 0
            continue

        # namespace Name  (only if it has { on same line)
        m = re.match(r'namespace\s+(\w+)', stripped)
        if m and "{" in stripped:
            symbols.append({"name": m.group(1), "kind": "namespace", "file": filepath, "line": lineno})
            depth = depth + line_opens - line_closes
            continue

        # Inside enum: capture values
        if in_enum:
            enum_brace += stripped.count("{") - stripped.count("}")
            m = re.match(r'(\w+)\s*=\s*', stripped)
            if not m:
                m = re.match(r'(\w+)\s*,', stripped)
                if not m:
                    m = re.match(r'(\w+)\s*$', stripped)
            if m and not stripped.startswith("}") and not stripped.startswith("enum"):
                symbols.append({"name": m.group(1), "kind": "enum-value", "file": filepath, "line": lineno, "parent": enum_name or ""})
            if enum_brace <= 0 and "}" in stripped:
                in_enum = False
                enum_name = None
            continue

        # === FUNCTION DETECTION (depth == 0) ===
        # Heuristic: look for definitions at file scope.
        # Priority 1: return_type name(args)  — typed functions
        # Priority 2: name(args) { — constructor-like
        # Priority 3: Class::name(args) — out-of-class method definitions
        is_fn = False
        fn_name = None

        m = re.match(
            r'((?:static|inline|virtual|constexpr|const|volatile|unsigned|signed|long|short)\s+)*'
            r'([\w:]+\s+|[\w:]+<[^>]+>\s+)'  # return type (word or templated)
            r'\**\s*'  # optional pointer
            r'(operator\s*\(|operator\s*\w+\s*\(|~?\w+)\s*\(',
            stripped
        )
        if m:
            fn_name = m.group(m.lastindex).rstrip("(").strip()
            if fn_name[0].isalnum() and fn_name not in ("if", "for", "while", "switch", "return", "else", "case", "catch", "delete", "new", "sizeof", "decltype", "const", "static", "inline", "virtual", "constexpr", "volatile", "unsigned", "signed", "long", "short", "void"):
                is_fn = True

        # Constructor / void function: name(args) {
        if not is_fn:
            m = re.match(r'(\w+)\s*\(', stripped)
            if m:
                candidate = m.group(1)
                if candidate not in ("if", "for", "while", "switch", "return", "else", "case", "catch", "sizeof", "delete", "new", "decltype"):
                    if "{" in stripped:
                        fn_name = candidate
                        is_fn = True

        # Class::name(args) definition
        if not is_fn:
            m = re.match(r'(\w+)::(\w+)\s*\(', stripped)
            if m:
                fn_name = f"{m.group(1)}::{m.group(2)}"
                is_fn = True

        if is_fn and fn_name:
            symbols.append({"name": fn_name.rstrip("("), "kind": "function", "file": filepath, "line": lineno})
            last_fn_name = fn_name
            depth = line_opens - line_closes
            if depth < 0:
                depth = 0
            continue

        # Global/extern variable at file scope (depth == 0, haven't entered a function)
        # Line must end with = or ; or {  (assignment/declaration, not function call)
        m = re.match(
            r'(static\s+|constexpr\s+|const\s+)?'
            r'(uint\d+_t|int\d+_t|bool|int|void|float|double|char|size_t|'
            r'uint32_t|uint16_t|uint8_t|int32_t|int16_t|int8_t|'
            r'uint64_t|int64_t|Result|Handle|Timestamp|MessageId|DeviceId|'
            r'BoardState|BoardType|BusType|SystemConfig)'
            r'\s+\**\s*(\w+)\s*(=|;|\{)',
            stripped
        )
        if m:
            symbols.append({"name": m.group(3), "kind": "global", "file": filepath, "line": lineno})
            continue

        # std::array<T,N> name = ... at file scope
        m = re.match(r'(static\s+|constexpr\s+)?std::array\s*<\s*[^>]+\s*>\s+(\w+)\s*(=|;)', stripped)
        if m:
            symbols.append({"name": m.group(2), "kind": "global", "file": filepath, "line": lineno})
            continue

        # volatile|const type name at file scope
        m = re.match(r'(volatile|const)\s+(uint\d+_t|int\d+_t|bool|int|uint32_t)\s+\**\s*(\w+)\s*(=|;)', stripped)
        if m:
            symbols.append({"name": m.group(3), "kind": "global", "file": filepath, "line": lineno})
            continue

        # extern "C" { } block - update depth
        if stripped.startswith('extern "C"'):
            depth = depth + line_opens - line_closes
            continue

        # Any other brace opens at file scope — likely class/struct body
        depth = depth + line_opens - line_closes
        if depth < 0:
            depth = 0

    return symbols


def scan_python(filepath: str) -> list[dict]:
    symbols = []
    with open(filepath) as f:
        lines = f.readlines()
    for i, line in enumerate(lines):
        stripped = line.strip()
        lineno = i + 1
        m = re.match(r'^(async\s+)?def\s+(\w+)\s*\(', stripped)
        if m:
            symbols.append({"name": m.group(2), "kind": "function", "file": filepath, "line": lineno})
            continue
        m = re.match(r'^class\s+(\w+)', stripped)
        if m:
            symbols.append({"name": m.group(1), "kind": "class", "file": filepath, "line": lineno})
            continue
    return symbols


def scan_go(filepath: str) -> list[dict]:
    symbols = []
    with open(filepath) as f:
        lines = f.readlines()
    for i, line in enumerate(lines):
        stripped = line.strip()
        lineno = i + 1
        m = re.match(r'^func\s+(\w+)', stripped)
        if m:
            symbols.append({"name": m.group(1), "kind": "function", "file": filepath, "line": lineno})
            continue
        m = re.match(r'^type\s+(\w+)\s+(struct|interface)', stripped)
        if m:
            symbols.append({"name": m.group(1), "kind": m.group(2), "file": filepath, "line": lineno})
            continue
        m = re.match(r'^type\s+(\w+)\s+', stripped)
        if m:
            symbols.append({"name": m.group(1), "kind": "type", "file": filepath, "line": lineno})
            continue
    return symbols


def scan_rust(filepath: str) -> list[dict]:
    symbols = []
    with open(filepath) as f:
        lines = f.readlines()
    for i, line in enumerate(lines):
        stripped = line.strip()
        lineno = i + 1
        m = re.match(r'^fn\s+(\w+)', stripped)
        if m:
            symbols.append({"name": m.group(1), "kind": "function", "file": filepath, "line": lineno})
            continue
        m = re.match(r'^(pub\s+)?(struct|enum|trait)\s+(\w+)', stripped)
        if m:
            symbols.append({"name": m.group(3), "kind": m.group(2), "file": filepath, "line": lineno})
            continue
        m = re.match(r'^(pub\s+)?(const|static)\s+(mut\s+)?(\w+)', stripped)
        if m:
            symbols.append({"name": m.group(4), "kind": m.group(2), "file": filepath, "line": lineno})
            continue
    return symbols


def scan_typescript(filepath: str) -> list[dict]:
    symbols = []
    with open(filepath) as f:
        lines = f.readlines()
    for i, line in enumerate(lines):
        stripped = line.strip()
        lineno = i + 1
        m = re.match(r'^(export\s+)?(function|const|let|var)\s+(\w+)', stripped)
        if m:
            symbols.append({"name": m.group(3), "kind": m.group(2), "file": filepath, "line": lineno})
            continue
        m = re.match(r'^(export\s+)?(class|interface|type|enum)\s+(\w+)', stripped)
        if m:
            symbols.append({"name": m.group(3), "kind": m.group(2), "file": filepath, "line": lineno})
            continue
    return symbols


SCANNERS = {
    "cpp": scan_cpp,
    "c": scan_cpp,
    "h": scan_cpp,
    "hpp": scan_cpp,
    "py": scan_python,
    "go": scan_go,
    "rs": scan_rust,
    "ts": scan_typescript,
    "tsx": scan_typescript,
    "js": scan_typescript,
    "jsx": scan_typescript,
}


def main():
    parser = argparse.ArgumentParser(description="Generate symbol index from source files")
    parser.add_argument("files", nargs="+", help="Source file globs to scan")
    parser.add_argument("--lang", default=None, help="Force language (cpp, py, go, rs, ts)")
    parser.add_argument("--exclude", default="", help="Comma-separated directory patterns to exclude")
    parser.add_argument("--output", "-o", default=None, help="Write to file instead of stdout")
    args = parser.parse_args()

    exclude_patterns = [p.strip() for p in args.exclude.split(",") if p.strip()]

    all_files = []
    for pattern in args.files:
        all_files.extend(glob(pattern, recursive=True))

    # Deduplicate and filter
    seen = set()
    filtered = []
    for f in all_files:
        real = os.path.realpath(f)
        if real in seen:
            continue
        seen.add(real)
        if any(excl in f for excl in exclude_patterns):
            continue
        filtered.append(f)

    all_symbols = []
    for filepath in sorted(filtered):
        ext = os.path.splitext(filepath)[1].lstrip(".")
        lang = args.lang or ext
        scanner = SCANNERS.get(lang)
        if scanner:
            try:
                symbols = scanner(filepath)
                all_symbols.extend(symbols)
            except Exception as e:
                print(f"Warning: {filepath}: {e}", file=sys.stderr)

    result = {
        "generated": str(date.today()),
        "count": len(all_symbols),
        "symbols": all_symbols,
    }

    output = json.dumps(result, indent=2)

    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
            f.write("\n")
        print(f"Wrote {len(all_symbols)} symbols to {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
