import os
import time
import datetime
import statistics
import requests
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import plotly.subplots as sp
import plotly.express as px
from typing import List
from bs4 import BeautifulSoup

from ClassForm4 import Form4


class TradingData:

    def __init__(self, cik: str, start_date: str = None, end_date: str = None) -> None:
        self.data = {}
        self.form4 = Form4(cik, start_date, end_date)
        self.add_stock_data()

    def add_stock_data(self) -> None:
        """
        Adds stock data to the Form 4 data and updates the Form4 instance.
        """

        df = pd.DataFrame(self.form4.data)
        df = df[df['ticker'].notnull()]
        df['transaction_date'] = pd.to_datetime(
            df['transaction_date'], format='%Y-%m-%d')
        min_max_dates = df.groupby('ticker').agg(min_date=('transaction_date', 'min'),
                                                 max_date=('transaction_date', 'max')).reset_index()
        # create a dictionary with Ticker as the key and min/max dates as the value
        stock_date_dict = dict(zip(min_max_dates['ticker'], zip(
            min_max_dates['min_date'], min_max_dates['max_date'])))
        # create a list of unique tickers in the dataframe
        tickers = df['ticker'].unique()
        ticker_history_pd = pd.DataFrame(
            columns=['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume', 'stock_ticker'])
        good_ticker = []
        bad_ticker = []
        # loop over each ticker to get the stock prices data from yfinance and append it to the stock prices dataframe
        for ticker in tickers:
            min_date, max_date = stock_date_dict[ticker]
            ticker_history_n = yf.download(
                ticker, start=min_date, end=max_date)
            if not ticker_history_n.empty:
                good_ticker.append(ticker)
                ticker_history_n['stock_ticker'] = ticker
                ticker_history_pd = ticker_history_pd.append(ticker_history_n)
            else:
                bad_ticker.append(ticker)
        ticker_history_pd = ticker_history_pd.reset_index()
        ticker_history_pd = ticker_history_pd.rename(
            columns={c: c.replace(' ', '_').lower() for c in ticker_history_pd.columns})
        stock_prices_df = pd.DataFrame(ticker_history_pd)
        # stock_prices_df = stock_prices_df.reset_index()
        stock_prices_df['date'] = pd.to_datetime(
            stock_prices_df['index'], format='%Y-%m-%d')

        stock_prices_df = stock_prices_df.drop(['index'], axis=1)

        df = pd.merge(df, stock_prices_df, how='left', left_on=[
            'ticker', 'transaction_date'], right_on=['stock_ticker', 'date'])

        df = df.drop(['date', 'stock_ticker'], axis=1)

        df['daily_return'] = (df['close'].astype(
            float) - df['open'].astype(float)) / df['open'].astype(float)
        df['percent_change'] = df['daily_return'].astype(float) * 100
        df['range'] = df['high'].astype(float) - df['low'].astype(float)
        df['average_price'] = (df['high'].astype(
            float) + df['low'].astype(float)) / 2

        df['shares_value_usd'] = df['average_price'].astype(float) * \
            df['shares'].astype(float)
        for col_name, col_values in df.iteritems():
            if col_values.dtype == float:
                df[col_name] = col_values.apply(lambda x: round(x, 4))

        self.data = df.to_dict(orient='records')

    def inside_traiding_impact_plot(self) -> None:
        """
        Generates a plot of the inside trading impact over time.
        """
        df = pd.DataFrame(self.data)
        # Calculate the total inside trading volume for each day
        df = df.groupby("transaction_date").agg({"shares_value_usd": "sum"}).rename(
            columns={"shares_value_usd": "inside_trading_volume"})

        df = df.sort_values(by='transaction_date', ascending=True)

        # Create figure with secondary y-axis
        fig = sp.make_subplots(specs=[[{"secondary_y": True}]])

        # Add traces
        fig.add_trace(
            go.Scatter(x=df["transaction_date"],
                       y=df["inside_trading_volume"], name="Inside Trading Volume"),
            secondary_y=False,
        )

        fig.add_trace(
            go.Scatter(x=df["transaction_date"],
                       y=df["close"], name="Stock Closing Price"),
            secondary_y=True,
        )

        # Add figure title
        fig.update_layout(
            title_text=f"Inside Trading Volume and Stock Closing Price Over Time"
        )

        # Set x-axis title
        fig.update_xaxes(title_text="Date")

        # Set y-axes titles
        fig.update_yaxes(title_text="Inside Trading Volume", secondary_y=False)
        fig.update_yaxes(title_text="Stock Closing Price", secondary_y=True)

        fig.show()
