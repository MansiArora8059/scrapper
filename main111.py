import yfinance as yf
import pandas as pd

# Functional Requirements
# 1.Accept stock information # type: ignore
stock_configuration = {}
valid_period = ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"]
while True:
    symbol = input("Enter the stock symbol:").strip().upper()
    period = (
        input(
            "Enter the period (e.g., 1d, 5d, 1mo,"
            " 3mo, 6mo, 1y, 2y, "
            "5y, 10y, ytd, max):  "
        )
        .strip()
        .lower()
    )
    if symbol == "":
        print("Stock symbol cannot be empty.")
        continue

    if period not in valid_period:
        print("Invalid period. Try again.")
        continue
    stock_configuration["symbol"] = symbol
    stock_configuration["period"] = period
    break
stock_configuration["interval"] = "5m"

print(stock_configuration)


def find_stockinfo(symbol, period):
    df = yf.download(tickers=symbol, period=period, interval="5m")
    df = df.asfreq("D")
    df = df.ffill()
    return df


df = find_stockinfo(stock_configuration["symbol"], stock_configuration["period"])

df["Symbol"] = stock_configuration["symbol"]
df["Period"] = stock_configuration["period"]
df["Interval"] = stock_configuration["interval"]

df.to_csv("stock_data.csv")
data_dict = df.to_dict()
dict_df = pd.DataFrame.from_dict(data_dict)
dict_df.to_csv("stock_data_from_dict.csv")
print(data_dict)
print(df)


class stock_config:
    def __init__(self, symbol, period, interval="5m"):
        if not self.is_validperiod(period):
            raise ValueError(f"Invalid period: {period}")
        if not self.validate_symbol_viahistory(symbol):
            raise ValueError(f"Invalid stock symbol: {symbol}")

        if interval == "5m" and period not in ["1d", "5d", "1mo", "3mo"]:
            raise ValueError(
                "5-minute interval data is only available for periods up to 3mo."
            )
        self.symbol = symbol
        self.period = period
        self.interval = interval

    def validate_symbol_viahistory(self, symbol):
        ticker = yf.Ticker(symbol)
        history = ticker.history(period="1d")
        return not history.empty

    def is_validperiod(self, period_string):
        valid_period = [
            "1d",
            "5d",
            "1mo",
            "3mo",
            "6mo",
            "1y",
            "2y",
            "5y",
            "10y",
            "ytd",
            "max",
        ]
        return period_string.strip().lower() in valid_period


while True:
    symbol = input("Enter the stock symbol:").strip().upper()
    period = (
        input(
            "Enter the period (e.g., 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max):  "
        )
        .strip()
        .lower()
    )

    if symbol == "":
        print("Stock symbol cannot be empty.")
        continue

    try:
        config = stock_config(symbol, period)
    except ValueError as e:
        print(e)
        continue
    break

print(f"Symbol: {config.symbol}, Period: {config.period}, Interval: {config.interval}")


class stockdownloader:
    def __init__(self, config, data, download_status):
        self.config = config
        self.data = data
        self.download_status = download_status

    def download_data(self):

        if self.has_data:
            self.data = yf.download(
                tickers=self.config.symbol,
                period=self.config.period,
                interval=self.config.interval,
            )
            self.download_status = not self.data.empty
        else:
            self.data = pd.DataFrame()
            self.download_status = False
        return self.data

    def has_data(self):
        return self.data is not None and not getattr(self.data, "empty", True)
