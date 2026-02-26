 
ด้านล่างคือ **สรุประบบการทำงาน** + **Patch Log (QEFC-001 → QEFC-006)**  

---

## สรุประบบ workflow (เวอร์ชันใช้งานจริง)

### Artifact หลัก

* `docs/agent-ledger/CONTRACT.md` = กติกา/trigger/สิทธิ์
* `docs/agent-ledger/TASKBOARD.md` = สถานะงาน (source of truth)
* `docs/agent-ledger/tasks/QEFC-###.md` = ledger ต่อ 1 งาน (handoff + updates + gate)
* `docs/agent-ledger/DECISIONS.md` = ปิดประเด็น doctrine drift (ถ้ามี)
* `scripts/new_task.py` = generator สร้าง task + update TASKBOARD + สร้าง ledger

### Role split (ที่ทำให้ “ประสานกันได้จริง”)

* **Human (Chief Architect)**: commit/push/merge เท่านั้น
* **Sovereign-Orchestrator**: สร้างงาน/assign/เขียน handoff/อัปเดต TASKBOARD/สรุป gate
* **Quant-Engineer**: implement ตาม handoff + log ลง ledger + `READY_FOR_REVIEW`
* **Reviewer-CI**: review-only (edit ได้เฉพาะ ledger) + `READY_TO_COMMIT`

### Trigger ที่ทำให้ระบบเดินเองแบบ deterministic

1. Orchestrator ตั้ง `TASKBOARD: IN_PROGRESS` + ใส่ Handoff ใน `QEFC-###.md`
2. Quant-Engineer เริ่มงานด้วย prompt สั้น (claim หรือระบุ QEFC-ID)
3. Reviewer-CI ปิด gate ใน ledger
4. Human push/PR/merge

---

## แนะนำโครงสร้าง Patch log

สร้างไฟล์:

* `docs/agent-ledger/PATCHLOG.md` (สรุปเป็นแพตช์/รีลีส)
* (ถ้าอยากเป็นมาตรฐาน OSS) `CHANGELOG.md` ที่ root ก็ได้

---

## PATCHLOG (QEFC-001 → QEFC-006)

> หมายเหตุ: ใน TASKBOARD ที่แนบมาเดิมยังโชว์สถานะบางตัวเป็น READY_TO_COMMIT/REVIEW แต่จากการทำงานจริงของคุณ “merge เข้าสู่ dev ครบแล้ว” ให้ถือว่า patch log นี้คือ **สถานะล่าสุด** และควรอัปเดต TASKBOARD ให้เป็น DONE ตามจริง

### QEFC-001 — Bootstrap agent-ledger and operating protocol

**เพิ่มระบบ Ledger coordination ทั้งชุด**

* เพิ่มโครง `docs/agent-ledger/` + `tasks/`
* เพิ่มสคริปต์ `scripts/new_task.py` สำหรับสร้าง QEFC task อัตโนมัติ
* วาง workflow: Orchestrator dispatch → Quant implement → Human merge

**ผลลัพธ์:** ระบบเริ่มทำงานแบบ task-driven ได้

---

### QEFC-002 — VS Code task + Quickstart manual

**ทำให้ “สร้างงานใหม่” ง่ายมาก**

* เพิ่ม VS Code Task สำหรับเรียก `scripts/new_task.py`
* เพิ่ม `docs/agent-ledger/README.md` เป็น user manual/quickstart

**ผลลัพธ์:** ลด friction ในการเริ่ม task รอบใหม่ และทำให้ onboarding agents/humans ง่ายขึ้น

---

### QEFC-003 — PR template (QEFC-compliant)

**บังคับรูปแบบ PR ให้ผูกกับ ledger**

* เพิ่ม/ปรับ `.github/pull_request_template.md`
* ฟอร์ม PR มี Task ID + ledger link + validation + manual check + risks

**ผลลัพธ์:** ทุก PR trace กลับไป QEFC ledger ได้แบบ audit-ready

---

### QEFC-004 — Issue template intake (QEFC Task Request)

**ทำ intake งานให้เป็นมาตรฐาน**

* เพิ่ม `.github/ISSUE_TEMPLATE/` สำหรับรับ “คำขอ task”
* Orchestrator triage → ถ้าผ่านจึงสร้าง ledger จริงด้วย `new_task.py`

**ผลลัพธ์:** งานเข้าระบบอย่างเป็นระเบียบ ไม่หลุด protocol

---

### QEFC-005 — CI check: require QEFC-### in PR title/body

**เพิ่ม guard rail ระดับ CI**

* เพิ่ม workflow `.github/workflows/qefc-id-check.yml`
* PR ต้องมี `QEFC-###` ใน title หรือ body ไม่งั้น check fail
* มีรอบแก้บั๊กเรื่อง regex quoting/escape ใน bash จน stable แล้ว (merge confirmed)

**ผลลัพธ์:** ป้องกัน PR ที่ไม่ผูก task id (traceability enforcement)

---

### QEFC-006 — `.gitattributes` normalize line endings (LF)

**ลด noise จาก CRLF/LF บน Windows**

* เพิ่ม `.gitattributes` เพื่อ normalize line endings
* ลด warning/diff ที่เกิดจาก line ending mismatch

**ผลลัพธ์:** PR/Docs diff สะอาดขึ้น ทำงานข้าม OS ได้ลื่น

---

## “สมบูรณ์แล้ว” แต่ควรทำอีก 1 อย่างเพื่อให้ปิดวงจรจริง 100%

ตอนนี้คุณ merge แล้ว แต่ TASKBOARD อาจยังค้างสถานะในบางช่วง (จากไฟล์เก่า)
งานที่คุ้มมากเป็น QEFC ถัดไป (ถ้าจะทำ) คือ:

**QEFC-007 — Auto-close TASKBOARD after merge**

* GitHub Action ที่เมื่อ PR merged และมี `QEFC-###` → ไป update ledger/TASKBOARD ให้เป็น DONE อัตโนมัติ
  (จะทำให้ “human ไม่ต้องคอยอัปเดต status” และลดความไม่ตรงของข้อมูล...)
 