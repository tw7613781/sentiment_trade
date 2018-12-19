import sqlite3
import base64
from io import StringIO
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
    img = StringIO()
    plt.plot(date, int(bit_usd))
    plt.plot(date, int(buy_bitcoin))
    plt.plot(date, int(price / 10000))
    plt.plot(date, int(change_rate))
    plt.savefig(img, format='png')
    img.seek(0)

    plot_url = base64.b64encode(img.getvalue())

    return render_template('index.html', plot_url=plot_url)

if __name__ == '__main__':
    APP.run()
