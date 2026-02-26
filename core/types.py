# core/types.py
"""
SOVEREIGN-QUANT CORE TYPES
Version: HCAP-01 Patched
Purpose: Formalize hierarchical capital flow
         Strategy Proposal → QEFC Modulation → Portfolio Constraint → Execution

This file contains ONLY structural contracts.
No business logic.
No allocation logic.
No QEFC logic.
No instrument logic.

Authority Boundaries:
- Strategy proposes risk
- QEFC modulates risk
- Allocator constrains risk
- Risk layer vetoes execution
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Literal, Optional

# ============================================================
# Primitive Types
# ============================================================

Symbol = str
AgentName = str


# ============================================================
# QEFC STATE MACHINE
# ============================================================


class QEFCState(str, Enum):
    """
    Quaternary Logic Framework State

    T = True (High conviction) or gain or positive outcome
    C = Contradictory (Mixed evidence)
    F = False (Invalid signal) or Loss or Negative Outcome
    S = Suppressed (Externally blocked)
    W = Waiting (Insufficient confirmation)
    """

    T = "T"
    C = "C"
    F = "F"
    S = "S"
    W = "W"


# ============================================================
# SIGNAL INTENT
# ============================================================


class SignalIntent(str, Enum):
    """
    Canonical directional intent for a strategy signal.

    LONG    = bullish position
    SHORT   = bearish position
    NEUTRAL = no directional bias (canonical; replaces FLAT)

    FLAT is kept as a deprecated alias for backward compatibility.
    TODO: will be removed in PR#2
    """

    LONG = "LONG"
    SHORT = "SHORT"
    NEUTRAL = "NEUTRAL"
    FLAT = "NEUTRAL"  # deprecated alias — will be removed in PR#2


# ============================================================
# STRATEGY LAYER
# ============================================================


@dataclass(frozen=True)
class AgentSignal:
    """
    Strategy Output Layer

    Strategy is allowed to:
    - Declare directional intent
    - Provide invalidation level
    - Propose risk percentage
    - Provide local Kelly fraction (optional)
    - Provide volatility context

    Strategy is NOT allowed to:
    - Compute lot size
    - Access portfolio state
    - Access instrument registry
    """

    agent_name: AgentName
    symbol: Symbol

    intent: Literal["LONG", "SHORT", "NEUTRAL"]
    confidence: float  # 0–1 epistemic belief
    invalidation_price: Optional[float]

    # --- HCAP-01 Extensions (Risk Proposal Only) ---
    proposed_risk_pct: Optional[float] = None
    local_kelly_fraction: Optional[float] = None
    volatility_context: Optional[Dict[str, Any]] = None

    # --- Metadata ---
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)


# ============================================================
# QEFC DECISION LAYER
# ============================================================


@dataclass(frozen=True)
class QEFCDecision:
    """
    Epistemic Adjudication Result

    risk_factor applies to:
        AgentSignal.proposed_risk_pct

    QEFC does NOT:
    - Compute lot sizes
    - Access portfolio state
    - Apply correlation caps
    """

    state: QEFCState
    risk_factor: float  # ∈ [0, 1]
    reason_codes: List[str] = field(default_factory=list)
    cooldown_bars: int = 0
    timestamp: datetime = field(default_factory=datetime.utcnow)


# ============================================================
# PORTFOLIO ALLOCATION LAYER
# ============================================================


@dataclass(frozen=True)
class AllocationDecision:
    """
    Portfolio Constructor Output

    Responsible for:
    - Applying correlation caps
    - Exposure caps
    - Margin caps
    - Drawdown throttle
    - VaR constraint

    This layer transforms:
        proposed_risk_pct
            → risk_after_QEFC
            → final_risk_pct

    Must be fully auditable.
    """

    symbol: Symbol
    action: Literal["OPEN", "CLOSE", "HOLD", "REJECT"]

    # --- Capital Trace (HCAP-01 Mandatory) ---
    proposed_risk_pct: float
    risk_after_QEFC: float
    portfolio_multiplier: float
    final_risk_pct: float

    # --- Order Intents ---
    orders: List["OrderIntent"] = field(default_factory=list)

    # --- Reporting ---
    notes: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)


# ============================================================
# EXECUTION INTENT
# ============================================================


@dataclass(frozen=True)
class OrderIntent:
    """
    Deterministic Execution Contract

    Must be reproducible from:
    - final_risk_pct
    - instrument spec
    - entry / stop

    No hidden sizing logic allowed.
    """

    symbol: Symbol
    side: Literal["BUY", "SELL"]
    quantity: float
    entry_price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None

    # --- Capital Attribution ---
    risk_pct_used: float = 0.0
    risk_source: str = "HCAP-01"

    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================
# RISK LAYER VERDICT
# ============================================================


@dataclass(frozen=True)
class RiskVerdict:
    """
    Absolute Execution Firewall

    Risk layer can:
    - Approve
    - Modify
    - Reject

    Risk overrides all prior layers.
    """

    approved: bool
    reason: Optional[str] = None
    adjusted_quantity: Optional[float] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)


# ============================================================
# MARKET SNAPSHOT (Read-Only)
# ============================================================


@dataclass(frozen=True)
class MarketSnapshot:
    """
    Immutable market data snapshot.

    No capital logic.
    No QEFC logic.
    """

    symbol: Symbol
    price: float
    bid: Optional[float] = None
    ask: Optional[float] = None
    spread: Optional[float] = None
    volatility: Optional[float] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)


# ============================================================
# REGIME INFO (Read-Only Context)
# ============================================================


@dataclass(frozen=True)
class RegimeInfo:
    """
    Market Regime Descriptor.

    Used by QEFC but not mutated by it.
    """

    regime_label: str
    confidence: float
    entropy_score: Optional[float] = None
    divergence_score: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)


# ============================================================
# END OF FILE
# ============================================================

"""
HCAP-01 Compliance Summary:

✔ Strategy proposes risk (never lot)
✔ QEFC modulates via risk_factor
✔ Portfolio applies multiplier
✔ Allocation fully traceable
✔ Execution deterministic
✔ Risk layer retains veto

Capital is governed, not guessed.
"""
