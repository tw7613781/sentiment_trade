import sqlite3
import base64
from io import BytesIO
from matplotlib import pyplot as plt
from flask import Flask, render_template
import pandas as pd

APP = Flask(__name__)


@APP.route('/')
def index():
    cnx = sqlite3.connect('history.db')
    cmd = 'SELECT * FROM history ORDER BY date'
    df = pd.read_sql_query(cmd, cnx)
    date = df.date
    bit_usd = df.bit_usd
    buy_bitcoin = df.buy_bitcoin
    price = df.price
    change_rate = df.change_rate
    strategy = df.strategy
    img = BytesIO()
    plt.plot(date, bit_usd)
    plt.plot(date, buy_bitcoin)
    plt.plot(date, price)
    plt.plot(date, change_rate)
    plt.title('sentiment trade')
    plt.legend(['bit_usd gtrend', 'buy_bitcoin gtrend', 'price (10000 KoreanWon)', 'change rate with previous day'])
    plt.savefig(img, format='png')

    html = """<html><body> 
<img src="data:image/png;base64,{}"/> 
</body></html>""".format(base64.encodebytes(img.getvalue()).decode())

    return html

if __name__ == '__main__':
    APP.run()
