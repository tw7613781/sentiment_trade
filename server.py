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
from main import get_google_trend_detail
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
    bit_usd = data_frame.bit_usd.astype(np.float)
    buy_bitcoin = data_frame.buy_bitcoin.astype(np.float)
    price = data_frame.price.astype(np.float)
    change_rate = data_frame.change_rate.astype(np.float)*100
    dic = {'BUY': 100, 'SELL': -100}
    strategy = data_frame.strategy.map(dic)
    plt.figure(figsize=(15, 6))
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%Y'))
    plt.gca().xaxis.set_major_locator(mdates.DayLocator())
    plt.plot(date, price/100000)
    plt.plot(date, bit_usd)
    plt.plot(date, buy_bitcoin)
    plt.plot(date, change_rate, '.')
    plt.plot(date, strategy, '^')
    plt.gcf().autofmt_xdate()
    plt.title('sentiment trade')
    plt.legend(['price (100000 KRW)', 'bit_usd gtrend',
                'buy_bitcoin gtrend', 'change rate with previous day',
                'strategy'])
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
    (btc_usd, buy_bitcoin) = get_google_trend_detail()
    plt.figure(figsize=(15, 6))
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%Y-%H:%M:%S'))
    plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=4))
    date_dataframe = btc_usd.axes[0].to_frame(index=False)
    date = date_dataframe['date']
    plt.plot(date, btc_usd)
    plt.plot(date, buy_bitcoin)
    plt.gcf().autofmt_xdate()
    plt.title('recent 7 days gtrend')
    plt.legend(['btc_usd', 'buy_bitcoin'])
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    graph_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    return graph_url

if __name__ == '__main__':
    APP.run()
