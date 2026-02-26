# Sovereign-Quant Architecture

## 1. System Identity
Sovereign-Quant is a **Constitutional Capital Governance System**.

It is **not**:
- an EA
- a single-strategy bot
- an indicator stack
- an ML wrapper

It is:
- a layered decision-about-decision architecture
- a capital governance constitution
- a system that separates signal generation from capital authority

---

## 2. Core Principle of Separation
### Authority hierarchy
1. **Strategy Agents** → generate signals only
2. **MRD (Market Regime Detector)** → report market condition only
3. **QEFC** → epistemic meta-decision (T/F/C/S/W)
4. **Allocator** → construct portfolio and position sizing
5. **Risk Engine** → absolute veto
6. **Capital Guard** → absolute kill-switch (out-of-band)
7. **Broker** → dumb execution only

### Hard laws
- Strategy cannot size positions
- Strategy cannot override risk
- Strategy cannot execute orders
- MRD cannot directly gate execution
- QEFC cannot bypass Risk
- Allocator must respect QEFC `risk_factor`
- Execution must remain dumb

---

## 3. Layer Architecture
Market Data  
→ Data + Features Layer (incl. QLib offline factors)  
→ Snapshot Builder  
→ Strategy Agents  
→ MRD  
→ QEFC Meta Engine  
→ Sovereign Allocator  
→ Risk Engine (Veto)  
→ Capital Guard (Kill)  
→ Virtual Broker / MT5 Bridge  
→ Performance & Governance Reporting

---

## 4. Constitutional Layers
### 4.1 Immutable Core Layer (Frozen)
- Contracts (`core/types.py`)
- QEFC FSM logic
- Risk veto structure
- Allocation decision contract
- Snapshot schema contract
- Dimensional compression law (<10 QEFC meta dimensions)
- Authority boundary enforcement

### 4.2 Governed Extension Layer (Regulated)
May evolve via review + ablation:
- Agents
- Factor pool
- MRD model
- RL models
- Rating parameters
- Strategy weights

### 4.3 Sandbox Layer (Isolated)
Research-only:
- new agents
- new factors
- new compression ideas
- adaptive experiments

No capital authority. No execution path access.

---

## 5. Core Contracts
### 5.1 MarketSnapshot
Must include at least:
- timestamp
- symbol
- OHLC price
- history window
- features (`ta_*`, `feat_*`, `meta_*`)
- portfolio state
- instrument spec
- factor lineage fields (version/hash)

### 5.2 AgentSignal
Must include:
- `agent_name`
- `symbol`
- `intent` (LONG/SHORT/NEUTRAL)
- `confidence`
- `invalidation_price` (optional)
- `tags`
- `metadata`

Optional proposal-only fields:
- `proposed_risk_pct`
- `local_kelly_fraction`
- `volatility_context`

### 5.3 RegimeInfo
- `regime_label`
- `regime_confidence`
- `session_state`
- `volatility_flags`

### 5.4 QEFCDecision
- `state` ∈ {T, F, C, S, W}
- `risk_factor` ∈ [0,1]
- `reason_codes`
- `cooldown_bars`

### 5.5 AllocationDecision
- `action`
- `orders`
- `target_exposure`
- `notes`

### 5.6 RiskVerdict
- `approved`
- `modified_decision` (optional)
- `kill_switch`
- `reason_codes`

---

## 6. Capital Flow Constitution (HCAP-01)
Capital flow is hierarchical, not democratic:

Signal  
→ Strategy local MM proposal (proposal only)  
→ QEFC epistemic conditioning (`risk_factor`)  
→ Allocator portfolio constraints (correlation / exposure / margin / VaR / DD throttle)  
→ Risk veto  
→ Capital Guard kill-switch  
→ Execution

### Final risk formula (conceptual)
`final_risk = proposed_risk_pct × qefc_risk_factor × portfolio_multiplier`

Strategy confidence alone must never allocate capital.

---

## 7. QEFC Boundary Rules
QEFC is a finite state machine and must remain small, auditable, and non-adaptive in runtime.

### QEFC may read
- compressed meta-features only (<10 dims)
- signal consensus/conflict summaries
- regime confidence
- volatility anomaly flags
- portfolio stress state
- rating divergence summaries

### QEFC may not read
- raw feature vectors
- correlation matrices
- broker execution internals
- direct order books for execution decisions

---

## 8. Risk and Capital Guard
### Risk Engine (in-loop veto)
Can:
- reject orders
- reduce exposure
- flatten positions
- trigger emergency conditions

### Capital Guard (out-of-band)
Can:
- enforce daily/weekly hard loss caps
- detect broker/data-feed anomalies
- hard-lock trading pending manual review

Capital Guard is above normal loop risk controls.

---

## 9. Reproducibility and Version Lock
Each run must log:
- `config_hash`
- `code_commit`
- factor version / schema version
- model versions
- QEFC rules version
- allocator exploration config
- execution model version

Reproducibility is a constitutional requirement.

---

## 10. Governance Metrics
Advisory metrics (non-execution authority):
- ICI (Information Complexity Index)
- GFM (Governance Friction Metric)
- SDS (Structural Drift Score)
- tail overlap / tail correlation diagnostics

These metrics can trigger review, not automatic capital decisions.

---

## 11. Promotion Model
All changes follow:

Sandbox → Evaluation → Governance Review → Extension Layer → Integration (`dev`) → Protected Promotion (`main`)

No direct mutation of frozen constitutional core without explicit major revision.

---

## 12. Repository Ownership Intent
Protected constitutional files (existing and planned) require strict review:
- `core/types.py`
- `core/QEFC_engine.py` (planned module; not yet implemented)
- `core/sovereign_allocator.py` (planned module; not yet implemented)
- `core/risk_engine.py` (planned module; not yet implemented)
- `.github/*`
- doctrine and architecture docs

This repository is designed for human + AI collaboration under constitutional constraints.