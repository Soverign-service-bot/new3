# Sovereign-Quant Development Roadmap

> Derived from [`ORG_DOCTRINE.md`](./ORG_DOCTRINE.md) — the single source of truth for authority boundaries, constitutional layers, and capital flow rules.

---

## Current Repository State

| Layer | File | Status |
|---|---|---|
| **Org Doctrine** | `ORG_DOCTRINE.md` | ✅ Created — master doctrine reference |
| **Type Contracts** | `core/types.py` | ✅ Canonical; `type/core.py` deprecated (re-export shim) |
| **Instrument Registry** | `core/instrument_registry.py` | 🔜 Stub (re-export) — PR#12 open: `InstrumentSpec` + `InstrumentRegistry` |
| **QLF Multiverse Simulator** | `QEFC/QLF_MULTIVERSE.py` | ✅ Proof-of-concept (Sandbox layer) |
| **Benchmark Visualization** | `QEFC/QLF_MULTIVERSE_Benchmark_Visualization.py` | ✅ Proof-of-concept (Sandbox layer) |
| **CI Pipeline** | `.github/workflows/ci.yaml` | ✅ ruff + mypy + pytest |
| **Security Scan** | `.github/workflows/security.yaml` | ✅ pip-audit on PR + weekly schedule |
| **Tests** | `tests/test_type_contracts.py` | ✅ 21 tests passing |
| **QEFC Engine** | `core/qefc_engine.py` | ❌ Not yet implemented |
| **MRD Engine** | `core/mrd_engine.py` | ❌ Not yet implemented |
| **Sovereign Allocator** | `core/sovereign_allocator.py` | ❌ Not yet implemented |
| **Risk Engine** | `core/risk_engine.py` | ❌ Not yet implemented |
| **Capital Guard** | `core/capital_guard.py` | ❌ Not yet implemented |
| **Strategy Agents** | `strategies/` | ❌ Not yet implemented |
| **Data Layer** | `data/` | ❌ Not yet implemented |
| **Simulation / Broker** | `simulation/` | ❌ Not yet implemented |

---

## Resolved Decisions (no longer open)

| Decision | Resolution |
|---|---|
| `AgentSignal.intent` canonical value | **`NEUTRAL`** — `FLAT` kept as deprecated alias, removed in PR#2 |
| State machine enum name | **`QEFCState`** — consistent with framework name |
| Type file location | **`core/types.py`** — `type/` folder kept only as shim |
| Test data source | **Synthetic fixtures** — no external OHLCV dependency in CI |
| QEFC input dimensionality | **< 10 meta-features** — frozen by v2.2.2 doctrine |
| Lot sizing authority | **Allocator only** — HCAP-01 frozen |

---

## Sprint Plan

### ✅ Sprint 0 — Foundation (Complete)

- [x] ruff lint errors fixed
- [x] mypy type errors fixed
- [x] `pyproject.toml` added (ruff + mypy + pytest config)
- [x] `requirements.txt` added
- [x] `__init__.py` added to `core/` and `type/`
- [x] `core/types.py` canonical (all contracts in one place)
- [x] `type/core.py` deprecated to re-export shim
- [x] `tests/__init__.py` added
- [x] `tests/test_type_contracts.py` — 21 tests passing
- [x] `ORG_DOCTRINE.md` created

---

### 🟡 Sprint 1 — Instrument Registry (In Progress)

> Goal: registry works; all contract types stable

- [ ] **PR#12** — `core/instrument_registry.py`: `InstrumentSpec` dataclass + `InstrumentRegistry` stub (`get`, `validate`)
- [ ] **`config/instruments.yaml`** — FX pairs, XAU, US100, SPX, DAX instrument specs
- [ ] **`core/instrument_registry.py`** — `load_from_yaml(path)` + `calc_lot_from_risk(risk_amount, sl_ticks, spec)`
- [ ] **`tests/test_instrument_registry.py`** — registry load, lookup, lot calc

---

### 🟡 Sprint 2 — Data Layer

> Goal: OHLCV data flows into `MarketSnapshot`

- [ ] **`data/data_loader.py`** — load OHLCV (CSV / Parquet)
- [ ] **`data/feature_engineer.py`** — ATR, EMA, RSI; output `ta_*` / `feat_*` fields
- [ ] **`data/qlib_pipeline.py`** — QLib factor integration with lineage + schema version lock (v2.2.2)
- [ ] **`data/factor_stability_monitor.py`** — detect silent factor drift (v2.2.2)
- [ ] **`core/snapshot_builder.py`** — assemble `MarketSnapshot` from raw data + features

---

### 🟠 Sprint 3 — QEFC Engine (Core of the System)

> Goal: QLF FSM is runnable and tested; inputs are compressed meta-features only (< 10 dims, v2.2.2)

- [ ] **`core/mrd_engine.py`** — Market Regime Detector → `RegimeInfo`
- [ ] **`core/qefc_engine.py`** — FSM: {T, C, F, S, W} × `risk_factor` × `reason_codes` × `cooldown_bars`
  - Must enforce meta-feature boundary (< 10 dims)
  - Must remain non-adaptive at runtime (v2.2.3)
- [ ] **`tests/test_qefc_engine.py`** — all 5 state transitions; boundary isolation tests

---

### 🟠 Sprint 4 — Strategy Agents

> Goal: at least one agent produces `AgentSignal` consumed by QEFC

- [ ] **`core/base_agent.py`** — abstract base; enforces no sizing, no execution
- [ ] **`strategies/trend/trend_agent.py`** — trend-following agent (start here)
- [ ] **`strategies/mean_reversion/mr_agent.py`** — mean-reversion agent
- [ ] **`core/rating_engine.py`** — dual rating (`R_mul`, `R_add`, divergence `D`); dynamic max active agents (v2.2.1)

---

### 🔴 Sprint 5 — Allocator + Risk + Capital Guard

> Goal: capital sizing, risk veto, and kill-switch all operational

- [ ] **`core/sovereign_allocator.py`** — apply `risk_factor` × `portfolio_multiplier`; correlation caps; exposure caps; margin caps; VaR; DD throttle
  - Must emit fully traceable `AllocationDecision` (HCAP-01)
- [ ] **`core/risk_engine.py`** — in-loop veto: reject / reduce / flatten
- [ ] **`core/capital_guard.py`** — out-of-band kill-switch: daily/weekly hard loss cap; broker anomaly detection (PRX-01)
- [ ] **`tests/test_allocator.py`** — anti-override tests (HCAP-01 invariants)
- [ ] **`tests/test_risk_engine.py`** — kill-switch, drawdown guard

---

### 🔴 Sprint 6 — Simulation & Backtest

> Goal: end-to-end bar-by-bar test with realistic microstructure (PRX-01)

- [ ] **`simulation/virtual_broker.py`** — dynamic spread, slippage, partial fill, latency, gap simulation
- [ ] **`simulation/portfolio.py`** — equity, margin, drawdown state
- [ ] **`core/orchestrator.py`** — bar-by-bar driver; logs `config_hash`, `code_commit`, all version fields (reproducibility requirement)
- [ ] **`main_backtest.py`** — entry point
- [ ] **`tests/test_e2e_backtest.py`** — determinism check; regime stress protocol (PRX-01)

---

## Implementation Order (Doctrine-Derived)

```
ORG_DOCTRINE.md  (constitution — done)
  → core/types.py  (contracts — done)
  → core/instrument_registry.py  (Sprint 1 — PR#12)
  → config/instruments.yaml
  → data/data_loader.py + feature_engineer.py + snapshot_builder.py  (Sprint 2)
  → core/mrd_engine.py + core/qefc_engine.py  (Sprint 3 — THE CORE)
  → strategies/ + core/rating_engine.py  (Sprint 4)
  → core/sovereign_allocator.py + risk_engine.py + capital_guard.py  (Sprint 5)
  → simulation/ + orchestrator + main_backtest  (Sprint 6)
```

QEFC engine is the **architectural core**. Every downstream layer depends on stable type contracts and a working QEFC FSM.
