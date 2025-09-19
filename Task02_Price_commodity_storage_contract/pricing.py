import matplotlib.pyplot as plt 
import pandas as pd 
from pydantic import BaseModel, ValidationError, model_validator
from typing import List
from datetime import datetime
from heapq import merge
from statsmodels.tsa.statespace.sarimax import SARIMAX
from typing import Mapping

class InputData(BaseModel):
    injection_dates: List[datetime]
    withdrawal_dates: List[datetime]
    gaz_natural_prices: Mapping[datetime, float]
    gas_rate: float #the quantity that we can move per day
    max_volume: int
    storage_costs: float

    @model_validator(mode="after")
    def assert_disjoint(self):
        if len(set(self.injection_dates) & set(self.withdrawal_dates)) != 0:
            raise ValidationError("The injection and withdrawal dates have to be disjointed")


data = pd.read_csv('Nat_Gas.csv')

def preprocessing(data: pd.DataFrame) -> pd.DataFrame:
    data["Dates"] = pd.to_datetime(data["Dates"])
    data = data.set_index("Dates")

    model = SARIMAX(data["Prices"], order=(1,1,1), seasonal_order=(1,1,1,12))
    results = model.fit()
    forecast = results.get_forecast(steps=12)
    forecast_df = forecast.predicted_mean.to_frame(name="Prices")

    data = pd.concat([data, forecast_df])

    data_daily = data.resample("D").asfreq()
    data_daily["Prices"] = data_daily["Prices"].interpolate(method="linear")

    return data_daily

def pricing(data: InputData) -> float:
    '''we do the max at each step'''
    result = 0
    quantity_store = 0 

    inj = sorted(data.injection_dates)
    wdr = sorted(data.withdrawal_dates)

    it = merge(
        ((i, "inj") for i in inj), 
        ((d, "wdr") for d in wdr)
    )

    for timestep, kind in it:

        if kind == "inj":
            
            if quantity_store + data.gaz_rate < data.max_volume:
                result -= data.gaz_natural_prices[timestep] * data.gaz_rate
                quantity_store += data.gaz_rate

            else:
                result -= data.gaz_natural_prices[timestep] * (data.max_volume - quantity_store)
                quantity_store = data.max_volume

        else:

            if quantity_store > data.gaz_rate:
                result += data.gaz_natural_prices[timestep] * data.gaz_rate
                quantity_store -= data.gaz_rate
            else:
                result += data.gaz_natural_prices[timestep] * quantity_store
                quantity_store = 0


    result -= data.storage_costs # Cout de stockage

    return result


gaz_natural_prices = preprocessing(data)

