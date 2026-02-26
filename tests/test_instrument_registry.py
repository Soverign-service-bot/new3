"""Tests for InstrumentRegistry and InstrumentSpec."""

import pytest

from core.instrument_registry import InstrumentRegistry, InstrumentSpec


class TestInstrumentRegistryLoading:
    """Test YAML loading and basic registry operations."""

    def test_load_yaml_and_instantiate_registry(self) -> None:
        """Test that registry loads YAML config without errors."""
        registry = InstrumentRegistry()
        assert registry is not None
        assert len(registry.list_symbols()) >= 3

    def test_list_symbols_returns_all_instruments(self) -> None:
        """Test that list_symbols returns expected instruments."""
        registry = InstrumentRegistry()
        symbols = registry.list_symbols()

        assert "XAUUSD" in symbols
        assert "EURUSD" in symbols
        assert "US100" in symbols

    def test_get_existing_symbol_returns_spec(self) -> None:
        """Test that get() returns InstrumentSpec for valid symbol."""
        registry = InstrumentRegistry()
        spec = registry.get("XAUUSD")

        assert isinstance(spec, InstrumentSpec)
        assert spec.symbol == "XAUUSD"
        assert spec.tick_size > 0
        assert spec.point_value > 0
        assert spec.contract_size > 0
        assert spec.min_lot > 0
        assert spec.max_lot > 0
        assert spec.lot_step > 0

    def test_get_nonexistent_symbol_raises_key_error(self) -> None:
        """Test that get() raises KeyError for invalid symbol."""
        registry = InstrumentRegistry()

        with pytest.raises(KeyError) as exc_info:
            registry.get("INVALID")

        assert "INVALID" in str(exc_info.value)
        assert "not found" in str(exc_info.value).lower()

    def test_instrument_spec_fields_match_yaml(self) -> None:
        """Test that InstrumentSpec fields match YAML configuration."""
        registry = InstrumentRegistry()

        # Test XAUUSD
        xau = registry.get("XAUUSD")
        assert xau.symbol == "XAUUSD"
        assert xau.tick_size == 0.01
        assert xau.point_value == 100.0
        assert xau.contract_size == 100
        assert xau.min_lot == 0.01
        assert xau.max_lot == 100.0
        assert xau.lot_step == 0.01

        # Test EURUSD
        eur = registry.get("EURUSD")
        assert eur.symbol == "EURUSD"
        assert eur.tick_size == 0.00001
        assert eur.point_value == 10.0
        assert eur.min_lot == 0.01
        assert eur.max_lot == 100.0

        # Test US100
        us100 = registry.get("US100")
        assert us100.symbol == "US100"
        assert us100.min_lot == 0.1
        assert us100.max_lot == 50.0
        assert us100.lot_step == 0.1


class TestCalcLotFromRisk:
    """Test lot sizing calculation logic."""

    def test_normal_sizing_within_bounds(self) -> None:
        """Test normal lot calculation without clamping."""
        registry = InstrumentRegistry()

        # Example: Risk $100, SL 50 points, point_value 10.0
        # risk_per_1_lot = 50 * 10 = 500
        # raw_lot = 100 / 500 = 0.2
        # quantized (lot_step=0.01): 0.2 (already aligned)
        # clamped: 0.2 (within [0.01, 100.0])
        lot = registry.calc_lot_from_risk(risk_amount_usd=100.0, sl_distance_points=50.0, symbol="EURUSD")
        assert lot == 0.2

        # Another test with XAUUSD
        # Risk $1000, SL 10 points, point_value 100.0
        # risk_per_1_lot = 10 * 100 = 1000
        # raw_lot = 1000 / 1000 = 1.0
        lot = registry.calc_lot_from_risk(risk_amount_usd=1000.0, sl_distance_points=10.0, symbol="XAUUSD")
        assert lot == 1.0

    def test_clamp_to_min_lot(self) -> None:
        """Test that result is clamped to min_lot when calculated size is too small."""
        registry = InstrumentRegistry()

        # Example: Risk $0.10, SL 100 points, point_value 100.0
        # risk_per_1_lot = 100 * 100 = 10000
        # raw_lot = 0.10 / 10000 = 0.00001
        # quantized: 0.0 (floor)
        # clamped: 0.01 (min_lot)
        lot = registry.calc_lot_from_risk(risk_amount_usd=0.10, sl_distance_points=100.0, symbol="XAUUSD")
        assert lot == 0.01  # min_lot for XAUUSD

        # Test with US100 (min_lot = 0.1)
        lot = registry.calc_lot_from_risk(risk_amount_usd=0.50, sl_distance_points=1000.0, symbol="US100")
        assert lot == 0.1  # min_lot for US100

    def test_clamp_to_max_lot(self) -> None:
        """Test that result is clamped to max_lot when calculated size is too large."""
        registry = InstrumentRegistry()

        # Example: Risk $100000, SL 1 point, point_value 10.0
        # risk_per_1_lot = 1 * 10 = 10
        # raw_lot = 100000 / 10 = 10000
        # quantized: 10000.0
        # clamped: 100.0 (max_lot for EURUSD)
        lot = registry.calc_lot_from_risk(risk_amount_usd=100000.0, sl_distance_points=1.0, symbol="EURUSD")
        assert lot == 100.0  # max_lot for EURUSD

        # Test with US100 (max_lot = 50.0)
        lot = registry.calc_lot_from_risk(risk_amount_usd=50000.0, sl_distance_points=1.0, symbol="US100")
        assert lot == 50.0  # max_lot for US100

    def test_quantization_to_lot_step(self) -> None:
        """Test that result is floored to nearest lot_step."""
        registry = InstrumentRegistry()

        # Example: Risk $100, SL 33 points, point_value 10.0, lot_step 0.01
        # risk_per_1_lot = 33 * 10 = 330
        # raw_lot = 100 / 330 = 0.303030...
        # quantized: floor(0.303030 / 0.01) * 0.01 = floor(30.303) * 0.01 = 30 * 0.01 = 0.30
        lot = registry.calc_lot_from_risk(risk_amount_usd=100.0, sl_distance_points=33.0, symbol="EURUSD")
        assert lot == pytest.approx(0.30, abs=1e-9)

        # Test with US100 (lot_step = 0.1)
        # Risk $100, SL 7 points, point_value 10.0
        # risk_per_1_lot = 7 * 10 = 70
        # raw_lot = 100 / 70 = 1.428571...
        # quantized: floor(1.428571 / 0.1) * 0.1 = floor(14.28571) * 0.1 = 14 * 0.1 = 1.4
        lot = registry.calc_lot_from_risk(risk_amount_usd=100.0, sl_distance_points=7.0, symbol="US100")
        assert lot == pytest.approx(1.4, abs=1e-9)

        # Edge case: result just below step boundary
        # Risk $99, SL 33 points, point_value 10.0
        # raw_lot = 99 / 330 = 0.3
        # quantized: 0.3 (already aligned)
        lot = registry.calc_lot_from_risk(risk_amount_usd=99.0, sl_distance_points=33.0, symbol="EURUSD")
        assert lot == pytest.approx(0.30, abs=1e-9)

    def test_invalid_risk_amount_raises_value_error(self) -> None:
        """Test that negative or zero risk_amount raises ValueError."""
        registry = InstrumentRegistry()

        with pytest.raises(ValueError) as exc_info:
            registry.calc_lot_from_risk(risk_amount_usd=-100.0, sl_distance_points=50.0, symbol="EURUSD")
        assert "risk_amount_usd must be > 0" in str(exc_info.value)

        with pytest.raises(ValueError) as exc_info:
            registry.calc_lot_from_risk(risk_amount_usd=0.0, sl_distance_points=50.0, symbol="EURUSD")
        assert "risk_amount_usd must be > 0" in str(exc_info.value)

    def test_invalid_sl_distance_raises_value_error(self) -> None:
        """Test that negative or zero sl_distance raises ValueError."""
        registry = InstrumentRegistry()

        with pytest.raises(ValueError) as exc_info:
            registry.calc_lot_from_risk(risk_amount_usd=100.0, sl_distance_points=-50.0, symbol="EURUSD")
        assert "sl_distance_points must be > 0" in str(exc_info.value)

        with pytest.raises(ValueError) as exc_info:
            registry.calc_lot_from_risk(risk_amount_usd=100.0, sl_distance_points=0.0, symbol="EURUSD")
        assert "sl_distance_points must be > 0" in str(exc_info.value)

    def test_invalid_symbol_raises_key_error(self) -> None:
        """Test that invalid symbol raises KeyError."""
        registry = InstrumentRegistry()

        with pytest.raises(KeyError) as exc_info:
            registry.calc_lot_from_risk(risk_amount_usd=100.0, sl_distance_points=50.0, symbol="INVALID_SYMBOL")
        assert "INVALID_SYMBOL" in str(exc_info.value)


class TestInstrumentSpecImmutability:
    """Test that InstrumentSpec is properly immutable."""

    def test_instrument_spec_is_frozen(self) -> None:
        """Test that InstrumentSpec fields cannot be modified."""
        registry = InstrumentRegistry()
        spec = registry.get("XAUUSD")

        with pytest.raises(Exception):  # FrozenInstanceError or AttributeError
            spec.symbol = "MODIFIED"  # type: ignore

        with pytest.raises(Exception):
            spec.min_lot = 999.0  # type: ignore
