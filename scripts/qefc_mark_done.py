#!/usr/bin/env python3
"""Mark a QEFC task as DONE after PR merge.

This script updates:
1. docs/agent-ledger/TASKBOARD.md - sets Status to DONE
2. docs/agent-ledger/tasks/QEFC-###.md - appends merge note

Idempotent: safe to re-run on already-DONE tasks.
"""

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path


def update_taskboard(task_id: str, merged_date: str) -> bool:
    """Update TASKBOARD.md to mark task as DONE.

    Args:
        task_id: Task ID (e.g., QEFC-007)
        merged_date: Merge date in YYYY-MM-DD format

    Returns:
        True if updated, False if task not found or already DONE
    """
    taskboard_path = Path("docs/agent-ledger/TASKBOARD.md")

    if not taskboard_path.exists():
        print(f"ERROR: TASKBOARD not found at {taskboard_path}", file=sys.stderr)
        return False

    content = taskboard_path.read_text(encoding="utf-8")

    # Find the task row with pattern: | QEFC-### | ... | STATUS | ...
    # Capture everything before and after the status column
    pattern = rf"(\| {re.escape(task_id)} \| [^|]+ \| )(\w+)( \|.+?\|)"
    match = re.search(pattern, content)

    if not match:
        print(f"WARNING: Task {task_id} not found in TASKBOARD. Skipping.")
        return False

    current_status = match.group(2)

    if current_status == "DONE":
        print(f"INFO: Task {task_id} already marked as DONE. Skipping TASKBOARD update.")
        return False

    # Replace status with DONE, update timestamp
    # Reconstruct the row with DONE status
    # Pattern: | ID | Title | STATUS | Owner | Priority | Branch | Ledger | Created | Updated |
    # We need to update STATUS (column 3) and Updated (column 9)

    # Split the line into columns
    row_parts = match.group(0).split("|")
    # Format: ['', ' QEFC-007 ', ' Title ', ' STATUS ', ' Owner ',
    #          ' Priority ', ' Branch ', ' Ledger ', ' Created ', ' Updated ', '']

    if len(row_parts) < 10:
        print(f"ERROR: Unexpected TASKBOARD row format for {task_id}", file=sys.stderr)
        return False

    # Update status (index 3) and updated timestamp (index 9)
    row_parts[3] = " DONE "
    row_parts[9] = f" {merged_date} 20:00 "  # Approximate time

    new_row = "|".join(row_parts)

    # Replace in content
    new_content = content.replace(match.group(0), new_row)
    taskboard_path.write_text(new_content, encoding="utf-8")

    print(f"✓ Updated TASKBOARD: {task_id} → DONE")
    return True


def append_merge_note(task_id: str, pr_number: int, merged_date: str) -> bool:
    """Append merge note to task ledger.

    Args:
        task_id: Task ID (e.g., QEFC-007)
        pr_number: PR number that was merged
        merged_date: Merge date in YYYY-MM-DD format

    Returns:
        True if note appended, False if already present or file not found
    """
    ledger_path = Path(f"docs/agent-ledger/tasks/{task_id}.md")

    if not ledger_path.exists():
        print(
            f"WARNING: Ledger not found at {ledger_path}. Skipping merge note.",
            file=sys.stderr,
        )
        return False

    content = ledger_path.read_text(encoding="utf-8")

    # Check if merge note already present (idempotency check)
    merge_signature = f"MERGED via PR #{pr_number}"
    if merge_signature in content:
        print(f"INFO: Merge note already present in {task_id} ledger. Skipping.")
        return False

    # Append to ## Review Notes section or create ## Merge Record section
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    merge_note = f"- ({timestamp}) **MERGED** via PR #{pr_number} to dev\n"

    # Find ## Review Notes section
    review_section_pattern = r"(## Review Notes\n)"
    match = re.search(review_section_pattern, content)

    if match:
        # Insert after ## Review Notes header
        insert_pos = match.end()
        new_content = content[:insert_pos] + merge_note + content[insert_pos:]
    else:
        # Create new ## Merge Record section before ## Final Gate
        final_gate_pattern = r"(## Final Gate)"
        match = re.search(final_gate_pattern, content)

        if match:
            merge_section = f"\n## Merge Record\n{merge_note}\n"
            insert_pos = match.start()
            new_content = content[:insert_pos] + merge_section + content[insert_pos:]
        else:
            # Append at end if no Final Gate section
            new_content = content + f"\n## Merge Record\n{merge_note}"

    ledger_path.write_text(new_content, encoding="utf-8")

    print(f"✓ Appended merge note to {task_id} ledger")
    return True


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Mark QEFC task as DONE after PR merge")
    parser.add_argument("--task-id", required=True, help="Task ID (e.g., QEFC-007)")
    parser.add_argument("--pr-number", required=True, type=int, help="PR number that was merged")
    parser.add_argument("--merged-date", required=True, help="Merge date (YYYY-MM-DD)")

    args = parser.parse_args()

    task_id = args.task_id.upper()  # Normalize to uppercase
    pr_number = args.pr_number
    merged_date = args.merged_date

    print(f"Processing task: {task_id} (PR #{pr_number}, merged {merged_date})")

    # Update TASKBOARD
    taskboard_updated = update_taskboard(task_id, merged_date)

    # Append merge note to ledger
    ledger_updated = append_merge_note(task_id, pr_number, merged_date)

    if not taskboard_updated and not ledger_updated:
        print(f"INFO: No changes made for {task_id} (already DONE or not found).")
        return 0  # Exit 0 for idempotency

    print(f"✓ Successfully processed {task_id}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
