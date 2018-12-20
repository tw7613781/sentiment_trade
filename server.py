'''
server provide a web server to host a data visualization and analysis
'''

import sqlite3
import base64
from io import BytesIO
from matplotlib import pyplot as plt
from flask import Flask, render_template
import pandas as pd
import numpy as np

APP = Flask(__name__)


# @APP.route('/')
# def index():
#     '''
#     provide route logic for '/' 
#     '''
#     cnx = sqlite3.connect('history.db')
#     cmd = 'SELECT * FROM history ORDER BY date'
#     data_frame = pd.read_sql_query(cmd, cnx)
#     date = data_frame.date
#     bit_usd = data_frame.bit_usd
#     buy_bitcoin = data_frame.buy_bitcoin
#     price = data_frame.price
#     change_rate = data_frame.change_rate
#     # strategy = data_frame.strategy
#     img = BytesIO()
#     plt.plot(date, bit_usd)
#     plt.plot(date, buy_bitcoin)
#     plt.plot(date, price)
#     plt.plot(date, change_rate)
#     plt.title('sentiment trade')
#     plt.legend(['bit_usd gtrend', 'buy_bitcoin gtrend', 
#                 'price (10000 KoreanWon)', 'change rate with previous day'])
#     plt.savefig(img, format='png')

#     html = """<html><body>
# <img src="data:image/png;base64,{}"/> 
# </body></html>""".format(base64.encodebytes(img.getvalue()).decode())

#     return html

if __name__ == '__main__':
#     APP.run()
    cnx = sqlite3.connect('history.db')
    cmd = 'SELECT * FROM history ORDER BY date'
    data_frame = pd.read_sql_query(cmd, cnx)
    date = data_frame.date
    bit_usd = data_frame.bit_usd.astype(np.int64)
    buy_bitcoin = data_frame.buy_bitcoin.astype(np.int64)
    price = data_frame.price.astype(np.int64)
    change_rate = data_frame.change_rate.astype(np.int64)
    # strategy = data_frame.strategy
    img = BytesIO()
    plt.plot(date, bit_usd)
    plt.plot(date, buy_bitcoin)
    plt.plot(date, price)
    plt.plot(date, change_rate)
    plt.title('sentiment trade')
    plt.legend(['bit_usd gtrend', 'buy_bitcoin gtrend', 
                'price (10000 KoreanWon)', 'change rate with previous day'])   
    plt.show() 
