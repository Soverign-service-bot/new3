# Sovereign-Quant Organizational Doctrine

**Version:** 2.2 + HCAP-01  
**Status:** Ratified  
**Authority:** Immutable Core — requires constitutional-level review to amend

---

## 1. System Identity

Sovereign-Quant is an **Autonomous Capital Governance System**.

It is **not**:
- an Expert Advisor (EA)
- a single-strategy bot
- an indicator stack
- an ML wrapper

It is:
- a layered decision-about-decision architecture
- a capital governance constitution
- a system that separates signal generation from capital authority

> *Core principle: Strategy thinks. Sovereign decides. Risk vetoes. Broker executes.*

---

## 2. Authority Hierarchy (Hard Laws)

The authority chain is strictly hierarchical and non-democratic:

| # | Layer | Role | Authority |
|---|---|---|---|
| 1 | **Strategy Agents** | Generate directional signals only | Propose only |
| 2 | **Market Regime Detector (MRD)** | Report market condition only | Inform only |
| 3 | **QEFC Meta Engine** | Epistemic adjudication (T/C/F/S/W) | Modulate risk_factor |
| 4 | **Sovereign Allocator** | Portfolio construction + position sizing | Constrain capital |
| 5 | **Risk Engine** | In-loop veto authority | Hard reject / reduce |
| 6 | **Capital Guard** | Out-of-band kill-switch | Absolute override |
| 7 | **Broker** | Dumb execution only | None |

### Hard Laws (inviolable)

- Strategy **cannot** size positions
- Strategy **cannot** override risk
- Strategy **cannot** execute orders directly
- MRD **cannot** gate execution directly
- QEFC **cannot** bypass Risk Engine
- Allocator **must** respect QEFC `risk_factor`
- Capital Guard **supersedes** all in-loop controls
- Execution **must** remain dumb

---

## 3. Quaternary Epistemic Control Framework (QEFC)

### 3.1 QLF Truth States

The QEFC finite state machine operates on five states (extended from the four-value QLF):

| State | Symbol | Meaning |
|---|---|---|
| True | `T` | High conviction; positive epistemic outcome |
| Contradictory | `C` | Mixed or conflicting evidence |
| False | `F` | Invalid signal; noise or negative outcome |
| Suppressed | `S` | Externally blocked; system-level inhibit |
| Waiting | `W` | Insufficient confirmation; hold state |

### 3.2 QEFC Necessary Conditions

A system attains Quaternary status only if:

- **N1. Irreversibility** — the Withdrawal/Suppressed state cannot be reversed by the Inference Engine
- **N2. Asymmetric Authority** — the Inference Engine has no write-access to the Supervisor's state
- **N3. Temporal Decoupling** — the Supervisor operates on a separate clock domain or event-trigger

### 3.3 QEFC Boundary Rules

**QEFC may read:**
- Compressed meta-features only (`< 10` dimensions)
- Signal consensus / conflict summaries
- Regime confidence
- Volatility anomaly flags
- Portfolio stress state
- Rating divergence summaries

**QEFC may not read:**
- Raw feature vectors
- Correlation matrices
- Broker execution internals
- Order books for execution decisions

---

## 4. Capital Flow Constitution (HCAP-01)

Capital flows through three mandatory stages — never bypassed, never reversed:

```
Signal
  → Strategy local MM proposal   (proposal only — risk %, not lot size)
  → QEFC epistemic conditioning  (risk_factor ∈ [0,1])
  → Allocator portfolio constraints (correlation / exposure / margin / VaR / DD throttle)
  → Risk veto
  → Capital Guard kill-switch
  → Execution
```

### Final Risk Formula

```
final_risk = proposed_risk_pct × qefc_risk_factor × portfolio_multiplier
```

**Key invariants:**
- Strategy confidence alone **must never** allocate capital
- Tail stability **overrides** Kelly / aggressive expectancy
- Lot sizing **belongs exclusively** to the Allocator layer
- Correlation caps **belong exclusively** to the portfolio layer

---

## 5. Constitutional Layers

### 5.1 Immutable Core (Frozen — requires constitutional review to change)

| Component | Status |
|---|---|
| Authority boundaries | ✅ Frozen |
| QEFC FSM role and dimensional rule | ✅ Frozen |
| Risk veto supremacy | ✅ Frozen |
| Capital Guard absolute kill role | ✅ Frozen |
| Contract semantics in `core/types.py` (breaking changes) | ✅ Frozen |
| Broker dumb-execution doctrine | ✅ Frozen |
| HCAP-01 capital flow constitution | ✅ Frozen |

### 5.2 Governed Extension Layer (Regulated — requires review + ablation)

- Strategy agents and signal logic
- Factor pool (QLib, TA indicators)
- MRD model
- RL models (FinRL)
- Rating parameters (`R_mul`, `R_add`, divergence `D`)
- Strategy weights and allocation thresholds
- Reporting dashboards

### 5.3 Sandbox Layer (Isolated — no capital authority, no execution path)

- New agents under research
- New factors under evaluation
- New QEFC compression ideas
- Adaptive / RL experiments
- Multiverse logic research (`QEFC/` directory)

No Sandbox artefact may gain capital authority without explicit promotion through the Governed Extension Layer.

---

## 6. Core Data Contracts (`core/types.py`)

All layers communicate exclusively through these immutable frozen dataclasses:

| Contract | Layer | Key Fields |
|---|---|---|
| `AgentSignal` | Strategy → QEFC | `intent`, `confidence`, `proposed_risk_pct`, `invalidation_price` |
| `RegimeInfo` | MRD → QEFC | `regime_label`, `confidence`, `entropy_score` |
| `QEFCDecision` | QEFC → Allocator | `state` ∈ {T,C,F,S,W}, `risk_factor`, `reason_codes`, `cooldown_bars` |
| `AllocationDecision` | Allocator → Risk | `action`, `proposed_risk_pct`, `risk_after_QEFC`, `portfolio_multiplier`, `final_risk_pct`, `orders` |
| `OrderIntent` | Allocator → Broker | `symbol`, `side`, `quantity`, `risk_pct_used` |
| `RiskVerdict` | Risk → Broker | `approved`, `reason`, `adjusted_quantity` |
| `MarketSnapshot` | Data → All | `symbol`, `price`, `bid`, `ask`, `volatility` |

**`SignalIntent` canonical values:** `LONG`, `SHORT`, `NEUTRAL`  
(`FLAT` is a deprecated alias — will be removed in PR#2)

---

## 7. Governance Amendments (Ratified)

| ID | Name | Key Change |
|---|---|---|
| v2.2 | Unified Deployable Blueprint | Formalized six-layer separation |
| v2.2.1 | Dual Rating & Allocator Sovereignty | Mortal Shadow doctrine; `R_mul`/`R_add`/`D`; dynamic max active agents |
| v2.2.2 | Stability & Dimensional Control | QEFC < 10 dims; QLib lineage; FinRL schema guard; ICI/GFM metrics |
| v2.2.3 + 9JVMH | Constitutional Evolution Control | Mutation budget; stability lock; SDS; identity preservation |
| PRX-01 | Production Readiness & Anti-Fragility | CapitalGuard out-of-band; microstructure simulation; tail correlation audit |
| HCAP-01 | Hierarchical Capital Allocation | Three-stage capital flow; lot sizing belongs to Allocator only |

---

## 8. Reproducibility Requirements

Every run **must** log:
- `config_hash`
- `code_commit`
- Factor version / schema version
- Model versions
- QEFC rules version
- Allocator exploration config
- Execution model version

Reproducibility is a **constitutional requirement**, not an advisory guideline.

---

## 9. Governance Metrics (Advisory Only — no execution authority)

| Metric | Description |
|---|---|
| ICI | Information Complexity Index |
| GFM | Governance Friction Metric |
| SDS | Structural Drift Score |
| Tail overlap / tail correlation | Tail risk diagnostics |

These metrics **can trigger review** but **cannot trigger automatic capital decisions**.

---

## 10. Promotion Model

All changes follow:

```
Sandbox → Evaluation → Governance Review → Extension Layer → Integration (dev) → Protected Promotion (main)
```

No direct mutation of Immutable Core without explicit major revision.

---

## 11. Frozen Files (require strict review before any change)

- `core/types.py`
- `core/qefc_engine.py` *(planned — not yet implemented)*
- `core/sovereign_allocator.py` *(planned — not yet implemented)*
- `core/risk_engine.py` *(planned — not yet implemented)*
- `core/capital_guard.py` *(planned — not yet implemented)*
- `.github/*`
- `ORG_DOCTRINE.md` (this file)
- `ARCHITECTURE.md`
- `docs/DOCTRINE_CHANGELOG.md`
