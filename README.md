# qlf-sov-quant-engine

Sovereign-Quant Doctrine v2.2 (Deployable Blueprint – Unified)
Autonomous Capital Governance Architecture
Status: Deployable (Lab Mode → Production Ready)
Scope: Multi-Agent Quant + QLF Meta Allocation + Virtual Broker + Indices + FinRL + QLib
Core Principle: Strategy thinks, Sovereign decides, Risk vetoes, Broker executes

0) System Identity
ระบบนี้ ไม่ใช่ EA, ไม่ใช่ single-strategy bot, ไม่ใช่ indicator stack
ระบบนี้คือ:
Autonomous Capital Governance System
ระบบ “จัดสรรทุนอัตโนมัติ” ที่มี ชั้นตรรกะการตัดสินใจเหนือสัญญาณ (decision-about-decision)

1) Core Philosophy — Principle of Separation
Role Split
Strategy Agents = Specialists (เสนอไอเดีย)
MRD = Market Summarizer (สรุปสภาพตลาด)
QLF = Meta-Decision (ตัดสิน “สถานะของความรู้/ความขัดแย้ง”)
Sovereign Allocator = Capital Sizing (จัดสรรทุน/Exposure)
Risk Engine = Veto Authority (มีสิทธิ์ฆ่าระบบ)
Broker = Dumb Executor (Lab=Virtual, Prod=MT5 Bridge)
ข้อห้าม (Hard Laws)
Strategy ห้าม sizing position
Strategy ห้าม override risk
Strategy ห้าม ยิงออเดอร์เข้าตลาดโดยตรง

2) Layer Architecture (v2.2 Unified)
┌──────────────────────────────────────────┐
│                MARKET DATA               │
│ FX / XAU / INDICES (US100, SPX, DAX...)  │
└──────────────────────────────────────────┘
                    │
                    ▼
┌──────────────────────────────────────────┐
│            DATA + FEATURES LAYER         │
│ loader + feature_engineer + QLib feats   │  ◄ QLib lives here
└──────────────────────────────────────────┘
                    │
                    ▼
┌──────────────────────────────────────────┐
│            SNAPSHOT BUILDER              │
│ features + history + portfolio state     │
└──────────────────────────────────────────┘
                    │
                    ▼
┌──────────────────────────────────────────┐
│             STRATEGY AGENTS              │
│ Trend | MeanRev | ICT | Indices | FinRL  │
└──────────────────────────────────────────┘
                    │
                    ▼
┌──────────────────────────────────────────┐
│        MARKET REGIME DETECTOR (MRD)      │
│ regime + confidence + session flags      │
└──────────────────────────────────────────┘
                    │
                    ▼
┌──────────────────────────────────────────┐
│            QLF META ENGINE               │
│            T / F / C / S / W             │
└──────────────────────────────────────────┘
                    │
                    ▼
┌──────────────────────────────────────────┐
│         SOVEREIGN ALLOCATOR              │
│ position sizing + exposure control       │
└──────────────────────────────────────────┘
                    │
                    ▼
┌──────────────────────────────────────────┐
│             RISK ENGINE (VETO)           │
│ DD / margin / spread / slip / kill-switch│
└──────────────────────────────────────────┘
                    │
                    ▼
┌──────────────────────────────────────────┐
│  VIRTUAL BROKER (LAB) / MT5 BRIDGE (PROD)│
│ fill + cost + margin + equity calc       │
└──────────────────────────────────────────┘
                    │
                    ▼
┌──────────────────────────────────────────┐
│          PERFORMANCE ANALYTICS           │
└──────────────────────────────────────────┘


3) Repository Blueprint (Deployable Directory Structure)
Sovereign-Quant-v2/
│
├── config/
│   ├── system_config.yaml
│   ├── instruments.yaml                 # (NEW) Indices/FX specs
│   └── strategy_weights.json            # calibration weights (offline)
│
├── core/
│   ├── types.py                         # contracts: snapshot/signal/decision/order
│   ├── instrument_registry.py           # (NEW) load+validate instruments.yaml
│   ├── snapshot_builder.py
│   ├── mrd_engine.py                    # (UPGRADE) regime + session flags
│   ├── qlf_engine.py                    # T/F/C/S/W + risk_factor + cooldown
│   ├── sovereign_allocator.py
│   ├── risk_engine.py
│   ├── orchestrator.py                  # main controller (bar-by-bar driver)
│   └── base_agent.py                    # abstract agent interface
│
├── data/
│   ├── data_loader.py                   # OHLCV + features merge
│   ├── feature_engineer.py              # basic TA indicators
│   └── qlib_pipeline.py                 # (NEW) offline factors -> parquet
│
├── strategies/
│   ├── trend/
│   ├── mean_reversion/
│   ├── smc/
│   │   └── ict_agent.py                 # structure specialist
│   ├── indices/
│   │   ├── opening_range.py             # ORB
│   │   ├── session_breakout.py
│   │   └── volatility_guard.py          # “market condition reporter”
│   └── rl/
│       ├── finrl_agent.py               # (NEW) inference wrapper -> AgentSignal
│       ├── gym_env_wrapper.py           # optional: training env
│       └── model_repository/
│
├── simulation/
│   ├── virtual_broker.py
│   ├── order_matcher.py
│   ├── portfolio.py
│   └── performance_analyst.py
│
├── main_backtest.py
└── requirements.txt                     # qlib, stable-baselines3, gym, etc.


4) Contracts ([core/types.py](core/types.py)) — ทีม Dev ต้องยึดเป็นมาตรฐานเดียว
เป้าหมาย: ทุก module คุยกันด้วย “สัญญาเดียว” ลด bug
4.1 MarketSnapshot (Agent Input)
ประกอบด้วยอย่างน้อย:
timestamp
symbol
price (open/high/low/close)
history_window (N bars)
features (ta_* + feat_* + meta_*)
portfolio_state (balance/equity/positions/margin)
instrument_spec (จาก instrument_registry)
4.2 AgentSignal (Agent Output)
agent_name
symbol
intent = LONG / SHORT / NEUTRAL
confidence = 0..1
invalidation_price (optional)
tags (เช่น ["ICT","sweep"], ["FinRL","AI"])
metadata (เช่น BOS level, ORB range, model name)
4.3 RegimeInfo (MRD Output)
regime_label (TREND_RUN / RANGE / VOLATILE / CHAOS …)
regime_confidence (0..1)
session_state (ASIA/LONDON/NY_OPEN/NY_MID/CLOSE…)
volatility_flags (เช่น OPEN_SPIKE_RISK, GAP_RISK)
4.4 QLFDecision (QLF Output)
state = T / F / C / S / W
risk_factor = 0..1 (ตัวคูณความเสี่ยงระดับ meta)
reason_codes (list)
cooldown_bars (กัน flip)
4.5 AllocationDecision (Allocator Output)
action = OPEN / CLOSE / HOLD / HEDGE / FLATTEN
orders (list of OrderIntent)
target_exposure (per symbol / per direction)
notes (audit log)
4.6 RiskVerdict (Risk Output)
approved True/False
modified_decision (optional)
kill_switch True/False
reason_codes

5) Instrument Registry (Indices-Ready Core)
เหตุผล: Indices ต่างจาก FX/XAU มาก (tick/contract/session/fees) sizing จะพังถ้าไม่มี registry
5.1 instruments.yaml (config)
กำหนดต่อ symbol:
tick_size, contract_size, tick_value/point_value
min_lot/max_lot/lot_step
sessions (multi session)
commission/spread/swap model
margin_rate/leverage cap
5.2 instrument_registry.py (core)
load + validate schema
normalize units (ticks/value)
provide helper ให้ Allocator ใช้:
calc_lot_from_risk(risk_amount, sl_distance_ticks)
(สำคัญ: strategy ห้ามเรียกเอง)

6) Agents Layer (Strategy Specialists)
6.1 กติกากลางของ Agents
Agents ทำได้:
detect setup
propose intent + confidence
define invalidation
attach tags/metadata
Agents ห้าม:
sizing / portfolio mgmt
override risk
execute order
6.2 Agent Packs (v2.2)
(A) Trend Agent
breakout / continuation
ทำงานดีใน TREND_RUN
(B) Mean Reversion Agent
range / bollinger
ทำงานดีใน RANGE
(C) ICT Agent (SMC / Inner Circle Trader)
Role: Structure specialist (tactical input)
Detects:
liquidity sweep
BOS / CHoCH
FVG
OB
Returns: LONG/SHORT + confidence + invalidation + tags
ICT ไม่ใช่ decision layer และไม่ใช่ risk layer
(D) Indices Agents (NEW)
Opening Range Breakout (ORB): สร้าง range ช่วงเปิดตลาด แล้ว breakout
Session Breakout / Continuation: follow-through หลัง breakout
Volatility Guard (สำคัญ): ไม่ใช่ trade maker แต่เป็น “market condition reporter”
ส่ง NEUTRAL + tag ["VOL_GUARD"] + flags เพื่อช่วย QLF/MRD/Risk
(E) FinRL Agent (NEW)
Role: Action proposer (AI Agent)
รับ snapshot → model.predict()
map action → LONG/SHORT/NEUTRAL
ใส่ tags ["FinRL","AI", "<algo>"]
มี deadzone + cooldown/minhold กัน flip-flop
FinRL ถูกครอบโดย QLF/Risk เสมอ

7) QLib Integration (Data/Research Workflow)
QLib ไม่ใช่ execution และไม่ใช่ QLF
QLib คือ:
feature factory (factor generation)
research workflow
optional: ช่วย MRD แยก regime
Mode A (แนะนำเริ่มต้น): Offline Factors
qlib_pipeline.py generate factors → export features.parquet
data_loader.py merge OHLCV + features.parquet
snapshot_builder ส่ง feat_* ให้ agents/mrd ใช้ทันที
ข้อดี: stable, deploy ง่าย, latency ต่ำ

8) MRD (Market Regime Detector) — + Session Logic (Indices)
MRD Output
regime_label, regime_confidence
session_state
volatility_flags (OPEN_SPIKE_RISK, GAP_RISK, …)
หลักการ: MRD “รายงานสภาพตลาด” ไม่สั่ง QLF โดยตรง
QLF จะอ่าน MRD + signals เพื่อออก state

9) QLF Meta Engine (หัวใจระบบ)
QLF = decision-about-decision
ไม่ใช่ indicator / ไม่ใช่ strategy
9.1 QLF States (ล็อกนิยาม)
T alignment → full allocation (risk_factor≈1.0)
F toxic regime → withdraw (risk_factor=0)
C conflict → half-risk / hedge (risk_factor≈0.5)
S suspense/unclear/vol anomaly → wait (risk_factor=0)
W emergency → close all + freeze (risk_factor=0)
9.2 QLF Inputs
agent signals vector
MRD regime + session/flags
volatility anomaly
drawdown state (จาก risk/portfolio)
9.3 QLF Outputs
QLFDecision(state, risk_factor, reason_codes, cooldown_bars)

10) Sovereign Allocator (Capital Allocation)
รับ:
QLFDecision
agent signals
MRD regime
instrument spec (from registry)
ส่ง:
AllocationDecision: order intents + target exposure
กฎหลัก
QLF บอก risk_factor
Allocator คำนวณ lot/size ตาม config + confidence + instrument tick value
Allocator ไม่ override Risk

11) Risk Engine (Veto Layer)
Risk overrides everything.
Checks:
drawdown / equity floor
margin / liquidation proximity
spread anomaly
slippage anomaly
session hazard flags (optional policy)
kill switch trigger
Actions:
reduce risk / reject new orders
force close (FLATTEN)
emergency W (freeze)

12) Broker Layer
12.1 Virtual Broker (Lab Mode)
Simulates:
fill logic (limit/stop/market)
spread/commission/swap
margin/equity
liquidation/margin call
Fill Rules
market → slippage
limit → next bar touch (high/low cross)
stop → trigger + slippage
12.2 Production Bridge (Phase 3)
Python Brain → MT5 Bridge → Broker
MT5 = dumb execution only

13) Orchestrator + Main Loop (Bar-by-Bar Time Driver)
Single deterministic loop (สำคัญต่อ replay/backtest)
Pseudo:
broker = VirtualBroker(...)
registry = InstrumentRegistry(...)
data = load_ohlcv_and_features(...)

for bar in data:
    broker.update_price(bar)
    broker.check_orders(bar.high, bar.low)

    snapshot = build_snapshot(bar, history, portfolio, registry)
    signals  = agents.analyze(snapshot)
    regime   = mrd.detect(snapshot)

    qlf_dec  = qlf.evaluate(signals, regime, portfolio_state)
    alloc    = allocator.allocate(qlf_dec, signals, regime, registry)

    verdict  = risk.veto(alloc, snapshot, regime, broker_state)
    broker.execute(verdict.decision)

report()


14) Deployment Phases
Phase 1: Lab simulation (virtual broker)
Phase 2: Forward test (paper/bridge)
Phase 3: MT5 execution bridge (production)

15) Key Design Laws (Final)
Strategy cannot allocate capital
QLF controls meta exposure (ผ่าน risk_factor/state)
Risk can kill everything
Execution must be dumb

16) Next Steps (Build Order)
core/types.py (contracts)
config/instruments.yaml + core/instrument_registry.py
core/qlf_engine.py (T/F/C/S/W + cooldown + reason_codes)
simulation/virtual_broker.py + order_matcher.py
core/orchestrator.py + main_backtest.py
Agents: ICT + Indices (ORB + VolGuard) + FinRL wrapper
data/qlib_pipeline.py (Mode A) + merge into snapshot

17) Final Definition
Sovereign-Quant v2.2 คือระบบที่ formalize
“decision-about-decision” ในการจัดสรรทุนอัตโนมัติ
โดย QLF คือแกนการปกครอง, Risk คือ veto, Broker คือ executor
 

VIII. Scalping Governance Pack (v2.3)
Scalper is NOT independent strategy.
Scalper = Specialist under Sovereign Budget.

1️⃣ Maker-First Doctrine
Scalper must:
Use LIMIT-first lifecycle


Respect spread ceiling


Respect regime allowlist


Respect throttle + budget



2️⃣ Scalper Budget Engine
Each scalper has:
Daily loss cap


Hourly trade cap


Pending order cap


Cooldown after loss


Risk can kill scalper independently before global kill-switch.

3️⃣ Limit Lifecycle Integrity (Non-Negotiable)
Order must support:
place


amend


partial fill


expiry


cancel on veto


If lifecycle incomplete → do NOT deploy.

4️⃣ Scalping KPIs (New Reporting Section)
Maker ratio


Time-to-fill


Cancel rate


Adverse selection %


Spread histogram during activity


PnL after cost


QLF state distribution during scalper trades



IX. Online MRD (Phase 2+)
Current:
Static monthly retrain
Future:
Online posterior update
Constraints:
Kalman gain tuning


Persistence prior


Drift detection


Controlled forward testing



X. Formal Definition of Sovereign Quant
Sovereign Quant is:
A capital governance system that separates
 signal generation from capital authority
 and validates every decision layer independently
 using statistical, structural, and interaction testing.
It is NOT:
Strategy stack


Indicator ensemble


ML wrapper


EA


It is:
A layered capital constitution.

XI. Final Governance Laws (Extended)
Strategy cannot size.


Strategy cannot override risk.


MRD cannot gate strategy absolutely.


QLF must use statistical reliability conditioning.


Allocator must respect QLF risk_factor.


Risk has absolute veto.


Execution must remain dumb.


Every layer must pass ablation testing.


Interaction effect must be measured.


Reporting is mandatory before capital deployment.



XII. End-State Vision
When system reaches:
Stable Sharpe > 2.0


Interaction ≈ 0 or positive


Robust to MRD degradation


Drawdown tail reduced > 25%


Complexity ratio acceptable



 




—----------------------------------------------------------------------------------------------------------------------------
REPORTING ARCHITECTURE

1. โครงสร้าง Reporting
ระบบแบ่งเป็น 2 โหมด + 1 analytics suite
A. Realtime Debug (ระหว่างรัน)
ใช้ดู “การตัดสินใจต่อบาร์”
สำหรับ dev / live monitoring
structured log ต่อ event
B. End-of-Batch Report (หลังจบ run)
ใช้ตัดสิน Go/No-Go
executive metrics
governance analysis
risk attribution
C. Visual + Advanced Analytics
plots
attribution
session heatmap
QLF timeline



2️. Realtime Debug Doctrine
วัตถุประสงค์
ดูการตัดสินใจ ทีละบาร์ แบบ deterministic
ต้องตอบได้ว่า:
“ทำไมระบบถึงเข้า/ไม่เข้า”
Format
[TIME] | [STAGE] | [DETAILS]

Mandatory Events
ต้อง print เฉพาะ events สำคัญ
(ไม่ spam)
1. Regime change
10:00 | REGIME | TREND_RUN conf=0.82 flags=[VOL_SPIKE]

2. Agent signals
10:00 | AGENTS |
Trend:LONG(0.8)
ICT:SHORT(0.6)[BearishOB]
FinRL:LONG(0.4)
Scalp:NEUTRAL[SPREAD_HIGH]

3. QLF decision
10:00 | QLF | STATE=C reason=Trend!=ICT action=HALF_RISK

4. Allocator
10:00 | ALLOC | risk_factor=0.5 size=0.3 lot

5. Risk veto
10:00 | RISK | APPROVED margin=420%

หรือ
10:00 | RISK | VETO reason=SPREAD_ANOMALY

6. Execution
10:00 | EXEC | OPEN BUY XAUUSD 0.3 @ 1945.2

7. Scalper lifecycle (v2.3)
10:00 | LIMIT | PLACED @1945.1 ttl=1200ms
10:00 | LIMIT | FILLED
10:00 | LIMIT | CANCELLED reason=expiry


Debug Principles
ต้อง deterministic
ต้อง parse ได้ (machine-readable)
ห้าม spam indicator values ทุกบาร์

3️⃣ End-of-Batch Reporting Doctrine
นี่คือ report หลัก ที่ใช้ประเมินระบบ
แบ่ง 4 layers

🟢 Layer 1 — Executive Summary
Run Metadata
ต้อง print:
Run ID
Git commit
Config hash
Period
Symbols
Mode (Lab / MT5)
Cost model
Bars processed
Missing data %
Performance
Final equity
Net PnL
Return %
CAGR
Sharpe
Sortino
Calmar
Profit factor
Expectancy
Win rate
Total trades
Trades/day
Risk
Max DD %
DD duration
Recovery factor
Capital efficiency
Avg exposure %
Max exposure %
Cost as % of gross profit
ถ้า cost > 20% = ระบบ feed broker

🔵 Layer 2 — Governance Report (QLF + Agents)
QLF Analytics
ต้อง print:
Time in state
T: 42%
C: 18%
S: 25%
F: 10%
W: 5%

State efficiency
Win rate when T
Loss avoided during F
Risk saved during C
Transition matrix
T→C
C→S
S→W

Agent Scoreboard
ต่อ agent:
signals generated
accepted
vetoed
win rate
payoff
PnL contribution
confidence calibration
best regime

Conflict Analysis
Top conflicting agent pairs
Resolution method
Hedge vs wait %

🔴 Layer 3 — Risk & Execution Report
Risk veto
Drawdown veto: 4
Spread veto: 12
Margin veto: 1
Session veto: 3

Saved loss estimate
PnL ที่หลบได้จาก veto

Execution quality
avg slippage
max slippage
fill rate
limit fill rate
rejection rate
Cost breakdown
spread cost
commission
swap

Drawdown analysis
Top 5 DD:
depth
duration
regime
agent cause

🟣 Layer 4 — Specialized Packs
Indices pack
PnL by session
ORB success rate
fakeout rate
AI pack
FinRL
action distribution
override rate
turnover
QLib
factor coverage
missing values
feature importance (optional)

🟡 Scalping Pack (v2.3)
Maker stats
limit ratio
cancel rate
amend rate
time to fill
Cost survival
net PnL after cost
adverse selection %
Risk interaction
veto triggered by scalper
daily loss limit hits

4. Visual Artifacts
ต้อง generate:
Mandatory
Equity curve
Drawdown plot
QLF state timeline
PnL by session heatmap
Optional
agent entry overlay
regime overlay

5. Debug vs Report Doctrine
Realtime debug
print decision flow
End batch
print analytics
ทั้งสองต้องมี
debug = microscope
report = telescope

6. Print Policy (Final)
During run
REGIME
AGENTS
QLF
RISK
EXEC
LIMIT lifecycle

After run
Executive summary
QLF report
Agent scoreboard
Risk report
Execution report
Scalping pack


7. What NOT to print
ห้าม print:
indicator values ทุก bar
full dataframe
tick spam
print เฉพาะ:
decision events

8. Golden Rule
รายงานที่ดีต้องตอบ:
กำไรเพราะอะไร
ขาดทุนเพราะอะไร
QLF ช่วยจริงไหม
Risk veto ช่วยจริงไหม
Broker กินเราไหม

9. Final Reporting Architecture
Realtime Log → Debug
End Batch → Decision
Charts → Insight


10. Final Verdict
โครง reporting ที่คุณเสนอ:
ถูกต้องระดับ institutional
มีครบ:
governance
attribution
execution
cost
AI
scalping 











Sovereign-Quant Doctrine v2.2.1
Phase-1 Governance Patch — Dual Rating & Allocator Sovereignty

I. Structural Additions to v2.2
Phase-1 Patch introduces:
Mortal Shadow Architecture (No Reset Doctrine)


Dual Rating Engine (Multiplicative + Additive + Divergence)


Dynamic Max Active Agents


Correlation Penalty in Allocator Layer


Deterministic Allocator with Controlled Stochastic Exploration


Epistemic Consistency Guard (Rating Divergence Conditioning)


This patch formalizes capital tournament logic without violating Separation of Concerns.

II. Mortal Shadow Doctrine
Law: No Reset Capital
If Shadow DD = 100%
 → Strategy = DEAD
 → Archived permanently
 → Statistics frozen
No resurrection in Phase-1.
Rationale:
Prevent immortal gambler bias


Encode survival into fitness


Preserve Darwinian pressure


Shadow now measures:
Expectancy Quality


Fragility


Tail Stability


Regime Robustness


Survival State


Shadow remains epistemic layer only.
 It does NOT observe capital allocation noise.

III. Dual Rating Engine (New Core Subsystem)
Metric Vector (Normalized [0,1])
E = Expectancy Quality (WR × R/R)
 F = Fragility Index (MDD / AvgRunup)
 T = Tail Penalty (CVaR / MeanReturn)
 R = Regime Robustness (Sharpe spread inverted)
 S = Survival Flag (0/1)

1️⃣ Multiplicative Rating
R_mul =
 E × (1 − F) × (1 − T) × R × S
Purpose:
Strict sovereign pressure


Any structural weakness penalizes heavily


Encodes “one flaw can collapse”



2️⃣ Additive Rating
R_add =
 w1E + w2(1 − F) + w3(1 − T) + w4R + w5S
Purpose:
Noise-robust baseline


Structural audit reference


Stability comparator



3️⃣ Divergence Guard
D = |R_mul − R_add|
Interpretation:
Low D → epistemic agreement


High D → metric instability / structural tension



4️⃣ Final Fitness Score (QLF Input Form)
R_final = mean(R_mul, R_add) × exp(−kD)
This preserves:
Performance level


Structural agreement confidence


QLF consumes R_final, not raw R_mul or R_add.

IV. Correlation Governance (Allocator Layer Only)
Decision:
Correlation penalty belongs exclusively in Allocator layer.
Architectural Reason:
Correlation = portfolio property
 Not intrinsic agent fitness
Rating must remain absolute.
 Allocator manages diversification.

Correlation Enforcement Modes
Allocator may apply:
Hard Cluster Cap
 High-corr agents share exposure ceiling


Soft Penalty
 weight_i ← weight_i × (1 − avg_corr_i)


Diversification Optimizer
 Signal-space minimum variance weighting


Correlation must NOT modify rating memory.

V. Dynamic Max Active Agents
Max active agents determined by:
Regime confidence


Rating dispersion


Divergence consistency


System uncertainty


Principle:
High certainty → concentrate
 High uncertainty → diversify
Bounded range example:
 min 2
 max 8
This is structural guard, not portfolio optimizer.
Correlation enforcement remains in Allocator.

VI. Deterministic + Controlled Stochastic Allocator
Allocator baseline = deterministic.
Weights derived from:
R_final


Regime compatibility


Correlation penalty


QLF risk_factor



Stochastic Activation Condition
Stochastic exploration allowed ONLY when:
uncertainty > threshold
Where uncertainty may derive from:
High divergence D


Low regime confidence


High entropy of signal distribution



Stochastic Rules
Apply only to near-tie weights


Max perturbation ±10%


Total exposure unchanged


No direction reversal allowed


Seeded and configurable


Disabled in strict production mode if required


Purpose:
Prevent crowding lock-in


Allow marginal agents exposure


Improve evolutionary robustness


Shadow rating remains unaffected.

VII. QLF Boundary Guard (Reaffirmed)
QLF:
Reads:
Signals vector


Regime


Portfolio raw state


R_final


Divergence summary


QLF does NOT:
Compute correlation


Access correlation matrix


Override Risk verdict


QLF remains small state machine (≤300 LOC core logic).

VIII. Updated Capital Constitution (Phase-1)
Strategy → generates signals
 Shadow → evaluates intrinsic survival fitness
 Dual Rating → produces epistemic score
 QLF → meta-state decision
 Allocator → exposure + correlation + exploration
 Risk → absolute veto
 Broker → dumb execution
No layer contamination permitted.

IX. Additional Freeze Constraints
Before implementation:
Rolling window policy fixed (rating window length immutable in Phase-1)


Regime sample threshold enforced


Correlation computed via rolling signal/return vector (no lookahead)


Allocator LOC constraint (<500 core)


QLF LOC constraint (<300 core)



X. Phase-1 Completion Criteria
Architecture considered stable when:
Rating divergence stable over time


Correlation penalty demonstrably reduces concentration


Stochastic exploration does not increase tail DD


Shadow mortality observable and interpretable


Ablation tests confirm layer independence



XI. Constitutional Identity (Reaffirmed)
Sovereign Quant is:
A layered capital governance constitution
 where signal generation, epistemic validation,
 portfolio construction, and risk sovereignty
 are separated and independently auditable.
It is not:
Indicator stack


EA


ML wrapper


Strategy ensemble


It is:
 Decision-about-decision architecture.

XII. Phase-1 Status
Architecture: Frozen
 Governance: Coherent
 Authority boundaries: Clean
 Epistemic safeguards: Installed
 Portfolio diversification: Allocator-bound
 Survival logic: Darwinian
Ready for implementation beginning at:
core/types.py
End









































Sovereign-Quant Doctrine v2.2.2
Phase-1 Governance Stability & Dimensional Control Patch
สถานะ: Constitutional Extension
 ขอบเขต: QLib Governance, FinRL Behavioral Guard, QLF Dimensional Scaling, Complexity Control
 ไม่ละเมิด Separation of Concerns
 ไม่เปลี่ยน Authority Boundaries
 เพิ่ม Stability & Auditability Layer

I. QLib Governance Hardening
QLib remains:
Data Layer Only
 Offline Feature Factory
 No execution authority
 No decision authority
1️⃣ Factor Lineage Enforcement (Mandatory)
Every generated factor set must include:
factor_version_id


raw_data_hash


generation_timestamp


feature_schema_hash


Snapshot Contract Extension
MarketSnapshot must now include:
factor_version_id
feature_schema_version
Guard Law
If:
model.feature_schema_version != snapshot.feature_schema_version
→ FinRL Agent must refuse inference
 → Emit structured alert
 → QLF receives neutral signal
This prevents silent feature drift corruption.

2️⃣ Feature Stability Monitoring Module (Offline)
New subsystem:
 data/factor_stability_monitor.py
Metrics required:
Rolling Mean Shift
 Rolling Std Drift
 Correlation Structure Drift
Threshold:
2σ deviation over rolling baseline
If triggered:
Raise Governance Warning


Flag MRD regime reliability


Flag FinRL retrain candidate


Important:
This module does NOT alter execution flow.
 It only generates governance alerts.

II. FinRL Behavioral Stability Guard
FinRL remains:
Signal proposer only
 No sizing
 No order authority
1️⃣ Action Entropy Monitoring (Required)
For each FinRL agent:
Track rolling window:
action_distribution


policy_entropy


If entropy < threshold for N consecutive windows:
QLF must reduce confidence weight
 OR
 Force temporary cooldown
This is Behavioral Governance Override
 (not Risk layer)

2️⃣ Reward Alignment Mandate (Training Doctrine)
Training reward must include:
PnL component
 Drawdown penalty
 Turnover penalty
 Regime conflict penalty
Objective:
Optimize survivability, not raw profit.
This aligns RL with Sovereign Constitution.

3️⃣ State Schema Freeze Law
Every RL model must store:
state_schema_version


scaler_parameters


normalization_stats


Inference must verify:
snapshot.schema == model.schema
Mismatch → inference aborted.
No silent coercion allowed.

III. QLF Dimensional Compression Rule
QLF must never consume raw feature vectors.
Before QLF evaluation, system must compute:
Meta-Feature Compression Layer
QLF allowed inputs (bounded < 10 dimensions):
Consensus score


Conflict intensity


Rating divergence D


Regime confidence


Volatility anomaly flag


Portfolio drawdown state


Agent entropy summary


Rating dispersion


QLF core logic must remain finite state machine.
QLF LOC constraint reaffirmed:
 ≤ 300 LOC core logic

IV. Complexity Governance Metrics (New)
Two structural monitoring indices are now formalized.
1️⃣ Information Complexity Index (ICI)
Two forms allowed:
Static:
 ICI = (Number of agents + feature blocks) / Rolling Sharpe
Dynamic:
 ICI = ΔComplexity / ΔPerformance
If ICI increases persistently:
System enters Complexity Review Mode.
No automatic action.
 Manual governance review required.

2️⃣ Governance Friction Metric (GFM)
GFM =
 w1·ConflictRate
w2·RiskVetoRate


w3·AllocatorOverrideRate


Threshold example:
 GFM > 0.5 → Governance Stress Alert
This measures structural instability,
 not profitability.

V. Version Lock Extension (All Layers)
The following must be versioned and reproducible:
Factor schema
 Agent logic (commit hash)
 MRD model version
 Dual rating parameters
 QLF transition rules
 Allocator exploration config
Each backtest run must log:
config_hash


code_commit


factor_version_id


model_versions


Reproducibility is constitutional requirement.

VI. Governance Dashboard (Advisory Layer)
Non-execution module:
simulation/governance_dashboard.py
Displays:
ICI
 GFM
 Agent entropy
 Conflict matrix
 QLF transition heatmap
 Rating divergence timeline
Dashboard has:
Zero authority
 Zero influence on execution
It is observatory only.

VII. Mandatory Ablation Protocol
Every new component must pass:
Ablation test:
Sharpe delta


Max DD delta


Governance Friction delta


ICI delta


If complexity increases without measurable structural gain:
Component enters probation.
This enforces architectural discipline.

VIII. Architectural Scaling Verdict
QLF remains scalable because:
It consumes compressed meta-features
 It does not learn
 It does not scale dimensionally with factor pool
Dimensional explosion is contained below QLF.
QLF remains epistemic governor, not data processor.

IX. Updated Constitutional Identity (v2.2.2)
Sovereign Quant is now:
A layered capital governance constitution
 with enforced feature lineage,
 behavioral AI discipline,
 dimensional compression,
 and complexity auditing.
Signal generation is free.
 Capital authority is sovereign.
 Complexity is monitored.
 Drift is detectable.
 Reproducibility is mandatory.

X. Phase-1 Freeze Status (Updated)
Architecture: Frozen
 Governance: Hardened
 Dimensional scaling: Controlled
 Feature drift guard: Installed
 RL entropy guard: Installed
 Complexity creep monitor: Installed


Sovereign-Quant Doctrine v2.2.3
Constitutional Evolution Control Patch — 9JVMH
สถานะ: Ratified
 ประเภท: Structural Stability & Controlled Evolution Amendment
 Core Authority: Unchanged
 Objective: Allow slow endogenous evolution without destabilizing Constitutional Core

I. Constitutional Layer Separation (Formalized)
Sovereign-Quant ถูกแบ่งออกเป็น 3 ชั้นถาวร:
1️⃣ Immutable Core Layer (Frozen Constitution)
องค์ประกอบ:
QLF finite state machine logic


Risk veto structure


Allocation decision contract


Snapshot schema contract


Dimensional compression law (<10 meta-dimensions)


Pre-flight validation rules


Authority boundary enforcement


กฎ:
Core ห้าม mutate โดย runtime
 Core เปลี่ยนได้เฉพาะผ่าน Major Version Revision เท่านั้น
ตัวอย่าง:
 v2.x → v3.0 = Constitutional Reform
 ไม่อนุญาต minor drift ภายใน patch

2️⃣ Governed Extension Layer (Regulated Evolution Zone)
องค์ประกอบที่ evolve ได้:
Agent set


Factor pool


MRD model


RL models


Strategy weights


Rating parameters


เงื่อนไขการเพิ่ม/แก้ไข:
ต้องผ่าน Ablation Protocol


ต้องไม่ละเมิด Dimensional Compression Law


ต้องไม่เพิ่ม Authority Scope


ต้องไม่ทำให้ QLF adaptive


Promotion Process:
Sandbox → Evaluation → Governance Review → Extension Layer

3️⃣ Evolution Sandbox Layer (Isolated Mutation Lab)
ลักษณะ:
ทดลอง agent ใหม่


ทดลอง factor ใหม่


ทดลอง regime model ใหม่


ทดลอง compression prototype


ทดลอง adaptive mechanism


ข้อจำกัด:
ไม่มี capital authority


ไม่เชื่อม execution path


ไม่มีสิทธิ์ override production


ไม่มี shared state กับ Core


Sandbox ทำหน้าที่เป็น Research Organism
 แต่ไม่ใช่ Constitution

II. Evolution Budget Control
กำหนด Mutation Rate Cap ต่อรอบเวลา (Quarterly Default)
ตัวอย่างค่าเริ่มต้น:
ΔAgents ≤ +1
 ΔFeatureBlocks ≤ +10
 ΔICI ≤ +0.2
หากเกินงบ evolution:
→ Defer promotion
 → ไม่อนุญาต cumulative mutation
เป้าหมาย:
 ป้องกัน Complexity Creep

III. Stability Lock Period
หลัง component ใหม่ถูก promote:
Observation Freeze Period = 3–6 เดือน (configurable)
ในช่วงนี้:
ห้ามปรับ logic เพิ่มเติม


ห้าม retune parameter


ทำได้เฉพาะ bug fix ที่ไม่กระทบ logic


เหตุผล:
 ป้องกัน oscillatory adaptation loop

IV. Constitutional Boundary Tests (Mandatory)
ทุก component ใหม่ต้องผ่านการตรวจสอบว่า:
ไม่เพิ่ม QLF input dimensionality


ไม่เพิ่ม authority ให้ agent


ไม่ทำให้ compression layer adaptive


ไม่เพิ่ม shared mutable state


ไม่ bypass Risk / QLF chain


ละเมิดข้อใดข้อหนึ่ง → Reject

V. Structural Drift Monitor
เพิ่ม Structural Drift Score (SDS)
SDS คำนวณจาก:
Rolling change in ICI


Rolling change in GFM


Rolling change in Capital Utilization


QLF state transition distribution shift


หาก:
SDS > threshold ต่อเนื่อง ≥ N periods
→ Governance Review Required
หมายเหตุ:
 SDS เป็น diagnostic tool
 ไม่ใช่ automatic execution override

VI. Alpha vs Constitutional Stability Principle
Doctrine 9JVMH รับรองหลักการ:
“Alpha ที่ทำลาย Constitutional Stability
 สามารถถูกปฏิเสธได้”
Hierarchy of Value:
1️⃣ Capital Survivability
 2️⃣ Structural Stability
 3️⃣ Governance Clarity
 4️⃣ Alpha Generation
Alpha ไม่มีสิทธิ์ override Constitution

VII. Identity Preservation Clause
Sovereign-Quant ถูกนิยามใหม่อย่างเป็นทางการว่า:
"A Research Organism governed by a Frozen Constitutional Core."
Evolution เกิดได้
 แต่ Constitution ไม่ self-modify
QLF เป็น Epistemic Governor
 ไม่ใช่ Self-Evolving Entity

VIII. Versioning Update
Current Active Doctrine:
v2.2.3 + 9JVMH Amendment
Core: Frozen
 Extension: Regulated
 Sandbox: Isolated
 Mutation Rate: Capped
 Drift: Monitored
 Authority: Asymmetric

IX. Final Architectural Statement
Sovereign-Quant ไม่ใช่:
Signal engine


RL optimizer


Adaptive meta-learning system


Sovereign-Quant คือ:
A Constitutional Capital Governance System
 with Controlled Evolution Capacity
ระบบสามารถเติบโต
 โดยไม่สูญเสียตัวตน
Sovereign-Quant Doctrine v2.2.3
Production Readiness & Anti-Fragility Implementation Patch — PRX-01
สถานะ: Mandatory Before Phase 1
 ประเภท: Implementation Detail Expansion
 Objective: Close Execution Reality Gap & Prevent Systemic Fragility in Production Transition

I. Market Microstructure Simulation Layer (Phase 1 Mandatory)
1️⃣ Extended Execution Model (Virtual Broker Upgrade)
Lab Simulation ต้องรวม:
Dynamic spread model (volatility-dependent)


Slippage model (size-dependent)


Partial fill simulation


Order queue delay simulation


Session gap risk model


Latency injection (configurable ms delay)


Spread widening during volatility spike


Implementation Requirement:
virtual_broker.py ต้องรองรับ:
execution_model = {
   "spread_mode": "dynamic",
   "slippage_model": "size_volatility_scaled",
   "partial_fill_probability": float,
   "latency_ms": int,
   "gap_model": True
}
Allocator & Risk Layer ต้องรับมือกับ partial fill scenario
 ห้าม assume fill 100%

II. Absolute Capital Circuit Breaker Layer
เพิ่ม Global Kill-Switch Layer (Out-of-Band Control)
Mandatory Controls:
Daily hard loss cap (e.g. -3% equity)


Weekly hard loss cap (e.g. -6%)


Absolute exposure cap


Max concurrent positions cap


Data feed anomaly detection


Broker disconnection detection


Implementation:
capital_guard.py ทำงานนอก strategy loop
ถ้า trigger:
→ Immediate flat
 → Lock trading until manual review
Risk veto ≠ Kill-switch
 Kill-switch เป็น Absolute Override

III. Regime Misclassification Stress Protocol
ก่อน Phase 2 ต้องทำ:
Stress Scenario Tests:
Force incorrect regime label (Bull in Bear)


Remove regime input entirely


Freeze regime state artificially


Inject delayed regime switching


Pass Criteria:
System survivability maintained
 Tail DD ไม่เกิน threshold
 QLF ไม่ collapse state oscillation
Results ต้อง log แยกจาก performance report

IV. Cross-Agent Tail Correlation Audit
เพิ่ม Tail Correlation Monitor
Metrics:
Rolling agent PnL correlation matrix


Worst 5% day overlap ratio


Tail loss synchronization score


Implementation:
tail_overlap_ratio = shared_loss_days / worst_5_percent_days
Threshold:
If overlap > 70% → Governance Alert
QLF ไม่ auto-act
 แต่ Governance Review Required

V. Out-of-Sample Governance Freeze Test
ก่อน Phase 2:
Freeze all thresholds


Freeze entropy rules


Freeze drift detection config


Freeze rating parameters


Run on unseen historical segment
ห้าม tune ระหว่าง run
Pass Criteria:
Structural metrics stable


No governance oscillation


No threshold cascade reaction



VI. Human Governance Protocol (Formalized)
เพิ่ม Governance Playbook:
If GFM > 0.7 for ≥ 5 bars:
→ Review within 48h
 → No automatic threshold change
If SDS > threshold:
→ Freeze evolution
 → Block promotion from Sandbox
If ICI rising 3 consecutive quarters:
→ Mutation budget reduced by 50%
If Tail DD breach:
→ Mandatory full architecture review
 → No new agents allowed for next cycle
Human intervention ต้อง documented
 ห้าม override silently

VII. Infrastructure & Operational Resilience Layer
ก่อน Phase 3 ต้อง implement:
Broker heartbeat monitor


Order acknowledgment validation


Duplicate order prevention


VPS failover plan


Time synchronization guard


Log integrity hash


Execution bridge ต้อง:
Stateless per order


Idempotent order submission


Confirm fill via broker acknowledgment only



VIII. Psychological Drift Guard (Owner Risk Control)
เพิ่ม Owner Discipline Clause:
เมื่อ:
Alpha underperforms 6 months
 → Evolution budget reduced (not increased)
ห้าม:
Add agents reactively


Loosen risk thresholds


Modify QLF state transitions


Evolution under drawdown = Prohibited

IX. Metric Coupling Audit
ก่อน production:
Run correlation analysis between:
ICI


GFM


SDS


Capital Utilization


If metric correlation > 0.8
 → Recalibrate weighting to prevent double counting instability

X. Phase 3 Production Gate Criteria (Strict)
ก่อน deploy real capital ต้องผ่าน:
90-day uninterrupted forward test


No emergency patch


No schema change


No threshold retune


Kill-switch test simulated successfully


Partial fill scenario tested


MRD stress passed


Tail correlation audit stable


If any fail → rollback to Phase 2

XI. Promotion Decision Rule (Tail Priority Doctrine)
If Phase 2 result:
Sharpe pass
 Tail DD fail
→ Promotion Prohibited
Hierarchy:
1️⃣ Capital survivability
 2️⃣ Tail stability
 3️⃣ Governance stability
 4️⃣ Alpha
Alpha cannot override Tail Risk


XII. Final Statement
PRX-01 ทำให้ Sovereign-Quant ไม่เพียงแต่เป็น:
Constitutional Design
แต่เป็น:
Operationally Defensible Institutional System
Architecture alone ไม่พอ
 Execution reality, infra resilience, human discipline
 ต้องถูก formalize เท่าเทียมกัน

XIII. Hierarchical Capital Allocation Amendment (HCAP-01)
สถานะ: Mandatory Patch
 ประเภท: Capital Governance Clarification
 วัตถุประสงค์: Formalize Strategy MM Proposal → QLF Adjudication → Portfolio Constraint Flow
 ไม่เปลี่ยน Authority Boundary
 เพิ่มความชัดเจนเรื่อง Capital Sovereignty

I. Capital Authority Hierarchy (Formal Definition)
ภายใต้ Sovereign Constitution:
Strategy = Risk Proposal Authority
 QLF = Epistemic Capital Modulator
 Allocator = Portfolio Constructor
 Risk = Absolute Veto
 CapitalGuard = Absolute Kill Authority
Strategy ไม่มีสิทธิ์จัดสรรทุนโดยตรง
 Strategy มีสิทธิ์ “เสนอ” Risk Intensity เท่านั้น

II. Three-Stage Capital Flow
Stage 1 — Strategy Local MM (Proposal Only)
Agent สามารถคำนวณ:
Base risk % (เช่น 1.0%)


ATR-based stop distance


Kelly fraction (local, capped)


Win-rate / R:R derived sizing suggestion


AgentSignal Extension:
proposed_risk_pct
local_kelly_fraction
volatility_context
ข้อจำกัด:
เป็น proposal เท่านั้น


ห้ามคำนวณ lot


ห้ามเข้าถึง instrument registry



Stage 2 — QLF Epistemic Adjustment
QLF ไม่กำหนดขนาด lot
 QLF ปรับ “ระดับความเชื่อมั่นของทุน”
QLF Output:
risk_factor ∈ [0,1]
state ∈ {T,F,C,S,W}
Capital Conditioning:
risk_after_qlf =
   proposed_risk_pct
   × risk_factor
Interpretation:
T → near full proposal
 C → partial risk
 S/F/W → zero
QLF ทำหน้าที่ balance:
Regime clarity


Signal conflict


Divergence D


Portfolio stress



Stage 3 — Portfolio Constraint Layer (Allocator Domain)
Allocator ต้องปรับด้วย:
1️⃣ Correlation Penalty
 2️⃣ Exposure Cap
 3️⃣ Margin Utilization Guard
 4️⃣ Portfolio VaR Cap
 5️⃣ Drawdown Throttle
Portfolio Multiplier:
portfolio_multiplier =
   min(
       correlation_cap,
       exposure_cap,
       margin_cap,
       var_cap,
       dd_throttle
   )
Final Risk:
Final Risk % =
   proposed_risk_pct
   × risk_factor
   × portfolio_multiplier
จากนั้นจึงเรียก:
calculate_risk_lot_size()

III. Volatility-Aware Overlay (Institutional Layer)
Allocator อาจใช้:
ATR-based normalization:
vol_adjustment =
   target_volatility / current_ATR
Kelly dampening:
kelly_effective =
   min(local_kelly, kelly_cap)

risk_kelly_adjusted =
   Final Risk × kelly_effective
Constraint:
 Kelly adjustment ต้องถูก cap เสมอ
 ห้าม exceed risk budget

IV. Regime-Capital Coupling Principle
Regime Confidence ต้องมีผลต่อ Capital Concentration
High regime confidence:
 → Concentrate capital
 → Allow fewer agents active
Low regime confidence:
 → Diversify capital
 → Reduce per-agent exposure
Formal Guard:
Dynamic Max Active Agents
 must scale with:
Regime confidence


Rating dispersion


Divergence stability



V. Capital Non-Democracy Law
Capital allocation is hierarchical.
Not:
 Majority vote of agents
Not:
 Average confidence
But:
 Epistemic sovereignty + portfolio constraint
Strategy = Intelligence
 QLF = Authority
 Allocator = Constructor
 Risk = Execution Firewall

VI. Tail Priority Enforcement
If conflict between:
High Kelly suggestion
 vs
 High Tail Correlation Risk
→ Tail wins
Tail stability overrides expectancy.

VII. Capital Reporting Extension
End-of-Batch ต้องเพิ่ม:
Capital Attribution Report
Per trade log:
proposed_risk
 risk_after_qlf
 portfolio_multiplier
 final_risk
 lot_final
Metrics:
Risk reduction due to regime
 Risk reduction due to correlation
 Risk reduction due to DD throttle
 Kelly contribution delta
ต้องตอบได้ว่า:
"ทุนถูกลดเพราะอะไร"

VIII. Anti-Override Clause
ห้าม:
Strategy escalate risk during drawdown
 QLF increase risk when GFM high
 Allocator bypass portfolio multiplier
 Risk override QLF state silently
ทุก layer ต้อง log capital transformation.





IX. Constitutional Clarification
Sovereign-Quant Capital Flow คือ:
signal
 → local MM proposal
 → epistemic conditioning
 → portfolio constraint
 → veto
 → execution
ไม่ใช่:
signal
 → lot
 → trade

X. Ratification Statement
HCAP-01 ทำให้ Sovereign-Quant:
Capital Sovereignty Explicit


Regime-aware Allocation Formalized


Kelly Contained


Correlation Bound


Tail Priority Enforced


Capital is not allocated by confidence alone.
 Capital is governed.

Patch Status:
 Compatible with v2.2.3 + 9JVMH + PRX-01
 Authority boundaries: Preserved
 QLF core logic: Unchanged
 Allocator scope: Clarified 



นี่คือ constitutional design
คนส่วนใหญ่ทำแค่:
 indicator → if → trade
เป้าหมายเรา(ระบบที่ทำงานแบบสถาบัน):
 signal → regime → meta-decision → exposure control → veto → execution



   
 