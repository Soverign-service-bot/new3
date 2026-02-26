# Doctrine Changelog

This file records constitutional and governance amendments for Sovereign-Quant and maps each amendment to implementation impact.

---

## v2.2 — Unified Deployable Blueprint
### Summary
Formalized Sovereign-Quant as a layered capital governance system with clear separation:

- Strategy (signal only)
- MRD (regime reporting)
- QEFC (meta-decision)
- Allocator (capital construction)
- Risk (veto)
- Broker (execution)

### Core constitutional identity
Decision-about-decision architecture for capital allocation.

### Implementation impact
- `core/types.py` (contracts baseline)
- `core/mrd_engine.py`
- `core/QEFC_engine.py`
- `core/sovereign_allocator.py`
- `core/risk_engine.py`
- `simulation/virtual_broker.py`
- `core/orchestrator.py`

---

## v2.2.1 — Phase-1 Governance Patch (Dual Rating & Allocator Sovereignty)
### Summary
Introduced:
- Mortal Shadow (no reset doctrine)
- Dual rating engine (`R_mul`, `R_add`, divergence `D`)
- Dynamic max active agents
- Correlation penalty explicitly in Allocator
- Deterministic allocator + controlled stochastic exploration

### Constitutional effect
Strengthened capital tournament logic while preserving authority boundaries.

### New guards
- Correlation belongs to portfolio layer only
- QEFC consumes epistemic score summaries, not correlation matrix
- Shadow remains epistemic (no allocation noise contamination)

### Implementation impact
- `core/sovereign_allocator.py`
- rating subsystem (future `core/rating_engine.py` or equivalent)
- reporting: divergence / uncertainty metrics
- tests for layer isolation

---

## v2.2.2 — Stability & Dimensional Control Patch
### Summary
Added governance hardening for:
- QLib lineage and schema guards
- FinRL entropy/behavioral stability guard
- QEFC dimensional compression enforcement
- Complexity metrics (ICI, GFM)
- Version lock and reproducibility extensions

### Constitutional effect
Prevents silent drift and dimensional explosion from contaminating the QEFC layer.

### New guards
- QEFC input remains compressed meta-features only (<10 dims)
- Factor lineage required
- RL schema mismatch must abort inference
- Complexity metrics are advisory, not execution authority

### Implementation impact
- `data/qlib_pipeline.py`
- `data/factor_stability_monitor.py` (new)
- FinRL wrapper / model registry components
- `core/QEFC_engine.py` (meta-feature boundary validation)
- reporting/dashboard modules
- schema/version logging in orchestrator/reporting

---

## v2.2.3 + 9JVMH — Constitutional Evolution Control Patch
### Summary
Formalized three permanent layers:
1. Immutable Core (frozen constitution)
2. Governed Extension (regulated evolution)
3. Sandbox (isolated mutation lab)

Added:
- mutation budget control
- stability lock period
- structural drift monitoring (SDS)
- identity preservation clause

### Constitutional effect
Allows controlled evolution without self-modifying the constitutional core.

### New guards
- no runtime mutation of core
- no shared mutable state from sandbox into core
- no adaptive QEFC
- evolution promotion must pass boundary tests + ablation

### Implementation impact
- repository governance docs and review rules
- CI/review checks (advisory + process)
- reporting/dashboard: SDS tracking
- promotion workflow definition (`dev` → `main`)

---

## PRX-01 — Production Readiness & Anti-Fragility Patch
### Summary
Added production transition safeguards:
- microstructure simulation realism
- capital circuit breaker (CapitalGuard)
- regime misclassification stress protocol
- tail correlation audit
- out-of-sample governance freeze tests
- infra resilience requirements
- owner discipline and metric coupling audit

### Constitutional effect
Bridges architecture to operational defensibility.

### New guards
- CapitalGuard is out-of-band absolute override
- production gate criteria are strict and testable
- alpha cannot override tail survivability

### Implementation impact
- `simulation/virtual_broker.py` (dynamic spread/slippage/partial fill/latency/gap)
- `core/capital_guard.py` (new)
- stress test harnesses
- reporting: tail overlap, stress outputs
- infra checks in bridge layer (future Phase 3)

---

## HCAP-01 — Hierarchical Capital Allocation Amendment
### Summary
Formalized three-stage capital flow:
1. Strategy local MM proposal (proposal only)
2. QEFC epistemic risk conditioning
3. Allocator portfolio constraints and final lot sizing

### Constitutional effect
Makes capital sovereignty explicit and non-democratic.

### New guards
- Strategy may propose risk, not size
- QEFC modulates risk intensity, not lot size
- Allocator applies correlation/exposure/margin/VaR/DD constraints
- Tail stability overrides Kelly/aggressive expectancy

### Implementation impact
- `core/types.py` (AgentSignal proposal fields)
- `core/QEFC_engine.py` (risk_factor semantics)
- `core/sovereign_allocator.py` (portfolio multipliers and final risk log)
- reporting: capital attribution section
- tests for anti-override behavior

---

## Frozen vs Extensible (Current Interpretation)
### Frozen (requires constitutional-level review)
- authority boundaries
- QEFC FSM role and dimensional rule
- Risk veto supremacy
- CapitalGuard absolute kill role
- contract semantics in `core/types.py` (breaking changes)
- broker dumb execution doctrine

### Extensible (with review + ablation)
- agents and signal logic
- factor sets
- MRD model
- RL models
- rating parameters
- reporting dashboards
- thresholds (within approved governance process)

---

## Review Note Template for Future Amendments
For every future amendment, record:

- **Patch ID / Name**
- **Status** (Draft / Ratified / Frozen)
- **Objective**
- **Constitutional effect**
- **Authority boundary impact** (if any)
- **Implementation impact** (files/modules)
- **Validation requirements**
- **Promotion constraints**