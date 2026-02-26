# QEFC Agent Ledger — Quickstart Guide

Welcome to the Sovereign-Quant (QEFC) multi-agent coordination system. This guide will help you create tasks, track work, and collaborate using the ledger system.

---

## 1. Ledger System Overview

The **Agent Ledger** is the single source of truth for multi-agent coordination in the QEFC repository.

### Key Files
- **`CONTRACT.md`** — Core rules and non-negotiables for all agents
- **`TASKBOARD.md`** — Active tasks with status, owner, priority, and branch info
- **`DECISIONS.md`** — Architectural decisions to prevent drift and repeated debates
- **`tasks/QEFC-###.md`** — Per-task ledgers with handoff packets, implementation updates, and reviews

### Purpose
- **Coordination**: All agents communicate through TASKBOARD + per-task ledgers
- **Traceability**: Every change maps to a TASK-ID (QEFC-###)
- **Accountability**: Clear ownership, scope, and acceptance criteria for each task
- **Quality**: Validation commands and review gates ensure minimal diffs and doctrine compliance

---

## 2. Creating Tasks

### Method 1: Command Line (CLI)

Run the task creation script directly:

```bash
python scripts/new_task.py "<task title>" --owner <agent-name> --priority <P0-P3>
```

**Example:**
```bash
python scripts/new_task.py "Add QLF indicator module" --owner Quant-Engineer --priority P1
```

**Output:**
```
Created QEFC-003
- Ledger: docs/agent-ledger/tasks/QEFC-003.md
- Suggested branch: bot/QEFC-003-add-qlf-indicator-module
```

### Method 2: VS Code Task (Recommended)

Use the integrated VS Code task for a streamlined workflow:

1. **Open Command Palette**: `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (Mac)
2. **Run Task**: Type `Tasks: Run Task` and select **"Create QEFC Task"**
3. **Fill Prompts**:
   - **Task Title**: Enter descriptive title (e.g., "Add backtesting engine")
   - **Task Owner**: Select agent (default: Quant-Engineer)
   - **Task Priority**: Select P0-P3 (default: P2)
4. **Result**: Task created, ledger file generated, TASKBOARD updated

**Priority Levels:**
- **P0**: Critical / blocking
- **P1**: High priority
- **P2**: Normal priority (default)
- **P3**: Low priority / nice-to-have

---

## 3. Task Lifecycle

### States
```
NEW → PLANNED → IN_PROGRESS → REVIEW → READY_TO_COMMIT → DONE
                                  ↓
                              BLOCKED
```

| State | Meaning |
|-------|---------|
| **NEW** | Task created, awaiting planning |
| **PLANNED** | Scoped and ready for implementation |
| **IN_PROGRESS** | Agent actively working on task |
| **REVIEW** | Implementation complete, awaiting review |
| **READY_TO_COMMIT** | Reviewed and approved, ready for Human merge |
| **DONE** | Committed to main/dev by Human Chief Architect |
| **BLOCKED** | Cannot proceed, needs intervention |

### Update Rules
- **TASKBOARD**: Only **Orchestrator** (or Human) updates status/metadata
- **Task Ledgers**: Assigned agent updates with implementation notes
- **Handoff Packets**: Document scope, constraints, acceptance criteria
- **Review Notes**: Reviewer appends findings and decision (APPROVED / CHANGES_REQUESTED / BLOCKED)

---

## 4. Working with Tasks

### Reading TASKBOARD

Open `docs/agent-ledger/TASKBOARD.md` to see all active tasks:

```markdown
| ID | Title | Status | Owner | Priority | Branch | Ledger | Created | Updated |
|----|-------|--------|-------|----------|--------|--------|---------|---------|
| QEFC-001 | Bootstrap ledger | READY_TO_COMMIT | Quant-Engineer | P1 | bot/QEFC-001-... | tasks/QEFC-001.md | ... | ... |
```

**Find your work:**
- Filter by **Owner** (your agent name)
- Check **Status** (IN_PROGRESS tasks are active)
- Note **Branch** name for git operations

### Navigating to Task Ledgers

1. Open `docs/agent-ledger/TASKBOARD.md`
2. Find your task (e.g., QEFC-003)
3. Click the **Ledger** link (e.g., `tasks/QEFC-003.md`)
4. Read the **Handoff Packet** for scope and requirements

### Documenting Work

#### Implementation Updates
After completing work, append to the task ledger:

```markdown
## Implementation Updates

### 2026-02-26 14:30 — Quant-Engineer
**Files Touched:**
- `core/indicators.py` (added QLF indicator logic)
- `tests/test_indicators.py` (added 5 test cases)

**Change Summary:**
- Implemented QLF indicator with deterministic output
- All tests pass, ruff/mypy clean

**Validation Results:**
```bash
$ ruff check .
All checks passed!
$ mypy .
Success: no issues found
$ pytest -q
32 passed
```

**Risks / Open Questions:**
- None identified

**Minimal Diff Verified:**
✅ Only 2 files modified (core + tests)
```

#### Ready-to-Commit Gate
Mark completion in the **Final Gate** section:

```markdown
## Final Gate
**Ready-to-Commit Statement**
- [x] Criteria met — All acceptance criteria satisfied
- [x] Checks green locally — ruff ✓, mypy ✓, pytest ✓
- [x] Minimal diff verified — Only 2 files

**Status:** READY_FOR_REVIEW: QEFC-003
```

---

## 5. Agent Roles

### Orchestrator
- **Responsibilities**: Create tasks, coordinate work, update TASKBOARD
- **Authority**: Task creation, handoff packets, status updates
- **Constraints**: No direct code implementation

### Quant-Engineer
- **Responsibilities**: Implement features, write tests, validate code quality
- **Authority**: Code changes in feature branches
- **Constraints**: No git push/merge, no architecture decisions

### Reviewer-CI
- **Responsibilities**: Review changes, verify acceptance criteria, approve/reject
- **Authority**: Review notes, READY_TO_COMMIT decisions
- **Constraints**: No code implementation, no TASKBOARD edits (except status updates)

### Chief Architect (Human)
- **Responsibilities**: Final authority on merges, architecture decisions
- **Authority**: Git push/merge to main/dev, doctrine changes
- **Constraints**: None (final authority)

---

## 6. Troubleshooting

### Issue: Task creation fails with "No module named 'scripts'"
**Solution**: Ensure you're in the repository root:
```bash
cd c:\SovereignQuant\qefc-sov-quant
python scripts/new_task.py "My Task" --owner Quant-Engineer --priority P2
```

### Issue: VS Code task doesn't appear
**Solution**: 
1. Reload VS Code window (`Ctrl+Shift+P` → "Reload Window")
2. Verify `.vscode/tasks.json` exists
3. Check for JSON syntax errors in tasks.json

### Issue: Task ledger not opening after creation
**Solution**: 
- CLI: Manually open `docs/agent-ledger/tasks/QEFC-###.md`
- VS Code task: File should open automatically; if not, navigate manually

### Issue: TASKBOARD shows wrong status
**Solution**: 
- Only Orchestrator should update TASKBOARD
- If incorrect, ask Orchestrator to correct the status
- Never edit TASKBOARD directly unless you are Orchestrator

### Issue: Validation commands fail (ruff/mypy/pytest)
**Solution**:
1. Install dependencies: `pip install -r requirements.txt`
2. Check Python version: `python --version` (requires ≥3.11)
3. Run commands individually to isolate issue:
   ```bash
   ruff check .
   mypy .
   pytest -q
   ```

---

## 7. Quick Reference

### Task Creation
```bash
# CLI
python scripts/new_task.py "<title>" --owner <agent> --priority <P0-P3>

# VS Code
Ctrl+Shift+P → Tasks: Run Task → Create QEFC Task
```

### Validation Commands
```bash
ruff check .           # Lint
ruff format .          # Format
mypy .                 # Type check
pytest -q              # Tests
```

### Key Locations
- **TASKBOARD**: `docs/agent-ledger/TASKBOARD.md`
- **Task Ledgers**: `docs/agent-ledger/tasks/QEFC-###.md`
- **Contract**: `docs/agent-ledger/CONTRACT.md`
- **Decisions**: `docs/agent-ledger/DECISIONS.md`

### Next Steps
1. Review [CONTRACT.md](CONTRACT.md) for non-negotiables
2. Check [TASKBOARD.md](TASKBOARD.md) for your assigned tasks
3. Open task ledger and read Handoff Packet
4. Implement, validate, document
5. Mark READY_FOR_REVIEW and notify Reviewer

---

**Need Help?** Escalate via DECISIONS.md or ask Orchestrator for clarification.

**Ready to start?** Create your first task using Method 2 (VS Code Task) above! 🚀
