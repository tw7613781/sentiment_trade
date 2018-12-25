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
from main import get_google_trend_detail, get_krw_btc_from_upbit_detail, get_google_trend_7_days, get_krw_btc_from_upbit_7_days
APP = Flask(__name__)


@APP.route('/')
def index():
    '''
    provide route logic for '/'
    '''
    graph_url_main = create_graph_main()
    graph_url_gtrend = create_graph_gtrend()
    graph_url_simulation = create_graph_simulation()
    return render_template('index.html', graph_url_main=graph_url_main,
                           graph_url_gtrend=graph_url_gtrend,
                           graph_url_simulation=graph_url_simulation)

def create_graph_main():
    '''
    create a analysis figure based on collected data and save it to memory as Bytes
    '''
    cnx = sqlite3.connect('history.db')
    cmd = 'SELECT * FROM history ORDER BY date'
    data_frame = pd.read_sql_query(cmd, cnx)
    date = pd.to_datetime(data_frame['date'])
    btc_usd_rate = data_frame.btc_usd_rate.astype(np.float)
    price = data_frame.price.astype(np.float)
    price_rate = data_frame.price_rate.astype(np.float)
    strategy = data_frame.strategy
    dic = {'BUY': 100, 'SELL': -100}
    strategy = strategy.map(dic)
    price = (price - price.min()) / (price.max() - price.min()) * 100
    plt.figure(figsize=(15, 6))
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%Y'))
    plt.gca().xaxis.set_major_locator(mdates.DayLocator())
    plt.plot(date, price)
    plt.plot(date, btc_usd_rate * 100)
    plt.plot(date, price_rate * 100, '*')
    plt.plot(date, strategy, '^')
    plt.axhline(y=0, color='k')
    plt.gcf().autofmt_xdate()
    plt.title('sentiment trade')
    plt.legend(['price(normalized)', 'btc usd gtrend changes', 
                'price change rate', 'strategy'])
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    graph_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    return graph_url

def create_graph_gtrend():
    '''
    create a figure base on recent 7 days gtrend data
    '''
    price_list = get_krw_btc_from_upbit_detail()
    price = pd.Series(price_list)
    price = (price - price.min()) / (price.max() - price.min()) * 100
    btc_usd = get_google_trend_detail()
    diff_rate = [0] * btc_usd.size
    price_rate = [0] * btc_usd.size
    for x in range(1, btc_usd.size):
        diff = btc_usd.iloc[x] - btc_usd.iloc[x-1]
        diff_rate_temp = diff / btc_usd.iloc[x-1]
        diff_rate[x] = diff_rate_temp
        diff_price_temp = price_list[x] - price_list[x-1]
        diff_price_rate_temp = diff_price_temp / price_list[x-1]
        price_rate[x] = diff_price_rate_temp
    diff_rate_serise = pd.Series(diff_rate)
    price_rate_serise = pd.Series(price_rate)
    plt.figure(figsize=(15, 6))
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%Y-%H:%M:%S'))
    plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=4))
    date_dataframe = btc_usd.axes[0].to_frame(index=False)
    date = date_dataframe['date']
    plt.plot(date, price)
    plt.plot(date, diff_rate_serise * 100)
    plt.plot(date, price_rate_serise * 100, '*')
    plt.axhline(y=0, color='k')
    plt.gcf().autofmt_xdate()
    plt.title('recent 7 days gtrend')
    plt.legend(['price (normalized)', 'btc usd gtrend changes', 'price change rate'])
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    graph_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    return graph_url

def create_graph_simulation():
    '''
    create a figure base on recent 7 days gtrend data
    '''
    price_list = get_krw_btc_from_upbit_7_days()
    price = pd.Series(price_list)
    price = (price - price.min()) / (price.max() - price.min()) * 100
    btc_usd = get_google_trend_7_days()
    diff_rate = [0] * len(btc_usd)
    price_rate = [0] * len(btc_usd)
    strategy = [-100] * len(btc_usd)
    for x in range(1, len(btc_usd)):
        diff = btc_usd[x] - btc_usd[x-1]
        diff_rate_temp = diff / btc_usd[x-1]
        diff_rate[x] = diff_rate_temp
        diff_price_temp = price_list[x] - price_list[x-1]
        diff_price_rate_temp = diff_price_temp / price_list[x-1]
        price_rate[x] = diff_price_rate_temp
        if diff_rate_temp > 0.25 and diff_price_rate_temp > 0.01:
            strategy[x] = 100
    diff_rate_serise = pd.Series(diff_rate)
    price_rate_serise = pd.Series(price_rate)
    plt.figure(figsize=(15, 6))
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%Y-%H:%M:%S'))
    plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=4))
    x_axis = range(7)
    plt.plot(x_axis, price)
    plt.plot(x_axis, diff_rate_serise * 100)
    plt.plot(x_axis, price_rate_serise * 100, '*')
    plt.plot(x_axis, strategy, '^')
    plt.axhline(y=0, color='k')
    plt.gcf().autofmt_xdate()
    plt.title('recent 7 days gtrend')
    plt.legend(['price (normalized)', 'btc usd gtrend changes', 'price change rate', 'strategy'])
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    graph_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    return graph_url

if __name__ == '__main__':
    APP.run()
