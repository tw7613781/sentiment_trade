'''
main module provide data collection, computation and notification
'''
import json
import logging
from datetime import datetime

from telethon import TelegramClient
from pytrends.request import TrendReq
import requests
import pandas as pd
import db_sqlite
import config

logging.basicConfig(format='%(name)s - %(asctime)s - %(message)s', level=logging.INFO)
LOGGER = logging.getLogger(__name__)

def get_google_trend():
    '''
    get google trend data, recent 2 days day basis data
    '''
    try:
        pytrend = TrendReq(tz=-540)
        pytrend.build_payload(kw_list=['BTC USD'], timeframe='now 7-d')
        interest_over_time_df = pytrend.interest_over_time()
        btc_usd = interest_over_time_df['BTC USD']
        today = btc_usd[167:143:-1].mean()
        yesterday = btc_usd[143:119:-1].mean()
        return (today, yesterday)
    except Exception as error:
        LOGGER.error('Error when get_google_trend: %s', error)
        raise error

def get_google_trend_detail():
    '''
    get google trend data, recent 7 days hour baiss data
    '''
    try:
        pytrend = TrendReq(tz=-540)
        pytrend.build_payload(kw_list=['BTC USD'], timeframe='now 7-d')
        interest_over_time_df = pytrend.interest_over_time()
        btc_usd = interest_over_time_df['BTC USD']
        return btc_usd
    except Exception as error:
        LOGGER.error('Error when get_google_trend_detail: %s', error)
        raise error

def get_google_trend_7_days():
    '''
    get google trend data, recent 7 days day basis data
    '''
    try:
        pytrend = TrendReq(tz=-540)
        pytrend.build_payload(kw_list=['BTC USD'], timeframe='now 7-d')
        interest_over_time_df = pytrend.interest_over_time()
        btc_usd = interest_over_time_df['BTC USD']
        rt = []
        for x in range(7):
            if x == 6:
                mean_temp = btc_usd[167-x*24:167-(x+1)*24+1:-1].mean()
            else:
                mean_temp = btc_usd[167-x*24:167-(x+1)*24:-1].mean()
            rt.append(mean_temp)
        return rt
    except Exception as error:
        LOGGER.error('Error when get_google_trend_7_days: %s', error)
        raise error

def get_krw_btc_from_upbit():
    '''
    get recent 2 days bitcoin price
    '''
    try:
        url = "https://api.upbit.com/v1/candles/days"
        querystring = {'market':'KRW-BTC', 'count': 1}
        response = requests.request('GET', url, params=querystring)
        data = json.loads(response.text, encoding='utf-8')
        today = data[0]['trade_price']
        yesterday = data[0]['opening_price']
        return (today, yesterday)
    except Exception as error:
        LOGGER.error('Error when get_krw_btc_from_upbit: %s', error)
        raise error

def get_krw_btc_from_upbit_detail():
    '''
    get bitcoin price with 60 min interval of 7 days
    '''
    try:
        url = "https://api.upbit.com/v1/candles/minutes/60"
        querystring = {'market':'KRW-BTC', 'count':168}
        response = requests.request('GET', url, params=querystring)
        data = json.loads(response.text, encoding='utf-8')
        price = []
        for candle in data:
            price.append(candle['trade_price'])
        price.reverse()
        return price
    except Exception as error:
        LOGGER.error('Error when get_krw_btc_from_upbit_detail: %s', error)
        raise error

def get_krw_btc_from_upbit_7_days():
    '''
    get recent 7 days bitcoin price
    '''
    try:
        url = "https://api.upbit.com/v1/candles/minutes/60"
        querystring = {'market':'KRW-BTC', 'count':168}
        response = requests.request('GET', url, params=querystring)
        data = json.loads(response.text, encoding='utf-8')
        price = []
        for candle in data:
            price.append(candle['trade_price'])
        price.reverse()
        price_serise = pd.Series(price)
        rt = []
        for x in range(7):
            if x == 6:
                mean_temp = price_serise[167-x*24:167-(x+1)*24+1:-1].mean()
            else:
                mean_temp = price_serise[167-x*24:167-(x+1)*24:-1].mean()
            rt.append(mean_temp)
        return rt
    except Exception as error:
        LOGGER.error('Error when get_krw_btc_from_upbit_7_days: %s', error)
        raise error

def send(receiver, msg):
    '''
    send notification by telegram api
    '''
    session = config.SESSION
    api_id = config.API_ID
    api_hash = config.API_HASH
    client = TelegramClient(session, api_id, api_hash).start()
    client.send_message(receiver, msg)


if __name__ == '__main__':
    try:
        # init db
        CMD = '''CREATE TABLE IF NOT EXISTS history
                            (date varchar(20),
                            btc_usd varchar(20),
                            btc_usd_rate varchar(20),
                            price varchar(20),
                            price_rate varchar(20),
                            strategy varchar(20))
                        '''
        db_sqlite.db_init(CMD)
        (BTC_USD_T, BTC_USD_Y) = get_google_trend()
        BTC_USD_DIFF = BTC_USD_T - BTC_USD_Y
        BTC_USD_RATE = BTC_USD_DIFF / BTC_USD_Y
        (PRICE_T, PRICE_Y) = get_krw_btc_from_upbit()
        PRICE_DIFF = PRICE_T - PRICE_Y
        PRICE_RATE = PRICE_DIFF / PRICE_Y
        if BTC_USD_RATE > 0.25 and PRICE_RATE > 0.01:
            STRATEGY = 'BUY'
        else:
            STRATEGY = 'SELL'
        # save to db
        CMD = 'INSERT INTO history VALUES (?,?,?,?,?,?)'
        DATE = datetime.now().strftime("%Y-%m-%d")
        PARAMS = (DATE, BTC_USD_T, BTC_USD_RATE, PRICE_T, PRICE_RATE, STRATEGY)
        db_sqlite.db_insert(CMD, PARAMS)
        # send to telegram
        MESSAGE = f'BTC USD GTrend: {BTC_USD_T}, change rate is {BTC_USD_RATE} \
                    and Upbit BTC/KRW current price is {PRICE_T}, change price is {PRICE_DIFF}, \
                    change rate is {PRICE_RATE}, today STRATEGY is {STRATEGY}'
        LOGGER.info(MESSAGE)
        send('me', MESSAGE)
    except BaseException as error:
        LOGGER.error('system abort abnormally due to %s', error)
