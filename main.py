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
        pytrend.build_payload(kw_list=['BTC USD', 'buy bitcoin'], timeframe='now 1-d')
        interest_over_time_df = pytrend.interest_over_time()
        btc_usd_ave = interest_over_time_df['BTC USD'].mean()
        buy_bitcoin_ave = interest_over_time_df['buy bitcoin'].mean()
        return (btc_usd_ave, buy_bitcoin_ave)
    except Exception as error:
        LOGGER.error('Error when get_google_trend: %s', error)
        raise error

def get_google_trend_detail():
    '''
    get google detail trend data of 5 days
    '''
    try:
        pytrend = TrendReq(tz=-540)
        pytrend.build_payload(kw_list=['BTC USD', 'buy bitcoin'], timeframe='now 7-d')
        interest_over_time_df = pytrend.interest_over_time()
        btc_usd = interest_over_time_df['BTC USD']
        buy_bitcoin = interest_over_time_df['buy bitcoin']
        return (btc_usd, buy_bitcoin)
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
        data = json.loads(result.text, encoding="utf-8")
        return (data[0]['trade_price'], data[0]['high_price'], data[0]['low_price'])
    except Exception as error:
        LOGGER.error('Error when get_krw_btc_from_upbit: %s', error)
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
                            STRATEGY varchar(20))
                        '''
        db_sqlite.db_init(CMD)
        # get google trend data of previous day with format (btc_usd_average, buy_bitcon_average)
        GTREND = get_google_trend()
        # get current price from exchage Upbit
        (PRICE, PRICE_HIGH, PRICE_LOW) = get_krw_btc_from_upbit()
        # calculate ratio of buy bitcon / btc usd
        RATE_GREAND = GTREND[1] / GTREND[0]
        # get price of yesterday from db
        CMD = 'SELECT price FROM history ORDER BY date DESC LIMIT 1'
        ST = db_sqlite.db_select(CMD)
        # no yesterday's data
        if not ST:
            PRICE_YESTERDAY = 0
            PRICE_DIFF = 0
            RATE_PRICE = 0
        else:
            PRICE_YESTERDAY = ST[0][0]
            PRICE_DIFF = float(PRICE) - float(PRICE_YESTERDAY)
            RATE_PRICE = PRICE_DIFF / float(PRICE_YESTERDAY)
        # STRATEGY condition: ratio of buy bitcon / btc usd > 35% and price increase rate > 1%
        if RATE_GREAND > 0.35 and RATE_PRICE > 0.01:
            STRATEGY = 'BUY'
        else:
            STRATEGY = 'SELL'
        # save to db
        CMD = 'INSERT INTO history VALUES (?,?,?,?,?,?,?)'
        DATE = datetime.now().strftime("%Y-%m-%d")
        PARAMS = (DATE, GTREND[0], GTREND[1], RATE_GREAND, PRICE, RATE_PRICE, STRATEGY)
        db_sqlite.db_insert(CMD, PARAMS)
        # send to telegram
        MESSAGE = f'BTC USD : buy bitcoin = {GTREND}, rate is {RATE_GREAND} \
                    and Upbit BTC/KRW current price is {PRICE}, change price is {PRICE_DIFF}, \
                    change rate is {RATE_PRICE}, \
                    today STRATEGY is {STRATEGY} with reference \
                    high price {PRICE_HIGH} and low price {PRICE_LOW}'
        LOGGER.info(MESSAGE)
        send('me', MESSAGE)
    except BaseException as error:
        LOGGER.error('system abort abnormally due to %s', error)
