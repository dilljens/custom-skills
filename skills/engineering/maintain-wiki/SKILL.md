---
name: maintain-wiki
description: Create and maintain a codebase wiki at docs/wiki/ keyed to git blob hashes so docs stay current. Generates spatial map, dependency map, code archeology (patterns), test inventory, and state/lifecycle docs. Use when user says "make wiki", "update wiki", "wiki status", or when docs/wiki/ already exists and code changes have been made.
---

# Maintain Wiki

Manages a hash-keyed codebase wiki at `docs/wiki/` that stays in sync with source via git blob hashes. Beyond domain docs, it generates AI-optimized meta files: spatial map, dependency graph, code patterns, test inventory, and state/lifecycle map.

See [REFERENCE.md](REFERENCE.md) for manifests, templates, and detection heuristics.

## Quick start

```
"make wiki"   → initialize docs/wiki/ (interactive: domains + patterns + lifecycle)
"update wiki" → diff hashes, surgically update domain docs, refresh _tests.md + _deps.md
"wiki status" → read-only report of staleness
```

## File inventory

| File | Kind | Updated by | Hash-tracked |
|------|------|-----------|-------------|
| `_index.md` | Spatial map | `make wiki`, `update wiki` | Yes (manifest) |
| `_deps.md` | Dependency map | `make wiki`, `update wiki` | Auto (import scan) |
| `_patterns.md` | Code archeology | `make wiki` (interactive) | No (editorial) |
| `_tests.md` | Test inventory | `make wiki`, `update wiki` | Auto (file scan) |
| `_lifecycle.md` | State machine | `make wiki` (interactive) | No (editorial) |
| `_hashes.json` | Manifest | All workflows | N/A (source of truth) |
| `features/*.md` | Domain docs | `update wiki` | Yes (per-file) |
| `README.md` | Wiki instructions | `make wiki` only | No |

## Workflow: make wiki

1. Detect tech stack from config files (`package.json`, `Cargo.toml`, etc.).
2. Read existing docs (README, CONTEXT, ARCHITECTURE, AGENTS.md) — link from wiki, don't duplicate.
3. **Domain detection**: scan imports + directory clusters → propose groupings → **ask user to approve**. Rule: 2–20 files per domain.
4. **Pattern detection**: scan source for error handling, async flow, module structure, state management, naming conventions. Read AGENTS.md for stated conventions. Propose 5–10 patterns → **ask user to approve**.
5. **Lifecycle detection**: scan entry points, state enums/transitions, middleware chains, realtime subscriptions. Propose a state flow diagram → **ask user to approve**.
6. Ask scope (default: source files matching language, excluding tests/generated code).
7. Create `docs/wiki/`:
   - `_index.md` — entry points, ASCII topology, "change X → look at Y" table, domain TOC
   - `_hashes.json` — file→domain→hash manifest
   - `_deps.md` — dependency graph from import analysis
   - `_patterns.md` — how code is written here (stack-specific templates in REFERENCE.md)
   - `_tests.md` — test file→domain mapping, test commands, coverage gaps
   - `_lifecycle.md` — runtime state machine (stack-specific templates in REFERENCE.md)
   - `README.md` — instructions for humans and agents
   - Create domain docs (`features/*.md`) for each approved domain now — one doc per domain covering its files, purpose, and key exports
8. Add the ## Codebase Wiki section to AGENTS.md.

## Workflow: update wiki

1. Diff git blob hashes against `_hashes.json` → categorize: stale, undocumented, orphaned, new.
2. **Present summary to user** before modifying anything.
3. For each stale domain: `git diff HEAD~1..HEAD -- <files>`, read existing doc, surgically rewrite only affected sections.
4. Create domain docs for undocumented files (after user assigns them to a domain).
5. Regenerate `_index.md` from manifest + source scan.
6. Regenerate `_deps.md` from import analysis.
7. Regenerate `_tests.md` from file scan.
8. Update all changed hashes in `_hashes.json`.
9. Run `wiki status` to confirm zero staleness.
10. **If `_patterns.md` or `_lifecycle.md` may be stale** (new files, refactored structure), suggest refreshing them. Never auto-update these — they're editorial.

## Workflow: wiki status

Read-only hash diff. Print report:

```
Wiki status:
  Stale:           3 docs (features/task-system, ...)
  Undocumented:    2 files (src/lib/newFeature.ts, ...)
  Orphaned:        1 file
  Up to date:      47 files
```

## Proactive suggestion

After making code changes, if `docs/wiki/_hashes.json` exists, silently check for staleness. If anything is stale/undocumented: "5 wiki docs may be stale after these changes. Run `update wiki` to refresh them?"

## Updating editorial meta files

```
"refresh patterns"    → re-scan codebase, propose updated _patterns.md
"refresh lifecycle"   → re-scan state machines, propose updated _lifecycle.md
```
