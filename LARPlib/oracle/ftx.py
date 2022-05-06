from typing import List
import requests as req
import pandas as pd
import numpy as np
from datetime import datetime as dt
# have to fix this eventually
from warnings import simplefilter
simplefilter(action="ignore", category=pd.errors.PerformanceWarning)

endpoint_url = 'https://ftx.com/api/markets'
daily = str(60*60) # for resolution param in req header
start_date = dt.now().timestamp()

def get_tickers():
    ftx_mkts = req.get(f'{endpoint_url}').json()['result']
    df = pd.DataFrame(ftx_mkts)
    
    perps = df.copy()[df['name'].str.contains("-PERP")]
    perps = perps[~perps['name'].str.contains('USDT|UST')] # don't wanna trade stablecoins do we

    # sort by volume
    perps = perps.sort_values(by=['volumeUsd24h'], ascending=False).reset_index(drop=True)
    return list(perps['name'])

def get_historical_df(tickers):
    ohlcvs = {}

    for ticker in tickers:
        historical_data = req.get(f'{endpoint_url}/{ticker}/candles?resolution={daily}').json()
        ticker_df = pd.DataFrame(historical_data['result'])
        ticker_df['startTime'] = pd.to_datetime(ticker_df['startTime']).dt.tz_localize(None)
        ticker_df = ticker_df.set_index('startTime')
        #we are interested in the OHLCV mainly, let's rename them 
        ohlcvs[ticker] = ticker_df[["open", "high", "low", "close", "volume"]]
        print(ticker)
        print(ohlcvs[ticker]) #we can now get the data that we want inside a nicely formatted df

    
    #now, we want to put that all into a single dataframe.
    #since the columns need to be unique to identify the instrument, we want to add an identifier.
    #let's steal the BTC-PERP index as our dataframe index
    df = pd.DataFrame(index=ohlcvs["BTC-PERP"].index)
    df.index.name = "datetime"
    instruments = list(ohlcvs.keys())

    for inst in instruments:
        inst_df = ohlcvs[inst]
        columns = list(map(lambda x: "{} {}".format(inst, x), inst_df.columns)) #this tranforms open, high... to AAPL open , AAPL high and so on
        df[columns] = inst_df

    return df, instruments

def get_historical_cumret(df, tickers):
    # may need to change this.
    df.fillna(method="ffill", inplace=True)
    df.fillna(method="bfill", inplace=True)

    # make a new df containing cumulative log returns
    cumret = pd.DataFrame(index=df.index)[1:]

    for ticker in tickers:
        base_ticker = ticker[:ticker.find('-')]
        cumret[base_ticker] = np.diff(np.log(df[f'{ticker} close'])).cumsum() + 1

    return cumret

