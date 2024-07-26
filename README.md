# Setup requirements

## Dependencies
- Use the command `pip install -r requirements.txt` to install dependencies.

## Config Properties
- Create an `app-config.properties` file with key-value pair API_KEY=[INSERT API KEY HERE].

# Additional Notes

**IMPORTANT**
- There seems to be a problem with the Echios API which happens occasionally, but it seems to fix itself, you just have to wait for a valid response to come through. 
- I believe that the API is sometimes returning an invalid JSON response due to throttling (even though we are requesting every 3 seconds which is within the limit). 
- However, there may be another reason this is happening that I am unaware of.

## Resources on HTML templating 
- https://www.geeksforgeeks.org/flask-rendering-templates/
- https://flask.palletsprojects.com/en/3.0.x/tutorial/templates/

## SocketIO Websockets

1. Frontend Javascript client connects to socket.
2. Backend returns connect message to tell client it has connected.
3. Backend polls Echios API every 3 seconds and emits stock data on the `stock_update` channel.
4. Frontend listens to `stock_update` channel to receive the data.
5. The default stock selected is ibm and is emitted on the `selected-stock-update` channel. Whenever the selected stock has been updated, a message will be emitted from this channel.
6. To change the selected stock, the frontend should emit a message on the `select-stock` channel.


# API Documentation
## Retrieve most recent stock data for all stocks

Returns the most recent stock data for all stocks in the Echios API. Available stocks are:
- ibm
- msft
- tsla
- race

**URL** : `/all-stocks`

**Method** : `GET`

## Success Response Example

**Request** : `http://127.0.0.1:5000/all-stocks`

**Code** : `200 OK`

**Content examples**

```json
{
    "stocks": [
        {
            "symbol": "IBM",
            "price": 179.77,
            "time": 1721999789
        },
        {
            "symbol": "MSFT",
            "price": 406.79,
            "time": 1721999789
        },
        {
            "symbol": "TSLA",
            "price": 143.87,
            "time": 1721999789
        },
        {
            "symbol": "RACE",
            "price": 424.97,
            "time": 1721999790
        }
    ]
}
```

## Retrieve most recent stock data for a specific stock

Returns the most recent stock data for a specific stock in the Echios API. Available stocks are:
- ibm
- msft
- tsla
- race

**URL** : `/stock`

**(REQUIRED)**
**Query Parameters** : `stock`

**Method** : `GET`

## Success Response Example

**Request** : `http://127.0.0.1:5000/stock?stock=msft`

**Code** : `200 OK`

**Content examples**

```json
{
    "symbol": "MSFT",
    "price": 407.51,
    "time": 1721999922
}
```

