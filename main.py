import requests
import json
import config
import logging
from telethon import TelegramClient
from datetime import datetime, timedelta
from pytrends.request import TrendReq

logging.basicConfig(format='%(name)s - %(asctime)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
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
        return (data[0]['opening_price'], data[0]['change_price'], data[0]['change_rate'], data[0]['high_price'], data[0]['low_price'])
    except Exception as e:
        logger.error(f'Error when get_krw_btc_from_upbit: {e}')


def send(receiver, message):
    session = config.session
    api_id = config.api_id
    api_hash = config.api_hash
    client = TelegramClient(session, api_id, api_hash).start()
    client.send_message(receiver, message)


if __name__ == '__main__':
    # get google trend data of previous day with format (btc_usd_average, buy_bitcon_average)
    rt = get_google_trend()
    # get upbit exchange data with format (opening price, change price, change rate, high price, low price)
    price = get_krw_btc_from_upbit()
    # calculate ratio of buy bitcon / btc usd
    rate1 = rt[1] / rt[0]
    # get ratio of price change rate compare with previous day
    rate2 = price[2]
    # strategy condition: ratio of buy bitcon / btc usd > 35% and price increase rate > 1%
    if rate1 > 0.35 and rate2 > 0.01:
        strategy = 'BUY'
    else:
        strategy = 'SELL'
    message = f'BTC USD : buy bitcion = {rt}, rate is {rate1} and upbit BTC/KRW open price is {price[0]}, change price is {price[1]}, change rate is {price[2]}, today strategy is {strategy}, reference with yesterday high {price[3]}, yesterday low {price[4]}'
    logger.info(message)
    send('me', message)
