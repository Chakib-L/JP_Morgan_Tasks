import pytest
from datetime import datetime
import pandas as pd

# On réimporte ta fonction et DateError ici
# tests/test_nat_gas.py
from .Nat_Gas import to_predict, DateError, data_daily

def test_date_ok():
    # Une date valide dans la plage
    date = datetime(2024, 11, 2)
    prix = to_predict(date)
    assert isinstance(prix, (int, float))

def test_date_too_early():
    # Avant la borne
    date = datetime(2020, 10, 1)
    with pytest.raises(DateError):
        to_predict(date)

def test_date_too_late():
    # Après la borne
    date = datetime(2025, 12, 1)
    with pytest.raises(DateError):
        to_predict(date)
