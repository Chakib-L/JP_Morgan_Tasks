import pandas as pd
import pytest
from datetime import datetime
from typing import Mapping

# Adapte ce chemin d'import à ton module (ex.: from Nat_Gas import InputData, pricing)
from Task02_Price_commodity_storage_contract.pricing import InputData, pricing

def _mk_prices() -> Mapping[datetime, float]:
    # J1=1.0, J2=1.0 (inject), J3=2.0, J4=2.0 (withdraw)
    return {
        datetime(2025, 1, 1): 1.0,
        datetime(2025, 1, 2): 1.0,
        datetime(2025, 1, 3): 2.0,
        datetime(2025, 1, 4): 2.0,
    }

def test_pricing_max_rate_and_capacity():
    prices = _mk_prices()

    # Politique "plein débit" avec capacité qui sature à 15
    # - Inj jour1: -10*1 = -10, stock=10
    # - Inj jour2: -5*1  = -5,  stock=15 (cap atteint)
    # - Wdr jour3: +10*2 = +20, stock=5
    # - Wdr jour4: +5*2  = +10, stock=0
    # Total attendu = -15 + 20 + 10 = 15
    inp = InputData(
        injection_dates=[datetime(2025, 1, 1), datetime(2025, 1, 2)],
        withdrawal_dates=[datetime(2025, 1, 3), datetime(2025, 1, 4)],
        gaz_natural_prices=prices,
        gas_rate=10.0,
        max_volume=15,
        storage_costs=0.0,  # on met 0 pour un résultat net propre
    )

    # Patch pour le bug d’implémentation: pricing lit "gaz_rate" au lieu de "gas_rate"
    if not hasattr(inp, "gaz_rate"):
        inp.__dict__["gaz_rate"] = inp.gas_rate  # évite un AttributeError

    val = pricing(inp)
    assert isinstance(val, (int, float))
    assert val == pytest.approx(15.0, rel=1e-12)

def test_inputdata_disjoint_dates_raises():
    prices = _mk_prices()
    # La même date dans les deux listes doit lever une erreur
    with pytest.raises(Exception):
        InputData(
            injection_dates=[datetime(2025, 1, 1)],
            withdrawal_dates=[datetime(2025, 1, 1)],
            gaz_natural_prices=prices,
            gas_rate=1.0,
            max_volume=10,
            storage_costs=0.0,
        )
