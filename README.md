
# Idea
The v0.1 version strategy has been run for more than 1 month, I analyzed the data and visualize it on my [blog](https://www.cnblogs.com/wtang/p/10155771.html), found that "buy bitcoin " has no correlation with bitcoin price. In the new strategy, I simplified varialbe, only the "btc usd" gtrend value be collected and the general relation with bitcoin price is that the higher value the key word is, the more changes the price will be. It could be rise, it could be drop. 

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


