#!/usr/bin/env python3
"""
Generate a lightweight symbol index from source files.

Output: markdown table (_symbols.md format).
Also updates domain doc inline symbol tables if --docs-dir is provided.

Usage:
  python generate-symbol-index.py --lang cpp --docs-dir docs/wiki appSrc/**/*.{cpp,h}
  python generate-symbol-index.py --lang py --docs-dir docs/wiki mcp_server/**/*.py
"""

import argparse
import os
import re
import sys
from glob import glob


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
    parser.add_argument("--exclude", default="", help="Comma-separated patterns to exclude")
    parser.add_argument("--output", "-o", default=None, help="Write _symbols.md to file (default: stdout)")
    parser.add_argument("--docs-dir", default=None, help="Path to docs/wiki/ for domain mapping")
    args = parser.parse_args()

    exclude_patterns = [p.strip() for p in args.exclude.split(",") if p.strip()]

    all_files = []
    for pattern in args.files:
        all_files.extend(glob(pattern, recursive=True))

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

    # Build domain map from docs/wiki/features/*.md filenames
    domain_map = {}  # file prefix -> domain name
    if args.docs_dir:
        features_dir = os.path.join(args.docs_dir, "features")
        if os.path.isdir(features_dir):
            for doc_file in os.listdir(features_dir):
                if doc_file.endswith(".md"):
                    domain = doc_file.replace(".md", "")
                    # domain name matches the features/*.md filename
                    domain_map[domain] = domain

    all_symbols = []
    for filepath in sorted(filtered):
        ext = os.path.splitext(filepath)[1].lstrip(".")
        lang = args.lang or ext
        scanner = SCANNERS.get(lang)
        if scanner:
            try:
                symbols = scanner(filepath)
                for s in symbols:
                    domain = infer_domain(filepath, domain_map)
                    s["domain"] = domain
                all_symbols.extend(symbols)
            except Exception as e:
                print(f"Warning: {filepath}: {e}", file=sys.stderr)

    # Build markdown table output
    lines = [
        "# Symbol Index",
        "",
        f"{len(all_symbols)} symbols across {len(domain_map)} domains.",
        "",
        "| Name | Kind | Domain | File:Line |",
        "|------|------|--------|-----------|",
    ]
    kind_order = {"class": 0, "struct": 1, "function": 2, "global": 3, "extern": 4,
                   "enum": 5, "enum-value": 6, "macro": 7, "namespace": 8}
    all_symbols.sort(key=lambda s: (kind_order.get(s.get("kind", ""), 9), s["name"].lower()))

    for s in all_symbols:
        name = s["name"]
        kind = s.get("kind", "")
        domain = s.get("domain", "—")
        loc = f"{s['file']}:{s['line']}"
        lines.append(f"| `{name}` | {kind} | {domain} | `{loc}` |")

    # Update domain doc inline symbol tables if requested
    if args.docs_dir:
        _update_domain_docs(args.docs_dir, all_symbols, domain_map)

    output = "\n".join(lines) + "\n"

    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"Wrote {len(all_symbols)} symbols to {args.output}", file=sys.stderr)
    else:
        print(output)


def infer_domain(filepath: str, domain_map: dict) -> str:
    parts = filepath.replace("\\", "/").split("/")
    for part in parts:
        part_lower = part.lower()
        for dom_name in domain_map:
            # Exact match
            if part_lower == dom_name:
                return dom_name
    # Fuzzy: directory name is a prefix or substring of a domain name
    for part in parts:
        part_lower = part.lower()
        for dom_name in domain_map:
            if part_lower in dom_name or dom_name in part_lower:
                return dom_name
    return "—"


def _update_domain_docs(docs_dir: str, symbols: list, domain_map: dict):
    """Update inline symbol tables in features/<domain>.md files."""
    features_dir = os.path.join(docs_dir, "features")
    if not os.path.isdir(features_dir):
        return

    # Group symbols by domain
    by_domain = {}
    for s in symbols:
        dom = s.get("domain", "—")
        if dom == "—":
            continue
        by_domain.setdefault(dom, []).append(s)

    for domain_name, dom_symbols in by_domain.items():
        doc_path = os.path.join(features_dir, f"{domain_name}.md")
        if not os.path.isfile(doc_path):
            continue

        # Read current doc and find "Key functions" section to replace
        with open(doc_path) as f:
            content = f.read()

        # Build replacement table
        table_lines = [
            "| Name | Kind | File:Line | Purpose |",
            "|------|------|-----------|---------|",
        ]
        kind_order = {"class": 0, "struct": 1, "function": 2, "global": 3, "extern": 4,
                       "enum": 5, "enum-value": 6, "macro": 7, "namespace": 8}
        dom_symbols.sort(key=lambda s: (kind_order.get(s.get("kind", ""), 9), s["name"].lower()))

        for s in dom_symbols:
            loc = f"{s['file']}:{s['line']}"
            table_lines.append(f"| `{s['name']}` | {s.get('kind', '')} | `{loc}` | |")

        new_table = "\n".join(table_lines)

        # Replace content between | Name ... | ... | and the next ## section
        pattern = re.compile(
            r'(\| Name \|.*?\| Purpose \|\n\|------.*?\n)(.*?)(\n## )',
            re.DOTALL
        )
        match = pattern.search(content)
        if match:
            new_content = content[:match.start()] + match.group(1) + new_table[len(match.group(1)):] + content[match.end() - len(match.group(3)):]
            # Simpler approach: find the table and replace it
            table_start = match.start()
            table_end = match.end() - len(match.group(3))
            content = content[:table_start] + new_table + "\n\n" + match.group(3) + content[table_end + len(match.group(3)):]

            with open(doc_path, "w") as f:
                f.write(content)

            print(f"  Updated {domain_name}.md: {len(dom_symbols)} symbols", file=sys.stderr)


if __name__ == "__main__":
    main()
