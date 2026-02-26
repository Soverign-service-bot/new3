import re
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER_DIR = ROOT / "docs" / "agent-ledger"
TASKS_DIR = LEDGER_DIR / "tasks"
TASKBOARD = LEDGER_DIR / "TASKBOARD.md"
DECISIONS = LEDGER_DIR / "DECISIONS.md"
TEMPLATE = TASKS_DIR / "TEMPLATE.md"


def ensure_bootstrap():
    LEDGER_DIR.mkdir(parents=True, exist_ok=True)
    TASKS_DIR.mkdir(parents=True, exist_ok=True)

    if not TASKBOARD.exists():
        TASKBOARD.write_text(
            "# TASKBOARD (QEFC)\n\n"
            "> Contract: See `docs/agent-ledger/CONTRACT.md`\n\n"
            "## Status Legend\n"
            "NEW | PLANNED | IN_PROGRESS | REVIEW | READY_TO_COMMIT | DONE | BLOCKED\n\n"
            "## Active Tasks\n"
            "| ID | Title | Status | Owner | Priority | Branch | Ledger | Created | Updated |\n"
            "|---|---|---|---|---|---|---|---|---|\n",
            encoding="utf-8",
        )

    if not DECISIONS.exists():
        DECISIONS.write_text(
            "# DECISIONS (QEFC)\n\n"
            "Decisions are recorded here to prevent doctrine drift and repeated debates.\n\n"
            "## Decision Log\n",
            encoding="utf-8",
        )

    if not TEMPLATE.exists():
        TEMPLATE.write_text(
            "# QEFC-XXX — <TITLE>\n\n"
            "## Meta\n"
            "- Status: NEW\n"
            "- Owner:\n"
            "- Priority: P2\n"
            "- Branch: bot/QEFC-XXX-<slug>\n"
            "- Scope (files):\n"
            "- Acceptance Criteria:\n"
            "- Validation Commands:\n"
            "  - ruff check .\n"
            "  - ruff format .\n"
            "  - mypy .\n"
            "  - pytest -q\n\n"
            "---\n\n"
            "## Handoff Packets\n\n"
            "### Handoff 1 — <From> → <To>\n"
            "**Goal**\n- ...\n\n"
            "**Proposed Changes**\n- ...\n\n"
            "**Risks / Open Questions**\n- ...\n\n"
            "**Acceptance Criteria**\n- ...\n\n"
            "---\n\n"
            "## Implementation Updates\n- (timestamp) ...\n\n"
            "## Review Notes\n- (timestamp) ...\n\n"
            "## Final Gate\n"
            "**Ready-to-Commit Statement**\n"
            "- [ ] Criteria met\n"
            "- [ ] Checks green locally\n"
            "- [ ] Minimal diff verified\n",
            encoding="utf-8",
        )


def next_task_id() -> str:
    pattern = re.compile(r"\bQEFC-(\d{3})\b")
    max_id = 0
    if TASKBOARD.exists():
        text = TASKBOARD.read_text(encoding="utf-8")
        for m in pattern.finditer(text):
            max_id = max(max_id, int(m.group(1)))
    # also scan tasks folder filenames
    for p in TASKS_DIR.glob("QEFC-*.md"):
        match = re.search(r"QEFC-(\d{3})", p.name)
        if match:
            max_id = max(max_id, int(match.group(1)))
    return f"QEFC-{max_id + 1:03d}"


def slugify(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-{2,}", "-", s).strip("-")
    return s[:48] if s else "task"


def insert_taskboard_row(task_id: str, title: str, owner: str, priority: str, branch: str, ledger_rel: str):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    row = f"| {task_id} | {title} | NEW | {owner} | {priority} | {branch} | {ledger_rel} | {now} | {now} |\n"

    tb = TASKBOARD.read_text(encoding="utf-8").splitlines(True)

    # Insert after header separator line of Active Tasks table
    # find the second table line (the separator)
    insert_idx = None
    for i, line in enumerate(tb):
        if line.startswith("| ID | Title |"):
            # next line is separator; insert after that
            insert_idx = i + 2
            break
    if insert_idx is None:
        # fallback append
        tb.append("\n## Active Tasks\n")
        tb.append("| ID | Title | Status | Owner | Priority | Branch | Ledger | Created | Updated |\n")
        tb.append("|---|---|---|---|---|---|---|---|---|\n")
        insert_idx = len(tb)

    tb.insert(insert_idx, row)
    TASKBOARD.write_text("".join(tb), encoding="utf-8")


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("title", help="Task title")
    parser.add_argument("--owner", default="Orchestrator", help="Owner agent name")
    parser.add_argument("--priority", default="P2", help="P0/P1/P2/P3")
    args = parser.parse_args()

    ensure_bootstrap()

    task_id = next_task_id()
    slug = slugify(args.title)
    branch = f"bot/{task_id}-{slug}"
    ledger_file = TASKS_DIR / f"{task_id}.md"
    ledger_rel = f"docs/agent-ledger/tasks/{task_id}.md"

    template = TEMPLATE.read_text(encoding="utf-8")
    content = template.replace("QEFC-XXX", task_id).replace("<TITLE>", args.title).replace("<slug>", slug)
    content = content.replace("Owner:\n", f"Owner: {args.owner}\n").replace(
        "Priority: P2", f"Priority: {args.priority}"
    )
    content = content.replace("Branch: bot/QEFC-XXX-<slug>", f"Branch: {branch}")

    ledger_file.write_text(content, encoding="utf-8")
    insert_taskboard_row(task_id, args.title, args.owner, args.priority, branch, ledger_rel)

    print(f"Created {task_id}")
    print(f"- Ledger: {ledger_rel}")
    print(f"- Suggested branch: {branch}")


if __name__ == "__main__":
    main()
