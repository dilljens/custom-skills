---
name: maintain-wiki
description: Create and maintain a codebase wiki at docs/wiki/ for AI navigation. Generates spatial map, coding standards, and domain docs. Use when user says "make wiki" or when docs/wiki/ already exists and code changes have been made.
---

# Maintain Wiki

Codebase wiki at `docs/wiki/`. Three files: spatial map, coding standards, domain docs.

See [REFERENCE.md](REFERENCE.md) for templates and detection heuristics.

## Quick start

```
"make wiki"          → initialize docs/wiki/ (interactive: domains + standards)
```

## File inventory

| File | Kind | Updated by |
|------|------|-----------|
| `_index.md` | Quickref + architecture map | `make wiki` (auto) |
| `_standards.md` | Rules + practices + patterns | `make wiki` (interactive) |
| `features/*.md` | Domain docs | `make wiki` |
| `plans/` | Architecture proposals | manual |
| `README.md` | Usage instructions | `make wiki` only |

`_index.md` — quickref block at top (build/test commands, key files, domain one-liners), then architecture topology + entry points + "change X → look at Y" table.

`_standards.md` — three sections: `## Rules` (what you MUST not do — catastrophic), `## Practices` (how you SHOULD write new code), `## Patterns` (how code IS written — detected conventions).

`features/<domain>.md` — per-domain doc with architecture, data flow, edge cases, and key functions/components table.

## Workflow: make wiki

1. Detect tech stack from config files (Makefile, CMakeLists.txt, Cargo.toml, package.json, etc.).
2. Read existing docs (README, CONTEXT, AGENTS.md) — link from `_index.md`, don't duplicate content.
3. **Domain detection**: scan imports + directory clusters → propose groupings (2–20 files per domain) → **ask user to approve**.
4. **Standards detection**: detect rules (scan for assertions, panic macros, guard patterns, explicit rules in AGENTS.md/CONTEXT), detect patterns (error handling, naming, module structure conventions), load practices from stack defaults (see REFERENCE.md). Present all three as a single `_standards.md` proposal → **ask user to approve**.
5. Ask scope (source files matching language, exclude tests/generated/build artifacts).
6. Create `docs/wiki/`:
   - `_index.md` — quickref + architecture topology + "change X → look at Y"
   - `_standards.md` — `## Rules` + `## Practices` + `## Patterns`
   - `README.md` — agent decision tree + human reading guide
   - `features/*.md` — one per domain, each with architecture + key functions table
   - `plans/` — empty directory
7. Add `## Codebase Wiki` section to AGENTS.md.

## Proactive suggestion

After making code changes, if `docs/wiki/` exists, check whether any domain docs need updating (new files in a domain, architecture changes, new edge cases).
