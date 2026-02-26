# core/instrument_registry.py
"""
Instrument Registry — domain object and registry stub.

InstrumentSpec is the authoritative descriptor for a tradeable instrument.
InstrumentRegistry loads specs from a YAML file and provides lookup /
validation helpers.  Full YAML loading is deferred (TODO).
"""

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Dict, Mapping, Optional

# ============================================================
# Domain Object
# ============================================================


@dataclass(frozen=True)
class InstrumentSpec:
    """
    Immutable descriptor for a single tradeable instrument.

    The set of fields is intentionally minimal and focused on core
    trading attributes. Extend this specification as sizing logic and
    related features are implemented.

    All fields — including `metadata` — are fully immutable: the
    dataclass is frozen and `metadata` is stored as a `MappingProxyType`,
    preventing both attribute re-assignment and in-place mutation of the
    mapping contents.
    """

    symbol: str
    asset_class: str  # e.g. "FX", "COMMODITY", "INDEX", "CRYPTO"
    pip_size: float
    contract_size: float
    currency: str  # denomination of contract value
    min_lot: float = 0.01
    lot_step: float = 0.01
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        # Wrap metadata in MappingProxyType to enforce full immutability.
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))


# ============================================================
# Registry Stub
# ============================================================


class InstrumentRegistry:
    """
    Loads InstrumentSpec objects from a YAML file and exposes
    symbol-keyed lookup.

    YAML loading is *not yet implemented*; calls to get() and
    validate() raise NotImplementedError until the loader is wired.
    """

    def __init__(self, yaml_path: str) -> None:
        self._yaml_path = yaml_path
        self._specs: Dict[str, InstrumentSpec] = {}
        # TODO: parse yaml_path and populate self._specs

    def get(self, symbol: str) -> InstrumentSpec:
        """Return the InstrumentSpec for *symbol*.

        Raises
        ------
        NotImplementedError
            Until the YAML loader is implemented.
        KeyError
            Once the loader is implemented, if *symbol* is unknown.
        """
        if not self._specs:
            raise NotImplementedError(
                "InstrumentRegistry YAML loader is not yet implemented. "
                f"Cannot look up '{symbol}'. "
                f"Populate self._specs from {self._yaml_path!r} first."
            )
        return self._specs[symbol]

    def validate(self) -> Optional[bool]:
        """Validate that all loaded specs are internally consistent.

        TODO: implement validation rules (pip_size > 0, lot_step > 0, …).
        """
        # TODO: implement validation
        raise NotImplementedError("InstrumentRegistry.validate() is not yet implemented.")
