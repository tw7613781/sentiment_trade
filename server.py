'''
server provide a web server to host a data visualization and analysis
'''

import sqlite3
import io
import base64
from matplotlib import pyplot as plt, dates as mdates
from flask import Flask, render_template
import pandas as pd
import numpy as np
from main import get_google_trend_detail, get_krw_btc_from_upbit_detail
APP = Flask(__name__)


@APP.route('/')
def index():
    '''
    provide route logic for '/'
    '''
    graph_url_main = create_graph_main()
    graph_url_gtrend = create_graph_gtrend()
    return render_template('index.html', graph_url_main=graph_url_main,
                           graph_url_gtrend=graph_url_gtrend)

def create_graph_main():
    '''
    create a analysis figure based on collected data and save it to memory as Bytes
    '''
    cnx = sqlite3.connect('history.db')
    cmd = 'SELECT * FROM history ORDER BY date'
    data_frame = pd.read_sql_query(cmd, cnx)
    date = pd.to_datetime(data_frame['date'])
    btc_usd = data_frame.bit_usd.astype(np.float)
    price = data_frame.price.astype(np.float)
    price = (price - price.min()) / (price.max() - price.min()) * 100
    strategy = ['SELL']*btc_usd.size
    for x in range(1, btc_usd.size):
        trend_diff = btc_usd.iloc[x] - btc_usd.iloc[x-1]
        if btc_usd.iloc[x-1] == 0.0:
            trend_rate = 0
        else:
            trend_rate = trend_diff / btc_usd.iloc[x-1]
        price_diff = price.iloc[x] - price.iloc[x-1]
        if price.iloc[x-1] == 0.0:
            price_rate = 0
        else:
            price_rate = price_diff / price.iloc[x-1]
        if trend_rate > 0.10:
            if price_rate > 0.03:
                strategy[x] = 'BUY'
    dic = {'BUY': 100, 'SELL': -100}
    strategy = data_frame.strategy.map(dic)
    plt.figure(figsize=(15, 6))
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%Y'))
    plt.gca().xaxis.set_major_locator(mdates.DayLocator())
    plt.plot(date, price)
    plt.plot(date, btc_usd)
    plt.plot(date, price_rate, '.')
    plt.plot(date, trend_rate, '*')
    plt.plot(date, strategy, '^')
    plt.axhline(y=0, color='k')
    plt.gcf().autofmt_xdate()
    plt.title('sentiment trade')
    plt.legend(['price(normalized)', 'btc_usd gtrend',
                'price rate', 'gtrend rate', 'strategy'])
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    graph_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    return graph_url

def create_graph_gtrend():
    '''
    create a figure base on recent 3 month gtrend data
    '''
    btc_usd = get_google_trend_detail()
    price_list = get_krw_btc_from_upbit_detail()
    diff = len(price_list) - btc_usd.size
    if diff != 0:
        for _ in range(diff):
            price_list.pop(0)
    # btc_usd = (btc_usd - btc_usd.min()) / (btc_usd.max() - btc_usd.min()) * 100
    price = pd.Series(price_list)
    price = (price - price.min()) / (price.max() - price.min()) * 100
    plt.figure(figsize=(21, 6))
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    plt.gca().xaxis.set_major_locator(mdates.DayLocator())
    date_dataframe = btc_usd.axes[0].to_frame(index=False)
    date = date_dataframe['date']
    strategy = ['SELL']*btc_usd.size
    for x in range(1, btc_usd.size):
        trend_diff = btc_usd.iloc[x] - btc_usd.iloc[x-1]
        if btc_usd.iloc[x-1] == 0.0:
            trend_rate = 0
        else:
            trend_rate = trend_diff / btc_usd.iloc[x-1]
        price_diff = price.iloc[x] - price.iloc[x-1]
        if price.iloc[x-1] == 0.0:
            price_rate = 0
        else:
            price_rate = price_diff / price.iloc[x-1]
        if trend_rate > 0.10:
            if price_rate > 0.03:
                strategy[x] = 'BUY'
    dic = {'BUY': 100, 'SELL': -100}
    strategy = pd.Series(strategy)
    strategy = strategy.map(dic)
    plt.plot(date, price)
    plt.plot(date, btc_usd)
    plt.plot(date, strategy, '^')
    plt.gcf().autofmt_xdate()
    plt.title('recent 3 month gtrend-price')
    plt.legend(['price (normalized)', 'btc_usd', 'strategy'])
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    graph_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    return graph_url

if __name__ == '__main__':
    APP.run()
