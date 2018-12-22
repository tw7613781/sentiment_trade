from main import get_google_trend, get_krw_btc_from_upbit

(x, y) = get_google_trend()
print(x, y)
(x, y) = get_krw_btc_from_upbit()
print(x, y)