import requests
import json
def get_google_trend():
    url = '''
    https://trends.google.com/trends/api/widgetdata/multiline?hl=zh-CN&tz=-540&req=%7B%22time%22:%222018-11-12T08%5C%5C:01%5C%5C:42+2018-11-13T08%5C%5C:01%5C%5C:42%22,%22resolution%22:%22EIGHT_MINUTE%22,%22locale%22:%22zh-CN%22,%22comparisonItem%22:%5B%7B%22geo%22:%7B%7D,%22complexKeywordsRestriction%22:%7B%22keyword%22:%5B%7B%22type%22:%22BROAD%22,%22value%22:%22BTC+USD%22%7D%5D%7D%7D,%7B%22geo%22:%7B%7D,%22complexKeywordsRestriction%22:%7B%22keyword%22:%5B%7B%22type%22:%22BROAD%22,%22value%22:%22buy+bitcoin%22%7D%5D%7D%7D%5D,%22requestOptions%22:%7B%22property%22:%22%22,%22backend%22:%22CM%22,%22category%22:0%7D%7D&token=APP6_UEAAAAAW-vWZo26XLYFBBBQfdDOz29BzCyw27d0&tz=-540
    '''
    try:
        r = requests.get(url, timeout = 5)
        data = json.loads(r.text[5:], encoding="utf-8")
        return (data['default']['averages'])
    except Exception as e:
        print(f'Error when get_google_trend: {e}')

def get_krw_btc_from_upbit():
    url = 'https://api.upbit.com/v1/candles/days?market=KRW-BTC'
    try:
        r = requests.get(url, timeout = 5)
        data = json.loads(r.text, encoding="utf-8")
        return (data[0]['opening_price'], data[0]['change_price'])
    except Exception as e:
        print(f'Error when get_krw_btc_from_upbit: {e}')


if __name__ == '__main__':
    trend = get_google_trend()
    message = f'BTC USD : buy bitcion = {trend}, rate is {trend[1] / trend[0]}'
    price = get_krw_btc_from_upbit()
    print(message)
    print(price)
