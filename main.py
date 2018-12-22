'''
main module provide data collection, computation and notification
'''
import json
import logging
from datetime import datetime

from telethon import TelegramClient
from pytrends.request import TrendReq
import requests
import db_sqlite
import config

logging.basicConfig(format='%(name)s - %(asctime)s - %(message)s', level=logging.INFO)
LOGGER = logging.getLogger(__name__)

def get_google_trend():
    '''
    get google trend data
    '''
    try:
        pytrend = TrendReq(tz=-540)
        pytrend.build_payload(kw_list=['BTC USD'], timeframe='now 1-d')
        interest_over_time_df = pytrend.interest_over_time()
        btc_usd_ave = interest_over_time_df['BTC USD'].mean()
        return btc_usd_ave
    except Exception as error:
        LOGGER.error('Error when get_google_trend: %s', error)
        raise error

def get_google_trend_detail():
    '''
    get google detail trend data of recent 3 month
    latest 3 days data miss
    '''
    try:
        pytrend = TrendReq(tz=-540)
        pytrend.build_payload(kw_list=['BTC USD'], timeframe='today 3-m')
        interest_over_time_df = pytrend.interest_over_time()
        btc_usd = interest_over_time_df['BTC USD']
        return btc_usd
    except Exception as error:
        LOGGER.error('Error when get_google_trend_detail: %s', error)
        raise error

def get_krw_btc_from_upbit():
    '''
    get bitcoin price from upbit exchange
    '''
    url = 'https://api.upbit.com/v1/candles/days?market=KRW-BTC'
    try:
        result = requests.get(url, timeout=5)
        data = json.loads(result.text, encoding='utf-8')
        return (data[0]['trade_price'], data[0]['high_price'], data[0]['low_price'])
    except Exception as error:
        LOGGER.error('Error when get_krw_btc_from_upbit: %s', error)
        raise error

def get_krw_btc_from_upbit_detail():
    '''
    get bitcoin price with day interval of recent 3 month
    remove latest 3 days data to match gtrend
    '''
    try:
        url = "https://api.upbit.com/v1/candles/days"
        querystring = {'market':'KRW-BTC', 'count': 93}
        response = requests.request('GET', url, params=querystring)
        data = json.loads(response.text, encoding='utf-8')
        price = []
        for candle in data:
            price.append(candle['trade_price'])
        price.reverse()
        for _ in range(3):
            price.pop()
        return price
    except Exception as error:
        LOGGER.error('Error when get_krw_btc_from_upbit_detail: %s', error)
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
                            bit_usd varchar(20),
                            buy_bitcoin varchar(20),
                            rate varchar(20),
                            price varchar(20),
                            change_rate varchar(20),
                            strategy varchar(20))
                        '''
        db_sqlite.db_init(CMD)
        BTC_USD_AVE = get_google_trend()
        # get current price from exchage Upbit
        (PRICE, PRICE_HIGH, PRICE_LOW) = get_krw_btc_from_upbit()
        # get price and btc_usd gtrend of yesterday from db
        CMD = 'SELECT price, bit_usd FROM history ORDER BY date DESC LIMIT 1'
        ST = db_sqlite.db_select(CMD)
        # no yesterday's data
        if not ST:
            RATE_PRICE = 0
            PRICE_DIFF = 0
            RATE_GTREND = 0
        else:
            PRICE_YESTERDAY = ST[0][0]
            PRICE_DIFF = float(PRICE) - float(PRICE_YESTERDAY)
            RATE_PRICE = PRICE_DIFF / float(PRICE_YESTERDAY)
            GTREND_YESTERDAY = ST[0][1]
            GTREND_DIFF = float(BTC_USD_AVE) - float(GTREND_YESTERDAY)
            RATE_GTREND = GTREND_DIFF / float(GTREND_YESTERDAY)
        if RATE_GTREND > 0.25 and RATE_PRICE > 0.01:
            STRATEGY = 'BUY'
        else:
            STRATEGY = 'SELL'
        # save to db
        CMD = 'INSERT INTO history VALUES (?,?,?,?,?,?,?)'
        DATE = datetime.now().strftime("%Y-%m-%d")
        PARAMS = (DATE, BTC_USD_AVE, 'n/a', 'n/a', PRICE, RATE_PRICE, STRATEGY)
        db_sqlite.db_insert(CMD, PARAMS)
        # send to telegram
        MESSAGE = f'BTC USD : {BTC_USD_AVE}, rate is {RATE_GTREND} \
                    and Upbit BTC/KRW current price is {PRICE}, change price is {PRICE_DIFF}, \
                    change rate is {RATE_PRICE}, \
                    today STRATEGY is {STRATEGY} with reference \
                    high price {PRICE_HIGH} and low price {PRICE_LOW}'
        LOGGER.info(MESSAGE)
        # send('me', MESSAGE)
    except BaseException as error:
        LOGGER.error('system abort abnormally due to %s', error)
