# Maintain Wiki — Reference

## `_index.md` template

Two sections: quick reference at top, full architecture below.

```markdown
# <Project Name> — Architecture Overview

**Build**: `<cmd>`  **Flash**: `<cmd>`  **Test**: `<cmd>` (<N> tests)

## Quick reference

### Key files
| Purpose | File |
|---------|------|
| Program entry | `<file>:<line>` |
| <purpose> | `<file>` |

### Test per domain
| Domain | Run |
|--------|-----|
| <Domain> | `<cmd> <filter>` |

### Top symbols
| Symbol | Kind | File |
|--------|------|------|

### Domain one-liners
| Domain | Doc |
|--------|-----|
| <Domain> | `features/<domain>.md` — <1 line> |

## Reading guide
| I want to... | Read |
|-------------|------|
| Know what NOT to do | `_standards.md` § Rules |
| Know how to write new code | `_standards.md` § Practices |
| Match existing conventions | `_standards.md` § Patterns |
| Know how system runs | `_lifecycle.md` |
| Know who uses what | `_deps.md` |
| Find a definition | Search `symbol-index.json` |
| Know what's tested | `_tests.md` |

## Entry points
| Trigger | File | Description |
|----------|------|-------------|

## Topology
```
<dir>/         (<pattern>)
  ├── <file> ──▶ <dep1> ──▶ <dep2>
```

## "Need to change X? Start here"
| Change | Look at |
|--------|---------|

## Domain registry
| Domain | Doc | Files | Purpose |
|--------|-----|-------|---------|

## Existing docs
- [README.md](../../README.md) — project overview, setup
```

Quick reference generated from: build scripts, test runner, symbol index (top 10 overarching symbols), domain descriptions.

---

## `_standards.md` template

Three sections: Rules (DON'T — catastrophic), Practices (SHOULD — aspirational), Patterns (TYPICALLY — descriptive).

```markdown
# Coding Standards

## Rules — What you must NEVER do

Breaking these causes bugs hard to find.

| # | Rule | Why | Check |
|---|------|-----|-------|
| 1 | Never <action> | <what breaks> | <how to verify> |

## Practices — How to write NEW code

Standards for code you add or refactor. Existing code may not comply.

### Function design
- Single responsibility. Small (<30 lines). Name for intent.

### State management
- Limit globals. Pass state as params. Make side effects visible.

### Error handling
- Never discard errors. Propagate with context.

### Code clarity
- Comments explain WHY not WHAT. Delete dead code. No magic numbers.

### Naming
- Reveal intent at call site. Booleans: `is*`, `has*`, `can*`.

### Testing
- New behavior → new test. Tests with tests, not `#ifdef UNIT_TEST`.

## Patterns — How code IS written

Detected conventions. Match these so new code fits in.

### Error handling
**Pattern**: <describe>  **Example**: `<file>:<line>`
**Rule**: <constraint>

### Naming
| Kind | Style | Example |
|------|-------|---------|
| Files | <style> | `<example>` |
| Functions | <style> | `<example>()` |
```

### Stack-specific practice defaults

**C/C++ embedded**: zero-init, no heap, enum class, fixed-width ints, no recursion, always brace, document shared variables, const everything.

**Python**: type hints on public fns, dataclasses for data, pathlib not strings, pytest over unittest.

**TypeScript/React**: explicit Props type, extract hooks from components, derive state don't duplicate, one export per file.

**Rust**: thiserror/anyhow, never .unwrap() in lib code, borrow before move, derive Debug/Clone/PartialEq by default.

**Go**: wrap errors with context (%w), short names in small scope, package name is part of API.

### Rule detection heuristics

Scan for `assert`, `BR_PANIC`, `if (x == nullptr) return`, `while(1)`, guard flags. These tell what author considered catastrophic.

Also scan AGENTS.md, CONTEXT.md, README for explicit rules.

### Pattern detection heuristics

| Category | Detect |
|----------|--------|
| Error handling | throw vs return; `Result`, `Either`, `{data, error}` patterns |
| Async flow | async/await, callbacks, event emitters, state-machine switch/case |
| Module structure | barrel files, import style (named vs default) |
| State management | hooks, stores, globals, actors |
| Naming | Sample 20+ names per layer, detect dominant style |

---

## `_deps.md` template

```markdown
# Dependency Map

| Module | Depends on | Depended on by |
|--------|-----------|----------------|

## High-risk (≥3 dependents)

## Solitary (0 dependents)

## Verify commands per module

| Module | Test command |
|--------|-------------|
```

---

## `_tests.md` template

```markdown
# Test Inventory

**Framework**: <name>  **Run all**: `<cmd>` (<N> tests)

## Per-domain
| Domain | Run command | Files | Tests | Confidence |
|--------|------------|-------|-------|-----------|

## Untested domains

## Conventions
- Location: `<dir>`
- Naming: `<pattern>`

## Add a test
1. Create `<file>`
2. Follow pattern from nearest test file
3. Run `<cmd>` to verify
```

---

## `_lifecycle.md` template

```markdown
# Runtime Lifecycle

## Entry points
| Access | Path | What |
|--------|------|------|

## Core state machine
```
<StateA> → <StateB> → (<StateC>)* → <End>
```
| State | Trigger | → Next |

## Error recovery
| Failure | Detection | Recovery |
|---------|-----------|----------|

## Entity lifecycles

## Background processes
| Process | Rate | Context |
|---------|------|---------|
```

---

## `_symbols.md` template

Lightweight symbol lookup. One-line entries per symbol in a markdown table. Grep-friendly, no JSON parsing needed:

```markdown
# Symbol Index

<N> symbols across <M> domains.

| Name | Kind | Domain | File:Line |
|------|------|--------|-----------|
| `<class>` | class | <domain> | `<path>:<line>` |
| `<function>` | function | <domain> | `<path>:<line>` |
| `<global>` | global | <domain> | `<path>:<line>` |
```

Usage:
```bash
rg 'BusHandle' docs/wiki/_symbols.md        # find any symbol
rg 'communication' docs/wiki/_symbols.md    # all symbols in a domain
```

---

## Module doc template

```markdown
# <Domain>

**Source**: `<files>`  **Updated**: `YYYY-MM-DD`  (N files)

## What it does
2-4 sentences.

## Architecture
ASCII flow diagram.

## Key functions / components
| Name | Kind | File:Line | Purpose |
|------|------|-----------|---------|
| `<fn>()` | function | `<file>:<line>` | <1 line> |
| `<class>` | class | `<file>:<line>` | <1 line> |

Populated from source scan during `refresh symbols`. Each domain doc has an inline symbol table — AI reads the domain doc and gets symbols, architecture, data flow, and edge cases in one file.

## Data flow
Numbered steps.

## Edge cases & gotchas

## Dependencies
| Depends on | For |

## Consumed by
| Consumer | How |

## Related domains
| Domain | Doc | Relationship |
```

### Stack-specific sections

| Stack | Add |
|-------|-----|
| React/Next.js | Components, Hooks |
| Python API | Endpoints |
| Go | Commands/Handlers |
| Rust | Types/Traits |
| C/C++ embedded | Globals, State Machines, Macros, PIO Programs, Protocol, Pin Map |

---

## Domain detection

1. **Directory clusters** — strongest signal
2. **Import communities** — files importing each other heavily
3. **Co-location** — similar names in same dir
4. **Barrel exports** — same index.ts/__init__.py/mod.rs
5. **Config-defined** — monorepo packages

2–20 files per domain.

---

## File scope defaults

| Stack | Include | Exclude |
|-------|---------|---------|
| TS/JS | `src/**/*.{ts,tsx,js,jsx}` | `*.test.*`, `__tests__`, `*.d.ts`, `*.stories.*` |
| Python | `**/*.py` | `test_*.py`, `tests/`, `conftest.py` |
| Go | `**/*.go` | `*_test.go` |
| Rust | `src/**/*.rs` | — |
| C/C++ | `src/**/*.{cpp,h,hpp,c}` | `*test*`, `build/`, `*.pio.h` |

Exclude `node_modules/`, `.git/`, `__pycache__/`, `.venv/`.

---

## `_symbols.md` format

See `_symbols.md` template above for the markdown table format. No JSON — uses markdown tables that are both human-readable and grep-friendly.

Scanner (`generate-symbol-index.py`) maps source files to domains from the `features/` directory structure and writes symbols into a single `_symbols.md` table + updates each domain doc's inline "Key functions / components" table.

Kinds per language: C/C++ (`class`, `struct`, `enum`, `enum-value`, `function`, `global`, `extern`, `macro`, `namespace`), TS/JS (`class`, `interface`, `type`, `enum`, `function`, `const`, `export`), Python (`class`, `function`), Go (`struct`, `interface`, `function`, `var`, `const`, `type`), Rust (`struct`, `enum`, `fn`, `trait`, `impl`, `const`, `static`, `macro`).

---

## README.md template

```markdown
# Codebase Wiki

AI-optimized codebase map.

## For humans
1. `_index.md` — quick reference + architecture (keep open)
2. `_standards.md` § Rules — what never to do
3. `_standards.md` § Practices — how to write new code
4. `_lifecycle.md` — how it runs
5. `_deps.md` — who depends on whom
6. `_tests.md` — what's tested
7. `features/<domain>.md` — module deep dive

## For agents

### Adding a feature
_index → _standards (Rules + Practices) → domain doc (symbols + architecture) → _standards (Patterns) → _deps → _tests

### Debugging
_lifecycle → _symbols.md (find symbol's domain) → domain doc (edge cases) → _deps → _standards (Rules)

### Refactoring
_deps (high-risk & solitary) → _tests (gaps) → domain docs (target + consumers) → refresh symbols

### Unfamiliar code
_symbols.md (find symbol → domain) → _index (domain overview) → domain doc

### Finding symbols
```bash
rg '<symbol>' docs/wiki/_symbols.md       # all match locations
rg '<domain>' docs/wiki/_symbols.md       # all symbols in a domain
```

## Commands
- `make wiki` — initialize
- `refresh symbols` — regenerate _symbols.md + domain doc tables
- `refresh standards` — propose updated _standards.md
- `refresh lifecycle` — propose updated _lifecycle.md

## Stale docs
Read source. If doc is wrong, propose update. Don't silently ignore.

## Plans
`docs/wiki/plans/` — architecture proposals and migration plans. Justify decisions (not living docs).
```

---

## Edge cases

**New project**: `make wiki` builds from scratch. Links existing README.

**Existing docs/**: Detected, linked from `_index.md`, excluded from wiki scope.

**File moved/deleted**: `refresh symbols` reflects current state.

**Large refactor**: Re-run `make wiki` if domain structure changed, `refresh symbols` if only definitions changed.

**Monorepo**: Detect workspace configs. Each member gets `docs/wiki/<member>/`.
