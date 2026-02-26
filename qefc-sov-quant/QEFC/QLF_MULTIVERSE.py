import itertools

import pandas as pd

# 1. กำหนดสถานะทั้ง 4 ของ Quaternary Logic
states = ["T", "F", "N", "C"]


def generate_qlf_table(q1_collapse, q2_catalyst, q3_soft_convert):
    """
    ฟังก์ชันสร้าง Truth Table ตามพารามิเตอร์ฟิสิกส์
    """
    # สร้างเมทริกซ์ว่าง 4x4
    table = {s: {s2: "" for s2 in states} for s in states}

    # --- กฎพื้นฐาน (Fundamental Identity) ---
    table["T"]["T"] = "T"
    table["N"]["N"] = "N"

    # --- Q1: การปะทะกันของความขัดแย้ง (Conflict + Conflict) ---
    # ถ้า Collapse จะกลายเป็น True (T) ถ้า Stable จะยังเป็น Conflict (C)
    table["C"]["C"] = "T" if q1_collapse else "C"

    # --- Q3: การจัดการ Noise (F) ---
    # ถ้า Soft-Convert จะเปลี่ยนเป็น Null (N) ถ้า Hard-Purge จะคงเป็น False (F)
    f_res = "N" if q3_soft_convert else "F"
    for s in states:
        table["F"][s] = f_res
        table[s]["F"] = f_res

    # --- Q2: บทบาทของ Null (N) ---
    if q2_catalyst:
        # แบบ Catalyst (Active): Null กระตุ้นให้เกิดแรงตึงหรือการยุบตัว
        table["T"]["N"] = "C"
        table["N"]["T"] = "C"
        table["N"]["C"] = "T"
        table["C"]["N"] = "T"
    else:
        # แบบ Vacuum (Passive): Null ไม่เปลี่ยนสถานะของสัจจะหรือความขัดแย้ง
        table["T"]["N"] = "T"
        table["N"]["T"] = "T"
        table["N"]["C"] = "C"
        table["C"]["N"] = "C"

    # --- แรงตึงมาตรฐาน (Tension) ---
    table["T"]["C"] = "C"
    table["C"]["T"] = "C"

    # แปลงเป็น DataFrame เพื่อความสวยงามและการบันทึก
    return pd.DataFrame(table).reindex(index=states, columns=states)


# 2. ตั้งค่า Permutations ทั้งหมด
options = {
    "Q1": ["Stable", "Collapse"],
    "Q2": ["Passive", "Catalyst"],
    "Q3": ["Hard-Purge", "Soft-Convert"],
}

# สร้าง List ของความเป็นไปได้ทั้งหมด (8 ชุด)
combinations = list(itertools.product(options["Q1"], options["Q2"], options["Q3"]))

# 3. รันการสร้างไฟล์
print("--- Starting Sovereign Engine Logic Generation ---")
for i, (q1, q2, q3) in enumerate(combinations, 1):
    q1_bool = q1 == "Collapse"
    q2_bool = q2 == "Catalyst"
    q3_bool = q3 == "Soft-Convert"

    df = generate_qlf_table(q1_bool, q2_bool, q3_bool)

    filename = f"QLF_Universe_{i}.csv"
    df.to_csv(filename)

    print(f"File {i}: {filename} | Parameters: Q1={q1}, Q2={q2}, Q3={q3}")

print("\n[SUCCESS] All 8 logic universes have been compiled.")
