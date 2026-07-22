import os
import numpy as np
import yfinance as yf
import pandas as pd
from datetime import datetime


class StockConfig:
    ALLOWED_PERIODS = ["1d", "5d", "1mo", "1y"]

    def __init__(self, symbol: str, period: str, interval: str = "5m"):
        self.symbol = symbol
        self.period = period
        self.interval = interval

    @property
    def symbol(self) -> str:
        return self._symbol

    @symbol.setter
    def symbol(self, value: str):
        clean_value = value.strip().upper()
        if not clean_value:
            raise ValueError("Ticker symbol cannot be empty.")
        self._symbol = clean_value

    @property
    def period(self) -> str:
        return self._period

    @period.setter
    def period(self, value: str):
        clean_value = value.strip().lower()
        if clean_value not in self.ALLOWED_PERIODS:
            raise ValueError(f"Invalid period. Must be one of: {self.ALLOWED_PERIODS}")
        self._period = clean_value

    def display_config(self):
        print(self)

    def __str__(self) -> str:
        return f"[Config] Ticker: {self.symbol} | Period: {self.period} | Interval: {self.interval}"


class StockDownloader:
    def __init__(self, config_object: StockConfig):
        self.config = config_object
        self.data = pd.DataFrame()
        self.download_status = "Not Started"

    def has_data(self) -> bool:
        return not self.data.empty

    def get_record_count(self) -> int:
        return len(self.data)

    def download_data(self) -> bool:
        self.download_status = "In Progress"
        print(f"\n[*] Fetching data from Yahoo Finance for {self.config.symbol}...")

        try:
            df = yf.download(
                tickers=self.config.symbol,
                period=self.config.period,
                interval=self.config.interval,
                progress=False,
            )

            if df.empty:
                self.download_status = "Failed"
                print("[-] No data returned. Please verify the ticker symbol.")
                return False

            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            self.data = df
            self.download_status = "Success"
            print(
                f"[+] Successfully downloaded {self.get_record_count()} market candles."
            )
            return True

        except Exception as e:
            self.download_status = "Failed"
            print(f"[-] A network or download error occurred: {e}")
            return False


class BaseReport:
    """Base class to demonstrate clean OOP Inheritance architectures"""

    def __init__(self, report_type: str):
        self.report_type = report_type
        self.generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def display_header(self):
        print(f"\n=== {self.report_type.upper()} REPORT ===")
        print(f"Generated at: {self.generated_at}")


class StockReport(BaseReport):
    def __init__(self, downloader: StockDownloader):

        super().__init__(report_type="Financial Stock Summary")
        self.downloader = downloader
        self.summary_data = {}

    def generate_summary(self):
        """Processes raw DataFrame numbers into an easily digestible summary dictionary"""
        if not self.downloader.has_data():
            return

        df = self.downloader.data

        self.summary_data["total_candles"] = len(df)
        self.summary_data["max_price"] = float(df["High"].max())
        self.summary_data["min_price"] = float(df["Low"].min())
        self.summary_data["avg_close"] = float(df["Close"].mean())

        self.summary_data["start_date"] = str(df.index.min())
        self.summary_data["end_date"] = str(df.index.max())

    def display_header(self):
        super().display_header()
        print(f"Target Asset: {self.downloader.config.symbol}")
        print("-" * 30)

    def display_summary(self):
        if not self.summary_data:
            self.generate_summary()

        if not self.summary_data:
            print("[-] No analytical metrics to show.")
            return

        self.display_header()
        print(f"Total Candles (5m):  {self.summary_data['total_candles']}")
        print(f"Highest Price:       ${self.summary_data['max_price']:.2f}")
        print(f"Lowest Price:        ${self.summary_data['min_price']:.2f}")
        print(f"Average Close Price: ${self.summary_data['avg_close']:.2f}")
        print(f"First Available Date: {self.summary_data['start_date']}")
        print(f"Last Available Date:  {self.summary_data['end_date']}")
        print("=" * 28)


class CSVManager:
    @staticmethod
    def generate_filename(symbol: str) -> str:
        return f"{symbol.lower()}_market_data.csv"

    @staticmethod
    def file_exists(filename: str) -> bool:
        return os.path.exists(filename)

    @classmethod
    def save_to_csv(cls, downloader_object: StockDownloader) -> bool:
        if not downloader_object.has_data():
            print(
                "[-] Data validation failed: Object contains no records to write out."
            )
            return False

        filename = cls.generate_filename(downloader_object.config.symbol)

        try:
            downloader_object.data.to_csv(filename)
            print(f"[+] File Saved Successfully -> {os.path.abspath(filename)}")
            return True
        except Exception as e:
            print(f"[-] Operating System File Write Failure: {e}")
            return False


class StockApplication:
    def __init__(self):
        self.download_history = []
        self.last_downloader = None

    def show_menu(self):
        print("\n=== STOCK DATA MANAGEMENT SYSTEM ===")
        print("1. Download Stock Data (5m)")
        print("2. View Download History")
        print("3. View Last Download Report")
        print("4. View Available Periods")
        print("5. Exit")

    def create_download(self):
        symbol = input("Enter ticker symbol (e.g., AAPL, TSLA): ").strip()

        print(f"Available periods: {StockConfig.ALLOWED_PERIODS}")
        period = input("Enter period choice exactly: ").strip()

        try:
            config = StockConfig(symbol, period)
            config.display_config()

            downloader = StockDownloader(config)

            success = downloader.download_data()

            if success:
                self.last_downloader = downloader

                self.download_history.append(
                    {
                        "symbol": config.symbol,
                        "period": config.period,
                        "interval": config.interval,
                        "records": downloader.get_record_count(),
                        "status": downloader.download_status,
                        "downloaded_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    }
                )

                CSVManager.save_to_csv(downloader)

            else:
                self.download_history.append(
                    {
                        "symbol": symbol.upper(),
                        "period": period,
                        "interval": "5m",
                        "records": 0,
                        "status": "Failed",
                        "downloaded_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    }
                )

        except ValueError as e:
            print(f"\n[-] Configuration Input Validation Error: {e}")

        except Exception as e:
            print(f"\n[-] Unexpected Error: {e}")

    def view_history(self):
        if not self.download_history:
            print("\n[*] History log is completely empty.")
            return

        print("\n========== DOWNLOAD HISTORY ==========")

        for index, item in enumerate(self.download_history, start=1):
            print(f"\nDownload #{index}")
            print(f"Ticker        : {item['symbol']}")
            print(f"Period        : {item['period']}")
            print(f"Interval      : {item['interval']}")
            print(f"Records       : {item['records']}")
            print(f"Status        : {item['status']}")
            print(f"Downloaded At : {item['downloaded_at']}")
            print("-" * 35)

    def view_last_report(self):
        if self.last_downloader is None:
            print(
                "\n[-] Operational Error: No successful download active in memory buffer."
            )
            return

        report = StockReport(self.last_downloader)
        report.generate_summary()
        report.display_summary()

    def run(self):
        while True:
            self.show_menu()

            choice = input("\nSelect Option (1-5): ").strip()

            if choice == "1":
                self.create_download()

            elif choice == "2":
                self.view_history()

            elif choice == "3":
                self.view_last_report()

            elif choice == "4":
                print(
                    f"\n[*] Allowed ingestion timeframes: {StockConfig.ALLOWED_PERIODS}"
                )

            elif choice == "5":
                print("\nShutting down engine core. Goodbye!")
                break

            else:
                print(
                    "[-] Command not recognized. Select an integer option between 1 and 5."
                )


if __name__ == "__main__":
    app = StockApplication()
    app.run()

    # project 3
    def download_stock_data(ticker, period="5d", interval="5m"):
        df = yf.download(tickers=ticker, period=period, interval=interval)
        if df.empty:
            raise ValueError(
                f"No data found for ticker '{ticker}'. The symbol might be invalid or no data is available."
            )
        print("\n--- Data Successfully Downloaded ---")
        print(f"Dataset Shape (Rows, Columns): {df.shape}")
        print("\nFirst 5 Rows:")
        print(df.head())
        return df
    def clean_data(df):
        df= df.copy()
        if isinstance(df.columns, pd.MultiIndex):
            df.columns= df.columns.get_level_values(0)
        df = df.reset_index()
        df= df.drop_duplicates()
        df = df.ffill().dropna()
        return df
    def add_technical_columns(df):
        df= df.copy()
        df['Price_Change']= df['Close'].diff()
        df['Percentage_Change']= df['Close'].pct_change() * 100
        df['Candle_Range']= df['High']- df['Low']
        df['SMA_10']= df['Close'].rolling(window=10).mean()
        df['SMA_20']= df['Close'].rolling(window=20).mean()
        df['Volume_Average']= df['Volume'].rolling(window=10).mean()
        df['Volatility']= df['Percentage_Change'].rolling(window=20).std()
        return df
    def generate_signals(df):
        df = df.copy()
        conditions= [
            df['SMA_10']>df['SMA_20'],
            df['SMA_10']<df['SMA_20'],
        ]
        choices= ["BUY", "SELL"]
        df["Signal"]= np.select(conditions, choices, default= "Hold")
        return df
    def analyze_data(df):
        print("\n--- Market Data Summary ---")
        print(f"Total Candles: {len(df)}")
        print(f"Average Close Price: {df['Close'].mean():.2f}")
        print(f"Highest Price: {df['High'].max():.2f}")
        print(f"Lowest Price: {df['Low'].min():.2f}")
        total_vol = df['Volume'].sum()
        avg_vol = df['Volume'].mean()
        std_dev = df['Close'].std()
        buy_count = (df["Signal"] == "BUY").sum()
        sell_count = (df["Signal"] == "SELL").sum()
        print(f"BUY Signals: {buy_count}")
        print(f"SELL Signals: {sell_count}")
        latest_signal = df['Signal'].iloc[-1]
        print(f"Total Volume         : {total_vol:,.0f}")
        print(f"Average Volume       : {avg_vol:,.0f}")
        print(f"Price Std Dev        : {std_dev:.2f}")
        print(f"BUY Signals          : {buy_count}")
        print(f"SELL Signals         : {sell_count}")
        print(f"Latest Signal        : {latest_signal}")
        print("========================================================\n")
        df['Date'] = df['Datetime'].dt.date
        daily_avg_price= df.groupby('Date')['Close'].mean()
        daily_max_vol = df.groupby('Date')['Volume'].max()
        daily_summary = df.groupby('Date').agg(
        Avg_Close=('Close', 'mean'),
        Max_Volume=('Volume', 'max')
        )
        print(daily_summary)
        print("\n--- Time-Based Daily Summary ---")
        print(daily_summary)
        print("--------------------------------\n")
    def export_data(df, filename="AAPL_5d_5m_analyzed.csv"):
        df.to_csv(filename, index=False)
        print(f"\n[Success] Data exported to {filename}")
    def time_based_analysis(df):
                df = df.copy()
                if "Datetime" in df.columns:
                    df["Date"] = pd.to_datetime(df["Datetime"]).dt.date
                elif isinstance(df.index, pd.DatetimeIndex):
                    df["Date"] = df.index.date
    
                daily_summary = df.groupby("Date").agg(
                    Avg_Close=("Close", "mean"), Max_Volume=("Volume", "max")
                )
                print("\n--- Time-Based Daily Summary ---")
                print(daily_summary)
                print("--------------------------------\n")
    def main():
        df= None
        while True:
            print("\n=== STOCK DATA ANALYSIS TOOL ===")
            print("1. Download New Data")
            print("2. Clean Data")
            print("3. Add Indicators & Signals")
            print("4. View Market Analysis")
            print("5. View Daily Summary")
            print("6. Export Data to CSV")
            print("7. Exit")

            choice = input("Select an option (1-7): ")
            if choice== "1":
                ticker= input("Enter ticker symbol(e.g., AAPL):")
                try:
                    df = download_stock_data(ticker)
                except Exception as e:
                    print(f"\n[Error] Could not download data:{e}")

            elif choice== "2":
                if df is not None:
                    df= clean_data(df)
                    print("\n[Success] Data cleaned successfully!")
                else:
                    print("\n[Warning] Please download or load data first!")

            elif choice== "3":
                if df is not None:
                    df = add_technical_columns(df)
                    df = generate_signals(df)
                    print(
                        "\n[Success] Technical indicators and signals added successfully!"
                    )
                else:
                    print("\n[Warning] Please download or load data first!")

        
            elif choice == "4":
                if df is not None:
                    analyze_data(df)
                else:
                    print("\n[Warning] Please download or load data first!")

        
            elif choice == "5":
                if df is not None:
                    time_based_analysis(df)
                else:
                    print("\n[Warning] Please download or load data first!")

        
            elif choice == "6":
                if df is not None:
                    filename = "AAPL_5d_5m_analyzed.csv"
                    df.to_csv(filename, index=False)
                    print(f"\n[Success] Data exported to '{filename}'!")
                else:
                    print("\n[Warning] Please download or load data first!")

        
            elif choice == "7":
                print("\nThank you for using the Stock Data Analysis Tool. Goodbye!")
                break
            else: 
                print("\n[Error] Invalid choice! Please enter a number between 1 and 7.")
        



if __name__ == "__main__":
    main()
