# Maintain Wiki — Reference

## `_index.md` template

Two sections: quick reference at top, full architecture below.

```markdown
# <Project Name> — Architecture Overview

**Build**: `<cmd>`  **Test**: `<cmd>` (<N> tests)

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
| Understand a module | `features/<domain>.md` |

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

Quick reference generated from: build scripts, test runner, domain descriptions.

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

Only include the stack(s) detected in this project. Below are the available defaults — pick matching ones:

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
| C/C++ embedded | Globals, Macros, PIO Programs, Protocol, Pin Map |

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

## README.md template

```markdown
# Codebase Wiki

AI-optimized codebase map.

## For humans
1. `_index.md` — quick reference + architecture (keep open)
2. `_standards.md` § Rules — what never to do
3. `_standards.md` § Practices — how to write new code
4. `features/<domain>.md` — module deep dive

## For agents

### Adding a feature
_index → _standards (Rules + Practices) → domain doc → _standards (Patterns)

### Debugging
_index → domain doc (edge cases) → _standards (Rules)

### Refactoring
domain docs (target + consumers) → _index (topology)

### Unfamiliar code
_index (domain overview) → domain doc

## Commands
- `make wiki` — initialize
- `refresh standards` — propose updated _standards.md

## Stale docs
Read source. If doc is wrong, propose update. Don't silently ignore.

## Plans
`docs/wiki/plans/` — architecture proposals and migration plans. Justify decisions (not living docs).
```

---

## Edge cases

**New project**: `make wiki` builds from scratch. Links existing README.

**Existing docs/**: Detected, linked from `_index.md`, excluded from wiki scope.

**Large refactor**: Re-run `make wiki` if domain structure changed.

**Monorepo**: Detect workspace configs. Each member gets `docs/wiki/<member>/`.
