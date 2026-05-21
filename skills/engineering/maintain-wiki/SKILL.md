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
"refresh symbols"      → regenerate _symbols.md from source
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
| `_symbols.md` | Symbol → domain lookup (lightweight) | `make wiki`, `refresh symbol-index` |
| `features/*.md` | Domain docs (with symbol tables inline) | `make wiki` |
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
   - `_symbols.md` — lightweight index: every symbol → domain + file:line (one-line entries, grep-friendly)
   - `README.md` — agent decision tree + human reading guide
   - Domain docs (`features/*.md`) — one per domain, each with inline symbol table
   - `plans/` directory — empty
8. Add `## Codebase Wiki` section to AGENTS.md.

## Workflow: refresh symbols

1. Scan source files in scope for classes, functions, enums, globals, externs, macros.
2. Map each symbol to its domain and file:line.
3. Write `docs/wiki/_symbols.md` — one line per symbol: `| <name> | <kind> | <domain> | <file>:<line> |`
4. Add or update the inline symbol table in each `features/<domain>.md` (the "Key functions / components" table).
5. Report count.

`_symbols.md` is a grep-friendly markdown table. Find any symbol: `rg 'BusHandle' docs/wiki/_symbols.md`. AI reads the domain column, then reads that domain doc for architecture and edge cases. No JSON parsing needed.

## Symbol lookup

```bash
rg '<symbol>' docs/wiki/_symbols.md       # find domain + file:line
rg 'communication' docs/wiki/_symbols.md  # all symbols in a domain
```

Domain docs also contain an inline symbol table (the "Key functions / components" section). When working in a domain, read the domain doc directly — it has symbols, architecture, data flow, and edge cases in one file.

## Proactive suggestion

After code changes, run `refresh symbols`. Check if `_standards.md`, `_lifecycle.md`, `_deps.md`, or domain docs need updating. Flag stale docs — don't silently ignore.
