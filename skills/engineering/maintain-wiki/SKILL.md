---
name: maintain-wiki
description: Create and maintain a codebase wiki at docs/wiki/ for AI navigation. Generates spatial map, dependency graph, coding standards, test inventory, state/lifecycle docs, and a machine-readable symbol index. Use when user says "make wiki", "refresh symbol-index", or when docs/wiki/ already exists and code changes have been made.
---

# Maintain Wiki

Codebase wiki at `docs/wiki/`. AI-optimized: spatial map, dependency graph, coding standards, test inventory, state machines, symbol index.

See [REFERENCE.md](REFERENCE.md) for templates and detection heuristics.

## Quick start

```
"make wiki"           → initialize docs/wiki/ (interactive: domains + standards + lifecycle)
"refresh symbol-index" → regenerate symbol-index.json from source
"refresh standards"    → re-scan, propose updated _standards.md
"refresh lifecycle"    → re-scan, propose updated _lifecycle.md
```

## File inventory

| File | Kind | Updated by |
|------|------|-----------|
| `_index.md` | Quickref + architecture | `make wiki` (auto) |
| `_deps.md` | Dependency map | `make wiki` (auto) |
| `_standards.md` | Rules + practices + patterns | `make wiki` (interactive), `refresh standards` |
| `_tests.md` | Test inventory | `make wiki` (auto) |
| `_lifecycle.md` | State machines + errors | `make wiki` (interactive), `refresh lifecycle` |
| `symbol-index.json` | Symbol → file:line map | `make wiki`, `refresh symbol-index` |
| `features/*.md` | Domain docs | `make wiki` |
| `plans/` | Architecture proposals | manual |
| `README.md` | Usage instructions | `make wiki` only |

`_index.md` has a quick reference section at the top (build, flash, test commands, key files, domain one-liners), then full architecture below. One file to open, two purposes.

`_standards.md` has three sections: `## Rules` (what you MUST not do — catastrophic failures), `## Practices` (how you SHOULD write new code — engineering standards), `## Patterns` (how code IS written — detected conventions). One file covers all coding guidance.

## Workflow: make wiki

1. Detect tech stack (CMakeLists.txt, Cargo.toml, package.json, etc.).
2. Read existing docs (README, CONTEXT, AGENTS.md) — link, don't duplicate.
3. **Domain detection**: scan imports + directory clusters → propose groupings (2–20 files per domain) → **ask user to approve**.
4. **Standards detection**: detect rules (scan for BR_PANIC, assert, guards in existing docs), detect patterns (error handling, naming, module structure), load practices from stack defaults. Present all three as a single `_standards.md` proposal → **ask user to approve**.
5. **Lifecycle detection**: scan entry points, state machines, error recovery → propose → **ask user to approve**.
6. Ask scope (source files matching language, exclude tests/generated).
7. Create `docs/wiki/`:
   - `_index.md` — quickref block at top (build/flash/test commands, key files, domain one-liners, top symbols), then architecture topology + entry points + "change X → look at Y" table
   - `_deps.md` — dependency graph + high-risk modules + per-module verify commands
   - `_standards.md` — `## Rules` (DON'T) + `## Practices` (SHOULD) + `## Patterns` (TYPICALLY)
   - `_tests.md` — per-domain run commands, coverage table, gaps
   - `_lifecycle.md` — state machines + error recovery table
   - `symbol-index.json` — every symbol → file:line
   - `README.md` — agent decision tree + human reading guide
   - Domain docs (`features/*.md`) — one per domain
   - `plans/` directory — empty
8. Add `## Codebase Wiki` section to AGENTS.md.

## Workflow: refresh symbol-index

1. Scan source files in scope for classes, functions, enums, globals, externs, macros.
2. Write `docs/wiki/symbol-index.json`.
3. Report symbol count.

## Workflow: refresh standards

Re-scan codebase + AGENTS.md for new rules, patterns, or practice gaps. Propose updated `_standards.md`. User approves. Never auto-write.

## Workflow: refresh lifecycle

Re-scan for new state machines or error recovery paths. Propose updated `_lifecycle.md`. User approves. Never auto-write.

## Symbol index usage

```bash
rg '"<symbol>"' docs/wiki/symbol-index.json -A 3     # find symbol definition
rg '"<file-path>"' docs/wiki/symbol-index.json -A 3  # all symbols in a file
rg '"kind"' docs/wiki/symbol-index.json | sort | uniq -c  # kind breakdown
```

Faster than full-tree grep. Returns precise file:line.

## Proactive suggestion

After code changes, run `refresh symbol-index`. Check if `_standards.md`, `_lifecycle.md`, `_deps.md`, or domain docs need updating. Flag stale docs — don't silently ignore.
