import glob
import itertools
import os

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


# ================================================================
# 0. Utility Functions
# ================================================================
def elo_update(elo_a, elo_b, result, k=32):
    """Update ELO rating between two universes."""
    expected_a = 1 / (1 + 10 ** ((elo_b - elo_a) / 400))
    new_a = elo_a + k * (result - expected_a)
    return new_a


# ================================================================
# 1. Load QLF Universe files (4x4 truth tables)
# ================================================================
universes = {}
file_list = glob.glob("QLF_Universe_*.csv")

if not file_list:
    print("[ERROR] ไม่พบไฟล์ QLF_Universe_*.csv")
    exit()

for file in file_list:
    df = pd.read_csv(file, index_col=0)
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

    if df.shape != (4, 4):
        print(f"[WARNING] ข้ามไฟล์ {file} เพราะมีขนาดไม่ถูกต้อง: {df.shape}")
        continue

    universes[os.path.basename(file)] = df

print(f"[INFO] Loaded {len(universes)} universes")

states = ["T", "F", "N", "C"]

# ================================================================
# 2. Stress Test Scenarios
# ================================================================
test_cases = [("C", "C"), ("N", "T"), ("F", "T"), ("F", "C")]

# ================================================================
# 3. Benchmark Simulation (A)
# ================================================================
results = []

for name, logic in universes.items():
    score = 0
    details = []

    for a, b in test_cases:
        res = logic.loc[a, b]
        details.append(f"{a}+{b}={res}")

        if res == "T":
            score += 10
        elif res == "N":
            score += 7
        elif res == "C":
            score += 3
        elif res == "F" or res == "ERR":
            score -= 5

    results.append({"Universe": name, "Score": score, "Detail": " | ".join(details)})

benchmark_report = pd.DataFrame(results).sort_values(by="Score", ascending=False)

print("\n================ BENCHMARK REPORT ================")
print(benchmark_report[["Universe", "Score", "Detail"]].to_string(index=False))

winner = benchmark_report.iloc[0]["Universe"]
print(f"\n[VERDICT]: Benchmark Winner → {winner}")

# ================================================================
# 4. Visualization (C)
# ================================================================
plt.figure(figsize=(10, 6))
sns.barplot(data=benchmark_report, x="Universe", y="Score")
plt.title("QLF Universe Stability Score")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("QLF_Benchmark_Visualization.png")
plt.close()

print("[INFO] Saved visualization → QLF_Benchmark_Visualization.png")

# ================================================================
# 5. Tournament Mode (ELO Ranking) (D)
# ================================================================
elo = {name: 1000 for name in universes.keys()}  # init ELO

match_pairs = list(itertools.permutations(universes.keys(), 2))


def eval_duel(u1, u2):
    """Universe u1 vs u2 — นับแต้มจากตาราง 4x4 แบบไร้น้ำหนัก"""
    df1 = universes[u1]
    df2 = universes[u2]

    u1_pts = 0
    u2_pts = 0

    for a in states:
        for b in states:
            r1 = df1.loc[a, b]
            r2 = df2.loc[a, b]

            if r1 == "T":
                u1_pts += 1
            if r2 == "T":
                u2_pts += 1

    if u1_pts > u2_pts:
        return 1
    if u1_pts < u2_pts:
        return 0
    return 0.5


for u1, u2 in match_pairs:
    result = eval_duel(u1, u2)
    elo[u1] = elo_update(elo[u1], elo[u2], result)

elo_report = pd.DataFrame([{"Universe": u, "ELO": round(score)} for u, score in elo.items()]).sort_values(
    by="ELO", ascending=False
)

print("\n================= ELO TOURNAMENT RESULT =================")
print(elo_report.to_string(index=False))

champion = elo_report.iloc[0]["Universe"]
print(f"\n[CHAMPION]: Universe '{champion}' เป็นจักรวาลที่แข็งแกร่งที่สุดจากระบบ ELO")

# ================================================================
# END
# ================================================================
