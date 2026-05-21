---
name: maintain-wiki
description: Create and maintain a codebase wiki at docs/wiki/ for AI navigation. Generates spatial map, dependency graph, code patterns, test inventory, state/lifecycle docs, and a machine-readable symbol index. Use when user says "make wiki", "refresh symbol-index", or when docs/wiki/ already exists and code changes have been made.
---

# Maintain Wiki

Manages a codebase wiki at `docs/wiki/` for AI navigation. Generates AI-optimized meta files: spatial map, dependency graph, code patterns, test inventory, state/lifecycle map, and a machine-readable **symbol index** that agents can use to jump directly to definitions.

See [REFERENCE.md](REFERENCE.md) for templates and detection heuristics.

## Quick start

```
"make wiki"          → initialize docs/wiki/ (interactive: domains + rules + patterns + lifecycle)
"refresh symbol-index" → re-scan source, regenerate symbol-index.json
"refresh patterns"   → re-scan codebase, propose updated _patterns.md
"refresh lifecycle"  → re-scan state machines, propose updated _lifecycle.md
"refresh rules"      → re-scan for coding commandments, propose updated _rules.md
"refresh practices"  → propose updated _practices.md based on language/framework
```

## File inventory

| File | Kind | Updated by |
|------|------|-----------|
| `_quickref.md` | One-page cheat sheet | `make wiki` (auto) |
| `_index.md` | Spatial map | `make wiki` (auto) |
| `_deps.md` | Dependency map | `make wiki` (auto) |
| `_rules.md` | Coding commandments | `make wiki` (interactive) |
| `_practices.md` | Engineering standards | `make wiki` (standards-based) |
| `_patterns.md` | Code archeology | `make wiki` (interactive), `refresh patterns` |
| `_tests.md` | Test inventory + per-domain run commands | `make wiki` (auto) |
| `_lifecycle.md` | State machines + error recovery | `make wiki` (interactive), `refresh lifecycle` |
| `symbol-index.json` | Machine-readable symbol map | `make wiki`, `refresh symbol-index` |
| `features/*.md` | Domain docs | `make wiki` |
| `plans/` | Architecture proposals & migration plans | manual |
| `README.md` | Wiki instructions | `make wiki` only |

The `plans/` directory is optional — created when users generate architecture proposals or migration plans. Plans are long-form docs that justify decisions, not living documentation. Each plan gets its own markdown file with a `README.md` index.

## How to use the symbol index

When looking up a symbol, search `docs/wiki/symbol-index.json` with a simple filter:

```
# Find all symbols matching "processState"
rg '"processState"' docs/wiki/symbol-index.json -A 3

# Find all BusHandle methods
rg '"name": ".*BusHandle.*"' docs/wiki/symbol-index.json

# Find all globals defined in Sys.h
rg '"file": "appSrc/system/Sys.h"' docs/wiki/symbol-index.json
```

This is faster than grepping the entire source tree and returns precise file:line locations. Use it before reading any file you're unfamiliar with — it tells you exactly where to look.

## Workflow: make wiki

1. Detect tech stack from config files (`CMakeLists.txt`, `Cargo.toml`, `package.json`, etc.).
2. Read existing docs (README, CONTEXT, ARCHITECTURE, AGENTS.md) — link from wiki, don't duplicate.
3. **Domain detection**: scan imports + directory clusters → propose groupings → **ask user to approve**. Rule: 2–20 files per domain.
4. **Rules detection**: scan AGENTS.md and existing docs for explicit "don't do X" statements. Scan source for patterns that would be catastrophic if broken (duplicate error handlers, missing guards, hard-coded timeouts). Propose 5–10 coding commandments → **ask user to approve**.
5. **Pattern detection**: scan source for error handling, async flow, module structure, state management, naming conventions. Read AGENTS.md for stated conventions. Propose 5–10 patterns → **ask user to approve**.
6. **Lifecycle detection**: scan entry points, state enums/transitions, error recovery paths, middleware chains. Propose state flow + error recovery diagrams → **ask user to approve**.
7. Ask scope (default: source files matching language, excluding tests/generated code).
8. Create `docs/wiki/`:
   - `_quickref.md` — single page with build, flash, test commands; top 15 most-defined symbols; one-sentence domain descriptions
   - `_index.md` — entry points, ASCII topology, "change X → look at Y" table, domain TOC
   - `_deps.md` — dependency graph from import analysis, per-module verify commands
   - `_rules.md` — coding commandments: what you must NEVER do
   - `_practices.md` — engineering standards: how to write maintainable new code (see REFERENCE.md for stack-specific defaults)
   - `_patterns.md` — how code is written here (stack-specific templates in REFERENCE.md)
   - `_tests.md` — test file→domain mapping, exact run commands per domain, coverage gaps
   - `_lifecycle.md` — runtime state machine diagrams + error recovery paths
   - `symbol-index.json` — machine-readable map of all symbols → file:line
   - `README.md` — instructions for humans and agents
   - Domain docs (`features/*.md`) — one per domain covering files, purpose, key exports, invariants
   - `plans/` directory — empty, ready for architecture proposals
9. Add the `## Codebase Wiki` section to AGENTS.md.

## Workflow: refresh symbol-index

1. Scan every source file in scope for classes, functions, methods, enums, global variables, `extern` declarations, and macros.
2. Map each symbol to its file path and line number.
3. Write `docs/wiki/symbol-index.json` as a JSON array of `{name, kind, file, line, ...}` objects.
4. Report count of indexed symbols.

## Workflow: refresh patterns

Re-scan the codebase and propose an updated `_patterns.md`. Same heuristic as `make wiki` step 4 — detect error handling, async flow, naming conventions, etc. Present proposed changes for user approval. Never auto-write.

## Workflow: refresh lifecycle

Re-scan the codebase and propose an updated `_lifecycle.md`. Same heuristic as `make wiki` step 6 — detect entry points, state machines, error recovery paths. Present proposed changes for user approval. Never auto-write.

## Workflow: refresh rules

Re-scan the codebase and AGENTS.md / README / CONTEXT for coding commandments. Propose additions or removals to `_rules.md`. Rules are high-importance: they prevent catastrophic bugs, not stylistic preferences. Present for user approval. Never auto-write.

## Workflow: refresh practices

Re-scan the codebase and propose additions to `_practices.md` based on new patterns observed in the source (e.g., if the project has started using a new framework, add framework-specific practices). Start from the stack-specific practice defaults in REFERENCE.md. Practices are aspirational — they set the bar for new code, not document existing code. Present additions for user approval. Never auto-write without approval.

## Proactive suggestion

After making code changes, run `refresh symbol-index` to keep the index current. Then check:

1. Did you add/remove any public API? → the relevant domain doc may need updating
2. Did you change any state machine or lifecycle path? → `_lifecycle.md` may need updating
3. Did you introduce a new pattern or convention? → `_patterns.md` may need updating
4. Did you add/remove dependencies? → `_deps.md` and domain doc "Dependencies" sections need updating
5. Did you write new code that should follow standards? → check `_practices.md` compliance

If a domain doc is clearly stale after your changes, propose an update to the user. Never silently let stale docs accumulate.

## Symbol index format

```json
{
  "generated": "2026-05-21",
  "language": "cpp",
  "count": 142,
  "symbols": [
    { "name": "BoardType", "kind": "enum", "file": "appSrc/include/ConfigTypes.h", "line": 10 },
    { "name": "LIDAR_NODE", "kind": "enum-value", "file": "appSrc/include/ConfigTypes.h", "line": 11 },
    { "name": "BusHandle", "kind": "class", "file": "appSrc/communication/BusHandle.h", "line": 27 },
    { "name": "processState", "kind": "method", "file": "appSrc/communication/BusHandle.cpp", "line": 150, "class": "BusHandle" },
    { "name": "board_state", "kind": "global", "file": "appSrc/system/Sys.h", "line": 25, "type": "BoardState" },
    { "name": "smfLidarScanHandler", "kind": "function", "file": "appSrc/core/Smf.cpp", "line": 532 },
    { "name": "MAX_BODY_LENGTH", "kind": "macro", "file": "appSrc/config/Global.h", "line": 23 },
    { "name": "cmfSendPacket", "kind": "function", "file": "appSrc/system/CommandFunctions.cpp", "line": 33 },
  ]
}
```

An agent can use this to instantly find where any symbol is defined, declared, or used — no grepping needed.
