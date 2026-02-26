# Agent Ledger Contract (QEFC)

## Purpose
This ledger is the single source of truth for multi-agent coordination.  
All agents must communicate through TASKBOARD + per-task ledgers.

## Non-Negotiables
1) No agent may run `git push` or merge branches. Human (Chief Architect) does commit/push/merge.
2) All work must map to a TASK-ID (QEFC-###). No “silent changes”.
3) Every task must have:
   - owner agent
   - scope (files)
   - acceptance criteria
   - validation commands
4) Minimal diffs: avoid refactors unless required by acceptance criteria.
5) Doctrine-first: if conflict arises, pause and escalate via DECISIONS entry (no improvisation).

## Task Lifecycle
- NEW → PLANNED → IN_PROGRESS → REVIEW → READY_TO_COMMIT → DONE
- If blocked: set status = BLOCKED and describe cause + next action.

## Update Rules
- TASKBOARD is updated only by Orchestrator agent (or Human).
- Each task ledger (`tasks/QEFC-###.md`) contains:
  - Handoff packets
  - Implementation updates
  - Review notes
  - Final “Ready-to-Commit” gate statement

## Required Output Format (Agents)
Every agent update must end with:
- Files touched (exact paths)
- Summary of changes
- Risks / open questions
- Validation commands (ruff/mypy/pytest etc.)