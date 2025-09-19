import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.statespace.sarimax import SARIMAX

from datetime import datetime
from pydantic import BaseModel

data = pd.read_csv('Nat_Gas.csv')

data["Dates"] = pd.to_datetime(data["Dates"])
data = data.set_index("Dates")

model = SARIMAX(data["Prices"], order=(1,1,1), seasonal_order=(1,1,1,12))
results = model.fit()
forecast = results.get_forecast(steps=12)
forecast_df = forecast.predicted_mean.to_frame(name="Prices")

data = pd.concat([data, forecast_df])

data_daily = data.resample("D").asfreq()
data_daily["Prices"] = data_daily["Prices"].interpolate(method="linear")

class DateInput(BaseModel):
    date: datetime

class DateError(Exception):
    """Exception levée pour indiquer une erreur liée aux dates."""
    def __init__(self, message: str):
        super().__init__(message)

def to_predict(date: DateInput) -> float: 
    '''
    Input: a string that gives a date (format:"2025-08-31") from 30th October 2020 to 30th September 2025
    Output: the price
    '''

    start = datetime(2020, 10, 31)
    end = datetime(2025, 9, 30)

    if date < start or date > end:
        raise DateError(f"The date {date} is not included between {start} and {end}")
    else:
        return data_daily.loc[date, "Prices"]
    

    


def test_graph():
    # bornes (elles doivent être compatibles avec to_predict)
    start = datetime(2020, 10, 31)
    end   = datetime(2025, 9, 30)

    # range quotidien
    dates = pd.date_range(start, end, freq="D")

    # appel de to_predict pour chaque date
    values = [to_predict(d) for d in dates]

    # DataFrame résultat
    df_pred = pd.DataFrame({"Price": values}, index=dates)

    # --- Affichage tabulaire ---
    print(df_pred)

    # --- Tracé ---
    plt.figure(figsize=(12,5))
    plt.plot(df_pred.index, df_pred["Price"], marker=".", linewidth=1, label="to_predict")
    plt.xlabel("Date")
    plt.ylabel("Prix")
    plt.title("Valeurs quotidiennes retournées par to_predict")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()  

#test_graph()