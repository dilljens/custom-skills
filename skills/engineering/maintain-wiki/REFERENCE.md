# Maintain Wiki — Reference

## `_quickref.md` template

A single page designed to stay open while coding. Generated from existing docs + symbol index + build scripts:

```markdown
# Quick Reference

**Build**: `<build command>`
**Flash/Deploy**: `<flash command>`
**Test**: `<test command>` (<count> tests)

## Key files

| Purpose | File |
|---------|------|
| Program entry | `<entry-point-file>:<line>` |
| System initialization | `<init-file>:<function>()` |
| Protocol spec | `<protocol-doc-path>` |

(Populate from the entry-point registry in `_index.md`. List the 10 most critical files a developer touches daily.)

## Test commands by domain

| Domain | Run command |
|--------|------------|
| `<domain>` | `<test-runner> <filter>` |

(Deduced from the project's test runner. Use substring filters or `-k` flags to scope tests to each domain.)

## Top symbols

| Symbol | Kind | File |
|--------|------|------|
| `<most-used-class>` | class | `<file>:<line>` |
| `<key-global>` | global | `<file>:<line>` |

(Scanned from `symbol-index.json`: pick the 10-15 most foundational symbols — widely-used classes, key globals, entry-point functions.)

## Domains at a glance

| Domain | One-liner | Doc |
|--------|----------|-----|
| `<Domain Name>` | <one-sentence purpose> | `features/<domain>.md` |
```

---

## `_rules.md` template

Coding commandments — what you must NEVER do. Detected from AGENTS.md, existing docs, and catastrophic-failure patterns in source:

```markdown
# Coding Commandments

These are NOT style preferences. Breaking any of these will cause bugs that are hard to find.

## Core safety rules

| # | Rule | Why | Enforcement |
|---|------|-----|-------------|
| 1 | Never allocate on the heap | All memory is static/stack | Review: grep for `new\|malloc` |
| 2 | Never block in a time-critical path | Starves the event loop or bus | Review: no sleep/delay in hot paths |
| 3 | Never write to <shared-resource> from <wrong-context> | Race condition / corruption | Code: guard check at call site |

## Domain-specific rules

| # | Rule | Domain | Why |
|---|------|--------|-----|
| 4 | Never <action> without <guard-check> | <domain> | <what breaks> |
| 5 | Never <modify-state> while <concurrent-access> | <domain> | <what corrupts> |
```

Detection: scan for `assert`, `BR_PANIC`, `if (x == nullptr) return`, `while(1)`, guard conditionals (`board_state ==`, `is_initialized`). These guard statements tell you what the author considered a catastrophic failure — and therefore what you must never trigger.

Also scan AGENTS.md, CONTEXT.md, and README for explicitly stated rules. Rules from existing docs get highest priority.

Rules are editorial (approved by user), not auto-generated. Present detected rules for discussion.

---

## `_tests.md` template

```markdown
# Test Inventory

**Framework**: <framework>
**Run all**: `<test command>` (<count> tests)

## Per-domain run commands

| Domain | Run command | Source files | Test files | Tests | Confidence |
|--------|------------|-------------|-----------|-------|-----------|
| <Domain> | `<runner> <filter>` | N | `<test-file>` | M | High/Med/Low/None |
| <Domain> | _(untested)_ | N | — | 0 | None |

## Untested domains
- **<Domain>** (N files) — no tests. Risky to refactor.

## Test file conventions
- Location: `<test-directory>`
- Naming: `<naming-pattern>`
- Base class / fixture: `<test-helper>`

## How to add a test
1. Create `<test-dir>/test_<name>.<ext>`
2. Follow existing pattern in the nearest test file
3. Run `<test command>` to verify
```

The "Per-domain run command" column is critical — it tells both humans and AI exactly what to run after changing a domain. Deduce from the test runner's filter mechanism.

---

## `_lifecycle.md` template

State machine documentation with error recovery. Editorial:

```markdown
# Runtime Lifecycle

## Entry points
| Access | Path | What happens |
|--------|------|-------------|
| <trigger> | `<file>` | <description> |

## Core state machine
```
<StateA> → <StateB> → (<StateC> → <StateB>)* → <Terminal>
```

States and transitions:
| State | Trigger | → Next state |
|-------|---------|--------------|
| `<state>` | <event> | `<next>` |

## Error recovery

| Failure mode | Detection | Recovery behavior |
|-------------|-----------|-------------------|
| <what fails> | <how detected> | <what happens> |
| Peer disconnect | Timeout counter > threshold | Degrade to <slow-mode>, retry at <interval> |
| <resource> unavailable | <check> returns false | <panic / graceful degradation> |

## Entity lifecycles
### <Entity>
```
<Create> → <Active> → (<SubState> → <Active>)* → <Destroy>
```

## Background / polling
| Process | Frequency | Context |
|---------|-----------|---------|
| <name> | <rate> | <core/thread> |
```

The error recovery section is editorial — fill it in during `make wiki` because recovery paths are often spread across multiple files.

---

## `_deps.md` template

```markdown
# Dependency Map

## Module dependency graph
| Module | Depends on | Depended on by |
|--------|-----------|----------------|
| `<domain-A>` | — | `<domain-B>`, `<domain-C>` |
| `<domain-B>` | `<domain-A>` | — |

## High-risk modules
Modules depended on by 3+ others — changes here have high blast radius:
- `<domain-A>` (depended on by N modules)

## Solitary modules
Modules with no dependents — safe to refactor freely:
- `<domain-Z>`

## Verify commands per module
After changing a module, run these to catch regressions:

| Module | Verify command |
|--------|---------------|
| `<domain-A>` | `<test command>` |
| `<domain-Z>` | _(untested — verify manually by <manual-check>)_ |
```

Detection: scan every source file for import/include/require statements, build a directed graph, classify modules by dependency count.

---

## Module doc template

Every domain doc at `docs/wiki/features/<domain>.md` follows this structure:

```markdown
# <Domain Label>

**Source**: `<file1>`, `<file2>`, ...
**Last updated**: `YYYY-MM-DD`

Files tracked for this domain (...N files)

## What it does
2-4 sentences. Purpose, role in the application, when it's used.

## Architecture
How the pieces connect. State ownership, dependency direction, key interfaces.
Include an ASCII data-flow diagram if the flow is non-trivial.

## Key functions / components
| Name | Location | Purpose |
|------|----------|---------|
| `<function>()` | `<file>:<line>` | <1-line purpose> |
| `<class>` | `<file>:<line>` | <1-line purpose> |

## Data flow
Numbered step-by-step: what triggers this module, what it does, what it emits.

## Edge cases & gotchas
- Unexpected states, race conditions
- Interactions with other modules
- Known failure modes

## Dependencies
| Depends on | For |
|------------|-----|
| `<module-path>` | <why it depends on this> |

## Consumed by
| Consumer module | How it uses this |
|----------------|------------------|
| `<consumer-path>` | <1-line description> |

## Related domains
| Domain | Doc | Relationship |
|--------|-----|-------------|
| <Domain> | `features/<domain>.md` | <how they relate> |
```

### Tech stack adaptations

| Language | Extra section | Content |
|----------|--------------|---------|
| React/Next.js | **Components** | Table of components with props summary |
| React/Next.js | **Hooks** | Table of hooks with return values |
| Go | **Commands / Handlers** | CLI commands or HTTP handlers |
| Python API | **Endpoints** | Route/method/purpose table |
| Rust | **Types / Traits** | Key structs, enums, trait impls |
| C/C++ embedded | **Globals** | Key `extern` variables, file-scope statics |
| C/C++ embedded | **State Machines** | SMF states and transitions |
| C/C++ embedded | **Macros** | Important `#define` constants |
| C/C++ embedded | **PIO Programs** | PIO assembler programs and their pins |
| C/C++ embedded | **Protocol** | Custom wire protocol format, byte layout, command table, CRC scheme |
| Embedded (any) | **Pin Map** | Key GPIO pin assignments (link to external pin doc if exists) |

Detect the stack from config files and auto-add the right sections. The base sections (What it does, Architecture, Data flow, Edge cases, Dependencies) always apply.

---

## `_index.md` template

Spatial map for AI orientation:

```markdown
# <Project Name> — Architecture Overview

**Stack**: <language, framework, board>
**Build**: <build command>
**Test**: <test command, count>
**Flash/Deploy**: <flash command>

## Reading guide
| I want to... | Read |
|-------------|------|
| Understand what this project does | This page, the entry point registry below |
| Know what NOT to do | `_rules.md` |
| Know how to write maintainable new code | `_practices.md` |
| Know how code is written here | `_patterns.md` |
| Know what NOT to do | `_rules.md` |
| Know how the system runs | `_lifecycle.md` |
| Know who uses what | `_deps.md` |
| Find a definition fast | Search `symbol-index.json` |
| Know what's tested | `_tests.md` |
| Explore a module in depth | `features/<domain>.md` |

## Entry point registry
| Trigger | File | Description |
|----------|------|-------------|
| `<command>` | `<file>:<line>` | <1-line description> |

## Topology
```
<directory>/         (<pattern>)
  ├── <file> ──▶ <dep1> ──▶ <dep2>
  └── <file> ──▶ <dep1>
```

## "Need to change X? Start here"
| Change | Look at |
|--------|---------|
| <common task> | `<file-or-directory>`, `<related-doc>` |

## Domain registry
| Domain | Doc | Files | Description |
|--------|-----|-------|-------------|
| <Domain> | `features/<domain>.md` | N | <1-line description> |

## Existing docs
- [README.md](../../README.md) — project overview, setup
```

The "Need to change X?" table is generated by scanning for files that import from each domain, config files, build scripts, and migration commands.

---

## `_practices.md` template

Engineering standards for writing NEW code. Unlike `_patterns.md` (which documents existing conventions) and `_rules.md` (which prevents catastrophic bugs), practices are **prescriptive**: they set the quality bar for code you add or refactor. Existing code may not follow these — that's fine, don't refactor just for compliance. Apply them to what you write NOW.

```markdown
# Engineering Practices

Standards to follow when writing NEW code. Existing code may not match — apply
these to code you add or refactor. These are professional norms, not style nitpicks.

## Function design
- **Single responsibility**: each function does one thing. If you need "and" in the function name, split it.
- **Small**: aim for under 30 lines. Extract helpers for readability, even if only called once.
- **Name for intent**: `processScanResults()` not `handle()`. Name says WHAT it does, not WHEN or HOW.

## State management
- **Limit global state**: each new `extern` or module-level variable is a future debugging session.
- **Pass state as parameters**: prefer `Result doThing(State* state, Input in)` over reading global state.
- **Make side effects obvious**: if a function modifies shared state, make that visible in its signature or name.

## Error handling
- **Always check return values**: never silently discard a `Result`, status code, or error condition.
- **Propagate with context**: attach enough information that the caller can handle the error or log it meaningfully.
- **No bare exceptions**: in languages with exceptions, catch at module boundaries. In C, always check.

## Code clarity
- **Comments explain WHY, not WHAT**: code explains what. Comments explain the reason behind a surprising choice.
- **Delete dead code**: commented-out code blocks rot. If it might be needed later, it's in git history.
- **No magic numbers**: every literal with semantic meaning gets a named constant.
- **One level of abstraction per function**: don't mix low-level register twiddling with high-level business logic.

## Naming
- **Reveal intent at the call site**: `if (isPortTimedOut())` not `if (flag)`. The reader shouldn't need to look up the definition.
- **Booleans**: `isReady`, `hasData`, `canSend` prefix.
- **Setters**: `setLedColor()` not `ledColor()`.
- **Length proportional to scope**: short names for locals (i, n, buf), longer names for globals and APIs.

## Testing
- **New behavior → new test**: any function with >3 branches needs at least one test exercising each path.
- **Tests live with tests**: don't embed test code in production files (no `#ifdef UNIT_TEST` in source).
- **Test the behavior, not the implementation**: if you refactor internals, the test should still pass.

## Refactoring safety
- **Tests first**: before refactoring, ensure the domain has passing tests (check `_tests.md`).
- **One change per commit**: don't mix refactoring and feature work.
- **Incremental**: extract a helper, commit. Rename a variable, commit. Inline a function, commit. Small steps that compile and pass tests at each commit.
```

### Stack-specific practice defaults

When generating `_practices.md`, include language-specific standards:

**C/C++ embedded:**
```markdown
## Memory
- **Zero-init**: `= {}` or `memset` all stack-allocated structs before use.
- **No heap**: unless the project explicitly allows it, never `new`/`malloc`. Use static buffers.
- **const all the things**: every variable and parameter that isn't mutated gets `const`.

## Types
- **Use enum class**: not bare `enum`. Gets you type safety, scoped names, explicit underlying type.
- **Fixed-width types**: use `uint8_t`, `int32_t`, etc. Never `int` in data structures or protocols.
- **Strong typedefs**: `using Timestamp = uint64_t` instead of raw `uint64_t` in interfaces.

## Control flow
- **No recursion**: on embedded systems with limited stack, recursion is dangerous.
- **One return per function**: early returns are fine (guard clauses), but multiple returns in the middle of logic make it hard to reason about cleanup.
- **Always brace**: even single-statement `if`/`for`/`while` bodies get braces.

## Concurrency
- **Document sharing**: if a variable is accessed from multiple cores or interrupts, add a comment.
- **Minimize critical sections**: lock/unlock (or IRQ disable/enable) should span the smallest possible region.
- **Volatile is not a synchronization primitive**: use proper atomics or mutexes.
```

**Python:**
```markdown
## Typing
- **Type hints on all public functions**: parameters and return types.
- **Use dataclasses** for data-only classes. NamedTuple for immutable records.

## Functions
- **Explicit returns**: avoid functions that sometimes return a value and sometimes None.
- **Use `pathlib.Path`** not string paths.

## Testing
- **pytest over unittest**: use fixtures, parametrize, and plain asserts.
```

**TypeScript/React:**
```markdown
## Components
- **Props interface**: every component has an explicit Props type.
- **Extract hooks**: move data fetching and state logic out of components.
- **Co-locate styles**: CSS/SCSS in the same directory as the component.

## State
- **Derive, don't duplicate**: compute values from state instead of storing redundant copies.
- **One state owner**: each piece of state has exactly one component that owns it.

## File structure
- **One export per file**: export one component or function per file. Index file re-exports.
- **Feature folders**: group by feature, not by type (pages/ vs components/ vs hooks/).
```

**Rust:**
```markdown
## Error handling
- **Use `thiserror`** for library error types, `anyhow` for application code.
- **Never `.unwrap()`** in library code. In application code, only where you can justify the panic.

## Ownership
- **Borrow before move**: prefer `&T` and `&mut T` over consuming ownership where possible.
- **Derive when possible**: `#[derive(Debug, Clone, PartialEq)]` by default for data types.

## Modules
- **Hygienic imports**: prefer `use crate::module::Type` over glob imports `use crate::module::*`.
```

**Go:**
```markdown
## Error handling
- **Wrap with context**: `fmt.Errorf("doing X: %w", err)` when propagating.
- **Don't ignore errors**: `_ = doThing()` is a code smell. If you must ignore, comment why.

## Naming
- **Short in small scope**: single-letter names in tight loops. Full words in exported APIs.
- **Getter without Get**: `Count()` not `GetCount()`.

## Packages
- **Package name is part of the API**: `user.Service` not `users.UserService`.
```

---

## `_patterns.md` template

Code archeology — how things are done in this project. Editorial (not auto-generated):

```markdown
# Code Patterns

Detected conventions. Before writing new code, match these patterns.

## Error handling
**Pattern**: <describe the dominant error-handling style>
**Canonical example**: `<file>:<line>` — <what it does>
**Rule**: <constraint on error handling>

## Naming conventions
| Kind | Convention | Example |
|------|-----------|---------|
| Files | <style> | `<example>` |
| Functions | <style> | `<example>()` |
| Classes | <style> | `<Example>` |
```

### Detection heuristics

| Pattern category | Detection method |
|-----------------|------------------|
| Error handling | Count throw vs return patterns; detect `Result`, `Either`, `{ data, error }` tuples |
| Async flow | Detect async/await, Promise chains, callbacks, event emitters, state machines |
| Module structure | Read barrel files (index.ts/__init__.py/mod.rs); detect import style |
| State management | Detect React hooks, stores, actors, global `extern` variables |
| Naming conventions | Sample 20+ file/fn/type names from each layer; detect dominant style |
| Component/data pattern | Detect `'use client'`, decorators, annotations, HOCs |
| Test pattern | Read a test file; detect framework + assertion style |

**After detecting patterns, present them to the user for approval.**

### Stack-specific patterns

| Stack | Always check |
|-------|-------------|
| React/Next.js | Components (`'use client'`, server vs client), hooks vs server actions |
| Vue/Nuxt | Composables, `<script setup>`, Pinia stores |
| Go | Error wrapping (`%w`), `database/sql` patterns, middleware chaining |
| Python | `async def` vs sync, pydantic models, FastAPI dependency injection |
| Rust | `Result<T, E>`, `?` operator, trait bounds, module visibility |
| C/C++ embedded | Global `extern` variables, SMF (switch/case state machines), PIO programs, static file-scope state, fixed-point arithmetic, `#define` constants |
| C/C++ embedded | Dual-core patterns (Core 0 vs Core 1 split, SPSC ring buffers, multicore FIFO) |
| C/C++ embedded | Interrupt model (polled vs IRQ-driven, PIO/DMA interrupt routing) |

---

## Symbol index format

Generated by `generate-symbol-index.py`. Stored at `docs/wiki/symbol-index.json`:

```json
{
  "generated": "YYYY-MM-DD",
  "language": "cpp",
  "count": NNN,
  "symbols": [
    { "name": "<ClassName>", "kind": "class", "file": "<path.h>", "line": N },
    { "name": "<functionName>", "kind": "function", "file": "<path.cpp>", "line": N },
    { "name": "<globalName>", "kind": "global", "file": "<path.h>", "line": N },
    { "name": "<MACRO_NAME>", "kind": "macro", "file": "<path.h>", "line": N }
  ]
}
```

### Symbol kinds detected

| Language | Symbol kinds |
|----------|-------------|
| C/C++ | `class`, `struct`, `enum`, `enum-value`, `function`, `global`, `extern`, `macro`, `namespace` |
| TypeScript/JavaScript | `class`, `interface`, `type`, `enum`, `function`, `const`, `let`, `export`, `component` |
| Python | `class`, `function` |
| Go | `struct`, `interface`, `function`, `var`, `const`, `type` |
| Rust | `struct`, `enum`, `fn`, `trait`, `impl`, `const`, `static`, `macro`, `type` |

---

## Domain detection heuristics

1. **Directory clusters** — domain-named subdirectories (strongest signal).
2. **Import communities** — find groups of files that import each other heavily.
3. **Co-location** — files with similar naming in the same directory.
4. **Barrel exports** — files re-exported from the same `index.ts` / `__init__.py` / `mod.rs`.
5. **Config-defined modules** — monorepo packages, workspace members.

Rule of thumb: a domain should cover 2-20 source files.

---

## File scope defaults

| Language | Default include | Default exclude |
|----------|----------------|-----------------|
| TypeScript/JavaScript | `src/**/*.{ts,tsx,js,jsx}` | `**/*.test.*`, `**/__tests__/**`, `**/*.d.ts`, `**/*.stories.*` |
| Python | `**/*.py` | `**/test_*.py`, `**/tests/**`, `**/conftest.py` |
| Go | `**/*.go` | `**/*_test.go` |
| Rust | `src/**/*.rs` | — |
| C/C++ | `src/**/*.{cpp,h,hpp,c}`, `appSrc/**/*.{cpp,h,hpp,c}` | `**/*test*`, `**/build/**`, `**/*.pio.h` |
| Generic | `src/**/*` | `**/test*/**`, `**/dist/**`, `**/build/**` |

Always exclude `node_modules/`, `.git/`, `vendor/`, `target/`, `__pycache__/`, `.venv/`.

---

## README.md template

```markdown
# Codebase Wiki

This wiki provides an AI-optimised map of the codebase: architecture, patterns, state machines, tests, and a machine-readable symbol index.

## For humans

1. `_quickref.md` — keep this open while coding
2. `_index.md` — full architecture overview in 5-10 minutes
3. `_rules.md` — what you must never do
4. `_practices.md` — how to write maintainable new code
5. `_patterns.md` — how code is written here
6. `_lifecycle.md` — how code runs here
6. `_deps.md` — who depends on whom
7. `_tests.md` — what's tested, what's not
8. `features/<domain>.md` — deep dive into any module

## For AI agents — decision tree

**Before making ANY change**, follow this protocol:

### I need to add a feature or modify behavior
1. Read `_index.md` → find the domain(s) involved
2. Read `_rules.md` → know what not to break
3. Read `_practices.md` → write maintainable code, not just working code
4. Read the relevant `features/<domain>.md` (architecture, key functions, edge cases)
4. Search `symbol-index.json` for the symbols you need
5. Read `_patterns.md` — match existing conventions
6. Check `_deps.md` — identify the blast radius
7. Check `_tests.md` — run the per-domain tests after your change

### I need to debug a problem
1. Read `_lifecycle.md` → find the state machine or lifecycle path
2. Search `symbol-index.json` for the symbols involved
3. Read the relevant domain docs for edge cases
4. Check `_deps.md` — the bug might be in a dependency
5. Check `_rules.md` — make sure you're not triggering a violation

### I need to refactor
1. Read `_deps.md` — identify high-risk modules and solitary modules
2. Read `_tests.md` — untested domains are dangerous to refactor
3. Read domain docs for the target module AND "Consumed by" modules
4. After refactoring, run `refresh symbol-index`

### I'm reading unfamiliar code
1. Search `symbol-index.json` for the file name → see all symbols defined there
2. Check `_index.md` → which domain owns this file?
3. Read the domain doc → what does this module do?

### Using `symbol-index.json`
Search it with any JSON tool or grep:
- Find a symbol: `rg '"<symbol>"' docs/wiki/symbol-index.json -A 3`
- List symbols in a file: `rg '"<file-path>"' docs/wiki/symbol-index.json -A 3`
- Count by kind: `rg '"kind"' docs/wiki/symbol-index.json | sort | uniq -c`

## Commands

- `make wiki` — initialize docs/wiki/
- `refresh symbol-index` — regenerate symbol-index.json
- `refresh patterns` — propose updated _patterns.md
- `refresh lifecycle` — propose updated _lifecycle.md
- `refresh rules` — propose updated _rules.md
- `refresh practices` — propose updated _practices.md

## If a domain doc seems stale
Read the source files listed in the doc's "Source" header. If the doc is wrong, propose an update. Don't silently ignore stale docs.

## Plans directory
`docs/wiki/plans/` holds architecture proposals and migration plans. Each plan is a standalone markdown file indexed by `plans/README.md`. Plans justify *decisions*, unlike domain docs which describe *facts*.
```

---

## Edge cases

### New project (no docs)
`make wiki` builds everything from scratch. Existing README.md is linked, not duplicated.

### Project with existing docs folder
`make wiki` detects existing `docs/` content, links it from `_index.md`, excludes those modules so the wiki fills gaps instead of competing.

### File moved / deleted
The symbol index is always regenerated from current source, so moves and deletions are reflected on the next `refresh symbol-index`.

### Large refactor
Re-run `make wiki` fresh if the domain structure itself changed, or `refresh symbol-index` if just adding/removing definitions.

### Monorepo
Detect workspace configs. Each workspace member gets its own `docs/wiki/<member>/` with independent wiki. The root gets a meta `_index.md` linking to all members.
