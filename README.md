
# Idea

The idea behind the code is from [How I Created a Bitcoin Trading Algorithm Using Sentiment Analysis With a 29% Return](https://hackernoon.com/how-i-created-a-bitcoin-trading-algorithm-with-a-29-return-rate-using-sentiment-analysis-b0db0e777f4), which basically it predicts the price by google trend.

# Component
## Main   
* The main component collect data from local cryptocurrency exchange and google trend, make a prediction based on the article above 

## Web server
* Analysis collected data and visualize in a flask web server    
* [demo](http://13.125.213.49/)

# How to run the code

## dependencies
`
pip install -r requirements.txt
`

## run the code

## main component
`      
python main.py
`

## web server
`
python server.py
`

## using telegram to send message
to use telegram, it need a file named **config.py**
```
API_ID = 'your api id'
API_HASH = 'your api hash'
SESSION = 'any_name'
```

## Example output
> BTC USD : buy bitcion = (65.22346368715084, 29.6536312849162), rate is 0.45464668094218413 and UPBIT BTC/KRW open price is 7248000.0, change price is -16000.0, change rate is -0.0022075055, today strategy is SELL, reference with yesterday high 7254000.0, yesterday low 7220000.0


