# core/instrument_registry.py
"""
Instrument Registry — domain object and registry.

InstrumentSpec is the authoritative descriptor for a tradeable instrument.
InstrumentRegistry loads specs from a YAML file and provides lookup,
sizing logic, and validation helpers.
"""

import math
from dataclasses import dataclass
from pathlib import Path
from typing import Dict

import yaml

# ============================================================
# Domain Object
# ============================================================


@dataclass(frozen=True)
class InstrumentSpec:
    """
    Immutable descriptor for a single tradeable instrument.

    Fields are focused on core trading attributes required for
    position sizing and risk management.
    """

    symbol: str
    tick_size: float
    point_value: float
    contract_size: float
    min_lot: float
    max_lot: float
    lot_step: float


# ============================================================
# Registry
# ============================================================


class InstrumentRegistry:
    """
    Loads InstrumentSpec objects from a YAML file and exposes
    symbol-keyed lookup and position sizing logic.
    """

    def __init__(self, config_path: str = "config/instruments.yaml") -> None:
        """Initialize registry and load instrument specs from YAML.

        Args:
            config_path: Path to YAML config file (default: config/instruments.yaml)

        Raises:
            FileNotFoundError: If config file does not exist
            yaml.YAMLError: If config file is invalid YAML
            KeyError: If required fields are missing in YAML
        """
        self._config_path = config_path
        self._specs: Dict[str, InstrumentSpec] = {}
        self._load_yaml(config_path)

    def _load_yaml(self, config_path: str) -> None:
        """Load instrument specifications from YAML file.

        Args:
            config_path: Path to YAML config file

        Raises:
            FileNotFoundError: If config file does not exist
            yaml.YAMLError: If config file is invalid YAML
            KeyError: If required fields are missing
        """
        path = Path(config_path)
        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        instruments = data.get("instruments", {})
        for symbol, spec_data in instruments.items():
            self._specs[symbol] = InstrumentSpec(**spec_data)

    def get(self, symbol: str) -> InstrumentSpec:
        """Return the InstrumentSpec for symbol.

        Args:
            symbol: Instrument symbol (e.g., "XAUUSD")

        Returns:
            InstrumentSpec for the given symbol

        Raises:
            KeyError: If symbol is not found in registry
        """
        if symbol not in self._specs:
            raise KeyError(f"Instrument '{symbol}' not found in registry")
        return self._specs[symbol]

    def list_symbols(self) -> list[str]:
        """Return list of all loaded instrument symbols.

        Returns:
            List of symbol names
        """
        return list(self._specs.keys())

    def calc_lot_from_risk(
        self,
        risk_amount_usd: float,
        sl_distance_points: float,
        symbol: str,
    ) -> float:
        """Calculate position size in lots based on risk parameters.

        This method implements deterministic lot sizing with conservative
        floor rounding and strict min/max/step enforcement.

        Algorithm:
            1. Validate inputs (risk > 0, sl_distance > 0, symbol exists)
            2. Calculate risk per 1 lot: sl_distance * point_value
            3. Calculate raw lot size: risk_amount / risk_per_1_lot
            4. Quantize to lot_step using floor (conservative)
            5. Clamp to [min_lot, max_lot]

        Args:
            risk_amount_usd: Risk amount in USD (must be > 0)
            sl_distance_points: Stop loss distance in points (must be > 0)
            symbol: Instrument symbol

        Returns:
            Position size in lots (quantized to lot_step, clamped to min/max)

        Raises:
            ValueError: If risk_amount_usd <= 0 or sl_distance_points <= 0
            KeyError: If symbol is not found in registry
        """
        # Validate inputs
        if risk_amount_usd <= 0:
            raise ValueError(f"risk_amount_usd must be > 0, got {risk_amount_usd}")
        if sl_distance_points <= 0:
            raise ValueError(f"sl_distance_points must be > 0, got {sl_distance_points}")

        # Get instrument spec (raises KeyError if not found)
        spec = self.get(symbol)

        # Calculate risk per 1 lot
        risk_per_1_lot = sl_distance_points * spec.point_value

        # Calculate raw lot size
        raw_lot = risk_amount_usd / risk_per_1_lot

        # Quantize to lot_step (floor for conservative sizing)
        quantized_lot = math.floor(raw_lot / spec.lot_step) * spec.lot_step

        # Clamp to [min_lot, max_lot]
        final_lot = max(spec.min_lot, min(quantized_lot, spec.max_lot))

        return final_lot
