"""
Tests for core type contracts (core/types.py) and the instrument registry stub
(core/instrument_registry.py).

These tests verify that the immutable data contracts behave correctly,
that the QEFC/QLF state enum is complete and consistent, and that the
InstrumentRegistry stub raises the expected errors before its YAML loader
is wired up.
"""

import pytest

from core.instrument_registry import InstrumentRegistry, InstrumentSpec
from core.types import (
    AgentSignal,
    AllocationDecision,
    MarketSnapshot,
    OrderIntent,
    QEFCDecision,
    QEFCState,
    RegimeInfo,
    RiskVerdict,
    SignalIntent,
)


class TestQEFCState:
    def test_all_five_states_exist(self) -> None:
        assert QEFCState.T == "T"
        assert QEFCState.C == "C"
        assert QEFCState.F == "F"
        assert QEFCState.S == "S"
        assert QEFCState.W == "W"

    def test_states_are_strings(self) -> None:
        for state in QEFCState:
            assert isinstance(state.value, str)


class TestAgentSignal:
    def test_create_long_signal(self) -> None:
        sig = AgentSignal(
            agent_name="trend_agent",
            symbol="XAUUSD",
            intent="LONG",
            confidence=0.8,
            invalidation_price=1900.0,
            proposed_risk_pct=0.01,
        )
        assert sig.intent == "LONG"
        assert sig.confidence == 0.8
        assert sig.proposed_risk_pct == 0.01

    def test_signal_is_immutable(self) -> None:
        sig = AgentSignal(
            agent_name="trend_agent",
            symbol="XAUUSD",
            intent="SHORT",
            confidence=0.5,
            invalidation_price=2100.0,
        )
        with pytest.raises((AttributeError, TypeError)):
            sig.confidence = 1.0  # type: ignore[misc]

    def test_defaults_are_set(self) -> None:
        sig = AgentSignal(
            agent_name="mr_agent",
            symbol="EURUSD",
            intent="NEUTRAL",
            confidence=0.3,
            invalidation_price=None,
        )
        assert sig.tags == []
        assert sig.metadata == {}
        assert sig.proposed_risk_pct is None


class TestSignalIntent:
    def test_canonical_members_exist(self) -> None:
        assert SignalIntent.LONG == "LONG"
        assert SignalIntent.SHORT == "SHORT"
        assert SignalIntent.NEUTRAL == "NEUTRAL"

    def test_flat_is_deprecated_alias_for_neutral(self) -> None:
        # FLAT is a deprecated alias — will be removed in PR#2
        assert SignalIntent.FLAT == SignalIntent.NEUTRAL

    def test_neutral_is_canonical(self) -> None:
        sig = AgentSignal(
            agent_name="alias_agent",
            symbol="XAUUSD",
            intent="NEUTRAL",
            confidence=0.0,
            invalidation_price=None,
        )
        assert sig.intent == "NEUTRAL"

    def test_neutral_is_valid_intent(self) -> None:
        sig = AgentSignal(
            agent_name="test_agent",
            symbol="XAUUSD",
            intent="NEUTRAL",
            confidence=0.5,
            invalidation_price=None,
        )
        assert sig.intent == "NEUTRAL"


class TestQEFCDecision:
    def test_create_t_state(self) -> None:
        decision = QEFCDecision(state=QEFCState.T, risk_factor=1.0)
        assert decision.state == QEFCState.T
        assert decision.risk_factor == 1.0
        assert decision.cooldown_bars == 0

    def test_create_w_state_freezes(self) -> None:
        decision = QEFCDecision(
            state=QEFCState.W,
            risk_factor=0.0,
            reason_codes=["kill_switch"],
            cooldown_bars=10,
        )
        assert decision.risk_factor == 0.0
        assert "kill_switch" in decision.reason_codes


class TestMarketSnapshot:
    def test_create_minimal_snapshot(self) -> None:
        snap = MarketSnapshot(symbol="XAUUSD", price=1950.0)
        assert snap.symbol == "XAUUSD"
        assert snap.price == 1950.0
        assert snap.bid is None

    def test_snapshot_is_immutable(self) -> None:
        snap = MarketSnapshot(symbol="EURUSD", price=1.0850)
        with pytest.raises((AttributeError, TypeError)):
            snap.price = 1.0860  # type: ignore[misc]


class TestOrderIntent:
    def test_create_buy_order(self) -> None:
        order = OrderIntent(
            symbol="XAUUSD",
            side="BUY",
            quantity=0.1,
            entry_price=1950.0,
            stop_loss=1930.0,
            risk_pct_used=0.01,
        )
        assert order.side == "BUY"
        assert order.risk_source == "HCAP-01"

    def test_create_sell_order(self) -> None:
        order = OrderIntent(symbol="EURUSD", side="SELL", quantity=0.05)
        assert order.quantity == 0.05


class TestAllocationDecision:
    def test_create_open_decision(self) -> None:
        order = OrderIntent(symbol="XAUUSD", side="BUY", quantity=0.1)
        decision = AllocationDecision(
            symbol="XAUUSD",
            action="OPEN",
            proposed_risk_pct=0.01,
            risk_after_QEFC=0.01,
            portfolio_multiplier=0.8,
            final_risk_pct=0.008,
            orders=[order],
        )
        assert decision.action == "OPEN"
        assert len(decision.orders) == 1
        assert decision.final_risk_pct == 0.008

    def test_create_reject_decision(self) -> None:
        decision = AllocationDecision(
            symbol="US100",
            action="REJECT",
            proposed_risk_pct=0.01,
            risk_after_QEFC=0.0,
            portfolio_multiplier=0.0,
            final_risk_pct=0.0,
            notes="QLF state=F: toxic regime",
        )
        assert decision.action == "REJECT"


class TestRiskVerdict:
    def test_approved(self) -> None:
        v = RiskVerdict(approved=True)
        assert v.approved is True
        assert v.adjusted_quantity is None

    def test_rejected_with_reason(self) -> None:
        v = RiskVerdict(
            approved=False,
            reason="max drawdown exceeded",
            adjusted_quantity=0.0,
        )
        assert v.approved is False
        assert v.reason == "max drawdown exceeded"


class TestRegimeInfo:
    def test_create_trend_regime(self) -> None:
        r = RegimeInfo(regime_label="TREND_RUN", confidence=0.85)
        assert r.regime_label == "TREND_RUN"
        assert r.entropy_score is None


class TestInstrumentSpec:
    def test_create_commodity_spec(self) -> None:
        spec = InstrumentSpec(
            symbol="XAUUSD",
            asset_class="COMMODITY",
            pip_size=0.01,
            contract_size=100.0,
            currency="USD",
        )
        assert spec.symbol == "XAUUSD"
        assert spec.min_lot == 0.01
        assert spec.metadata == {}

    def test_spec_is_immutable(self) -> None:
        spec = InstrumentSpec(
            symbol="EURUSD",
            asset_class="FX",
            pip_size=0.0001,
            contract_size=100_000.0,
            currency="USD",
        )
        with pytest.raises((AttributeError, TypeError)):
            spec.pip_size = 0.001  # type: ignore[misc]

    def test_metadata_is_immutable(self) -> None:
        """metadata is stored as MappingProxyType — contents cannot be mutated."""
        spec = InstrumentSpec(
            symbol="GBPUSD",
            asset_class="FX",
            pip_size=0.0001,
            contract_size=100_000.0,
            currency="USD",
            metadata={"source": "initial"},
        )
        with pytest.raises(TypeError):
            spec.metadata["source"] = "updated"  # type: ignore[index]


class TestInstrumentRegistry:
    def test_get_raises_not_implemented(self) -> None:
        registry = InstrumentRegistry(yaml_path="instruments.yaml")
        with pytest.raises(NotImplementedError):
            registry.get("XAUUSD")

    def test_validate_raises_not_implemented(self) -> None:
        registry = InstrumentRegistry(yaml_path="instruments.yaml")
        with pytest.raises(NotImplementedError):
            registry.validate()


class TestContractInstantiation:
    def test_all_contracts_instantiate(self) -> None:
        sig = AgentSignal(agent_name="a", symbol="S", intent="NEUTRAL", confidence=1.0, invalidation_price=None)
        assert sig.agent_name == "a"
        decision = QEFCDecision(state=QEFCState.T, risk_factor=1.0)
        assert decision.state == QEFCState.T
        alloc = AllocationDecision(
            symbol="S",
            action="OPEN",
            proposed_risk_pct=0.01,
            risk_after_QEFC=0.01,
            portfolio_multiplier=1.0,
            final_risk_pct=0.01,
        )
        assert alloc.action == "OPEN"
        order = OrderIntent(symbol="S", side="BUY", quantity=1.0)
        assert order.side == "BUY"
        snap = MarketSnapshot(symbol="S", price=1.0)
        assert snap.symbol == "S"
        verdict = RiskVerdict(approved=True)
        assert verdict.approved is True
        regime = RegimeInfo(regime_label="TREND", confidence=0.9)
        assert regime.regime_label == "TREND"
