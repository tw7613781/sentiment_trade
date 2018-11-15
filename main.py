import requests
import json
import config
import logging
import sqlite3
from telethon import TelegramClient
from datetime import datetime
from pytrends.request import TrendReq

logging.basicConfig(format='%(name)s - %(asctime)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


def db_init(cmd_sql):
    conn = sqlite3.connect('history.db')
    cursor = conn.cursor()
    cursor.execute(cmd_sql)
    cursor.close()
    conn.close()


def db_select(cmd_sql):
    conn = sqlite3.connect('history.db')
    cursor = conn.cursor()
    cursor.execute(cmd_sql)
    records = cursor.fetchall()
    cursor.close()
    conn.close()
    # return a 2-dimension array including sql select result
    return records


def db_insert(cmd_sql, params):
    conn = sqlite3.connect('history.db')
    cursor = conn.cursor()
    cursor.execute(cmd_sql, params)
    cursor.close()
    conn.commit()
    conn.close()


def get_google_trend():
    try:
        pytrend = TrendReq(tz=-540)
        pytrend.build_payload(kw_list=['BTC USD', 'buy bitcoin'], timeframe='now 1-d')
        interest_over_time_df = pytrend.interest_over_time()
        btc_usd_ave = interest_over_time_df['BTC USD'].mean()
        buy_bitcoin_ave = interest_over_time_df['buy bitcoin'].mean()
        return (btc_usd_ave, buy_bitcoin_ave)
    except Exception as e:
        logger.error(f'Error when get_google_trend: {e}')

def get_krw_btc_from_upbit():
    url = 'https://api.upbit.com/v1/candles/days?market=KRW-BTC'
    try:
        r = requests.get(url, timeout = 5)
        data = json.loads(r.text, encoding="utf-8")
        return (data[0]['trade_price'], data[0]['high_price'], data[0]['low_price'])
    except Exception as e:
        logger.error(f'Error when get_krw_btc_from_upbit: {e}')


def send(receiver, message):
    session = config.session
    api_id = config.api_id
    api_hash = config.api_hash
    client = TelegramClient(session, api_id, api_hash).start()
    client.send_message(receiver, message)


if __name__ == '__main__':
    # init db
    cmd = '''CREATE TABLE IF NOT EXISTS history
                        (date varchar(20),
                        bit_usd varchar(20),
                        buy_bitcoin varchar(20),
                        rate varchar(20),
                        price varchar(20),
                        change_rate varchar(20),
                        strategy varchar(20))
                    '''
    db_init(cmd)
    # get google trend data of previous day with format (btc_usd_average, buy_bitcon_average)
    gtrend = get_google_trend()
    # get current price from exchage Upbit
    (price, price_high, price_low) = get_krw_btc_from_upbit()
    # calculate ratio of buy bitcon / btc usd
    rate_gtrend = gtrend[1] / gtrend[0]
    # get price of yesterday from db
    cmd = 'SELECT price FROM history ORDER BY date DESC LIMIT 1'
    st = db_select(cmd)
    # no yesterday's data
    if len(st) == 0:
        price_yesterday = 0
        price_diff = 0
        rate_price = 0
    else:
        price_yesterday = st[0][0]
        price_diff = float(price) - float(price_yesterday)
        rate_price = price_diff / float(price_yesterday)            
    # strategy condition: ratio of buy bitcon / btc usd > 35% and price increase rate > 1%
    if rate_gtrend > 0.35 and rate_price > 0.01:
        strategy = 'BUY'
    else:
        strategy = 'SELL'
    # save to db
    cmd = 'INSERT INTO history VALUES (?,?,?,?,?,?,?)'
    date = datetime.now().strftime("%Y-%m-%d")
    params = (date, gtrend[0], gtrend[1], rate_gtrend, price, rate_price, strategy)
    db_insert(cmd, params)
    # send to telegram
    message = f'BTC USD : buy bitcoin = {gtrend}, rate is {rate_gtrend} and Upbit BTC/KRW current price is {price}, change price is {price_diff}, change rate is {rate_price}, today strategy is {strategy} with reference high price {price_high} and low price {price_low}'
    logger.info(message)
    send('me', message)
