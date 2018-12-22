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
APP = Flask(__name__)


@APP.route('/')
def index():
    '''
    provide route logic for '/'
    '''
    graph_url_main = create_graph_main()
    return render_template('index.html', graph_url_main=graph_url_main)

def create_graph_main():
    '''
    create a analysis figure based on collected data and save it to memory as Bytes
    '''
    cnx = sqlite3.connect('history.db')
    cmd = 'SELECT * FROM history ORDER BY date'
    data_frame = pd.read_sql_query(cmd, cnx)
    date = pd.to_datetime(data_frame['date'])
    btc_usd = data_frame.btc_usd.astype(np.float)
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
    plt.plot(date, price_rate * 100, '.')
    plt.plot(date, btc_usd)
    plt.plot(date, btc_usd_rate * 100, '*')
    plt.plot(date, strategy, '^')
    plt.axhline(y=0, color='k')
    plt.gcf().autofmt_xdate()
    plt.title('sentiment trade')
    plt.legend(['price(normalized)', 'price change rate', 
                'btc usd gtrend value', 'btc usd gtrend change rate', 'strategy'])
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    graph_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    return graph_url

if __name__ == '__main__':
    APP.run()
