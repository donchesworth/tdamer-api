import requests
import urllib
import json
import pandas as pd
from pathlib import Path
from gspread_pandas import Spread, Client
import os
import time
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
CLIENT_ID = os.environ.get("CLIENT_ID")
TD_ACCT = os.environ.get("TD_ACCT")
AUTH_ENDPOINT = 'https://api.tdameritrade.com/v1/oauth2/token'
LOCALURI = 'http://localhost'

         
def get_positions(access_token):
    token = access_token['token_type'] + ' ' + access_token['access_token']
    qparams={'fields':'positions'}
    hparams={'Authorization': token}
    acct_req = f'https://api.tdameritrade.com/v1/accounts/{TDACCT}'
    response = requests.get(acct_req, params=qparams, headers=hparams)
    if response.status_code == 200:
        print("pulled positions")
    return response.json()


def positions_to_pandas(positions):
    json_data = json.loads(positions.text)
    df = pd.json_normalize(json_data['securitiesAccount']['positions'])
    # maybe 'currentDayCost', 'currentDayProfitLoss', 'currentDayProfitLossPercentage' in the future
    df = df[['marketValue', 'instrument.symbol', 'instrument.cusip', 'longQuantity', 'averagePrice', 'instrument.assetType']]
    df.columns = ['Investment', 'Symbol', 'CUSIP', 'Quantity', 'Initial Price', 'Type']
    df = df.sort_values(['Type', 'Symbol'])
    df.reset_index(inplace=True)
    return df


def add_stock_bond_percentage(df):
    df['Stock%'] = df.replace({'Type':{'EQUITY':1, 'CASH_EQUIVALENT':0}})['Type']
    df['Bond%'] = 0
    df['Cash%'] = df.replace({'Type':{'EQUITY':0, 'CASH_EQUIVALENT':1}})['Type']
    df.drop('Type', axis=1, inplace=True)
    return df


def get_full_positions(atoken):
    positions = get_positions(atoken)
    df = positions_to_pandas(positions)
    df = add_stock_bond_percentage(df)
    return df


def add_to_sheet(df):
    td_spread = Spread(SHEETID)
    td_spread.df_to_sheet(df, index=False, sheet='TD Ameritrade', replace=True)



# execution
rtoken = get_refresh_token()
atoken = thirty_min_access_token(rtoken)
positions_response = get_positions(atoken)
df = positions_to_pandas(positions_response)
df = add_stock_bond_percentage(df)
add_to_sheet(df)
