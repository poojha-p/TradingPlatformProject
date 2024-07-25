import requests
from flask import Flask, render_template
import time

app = Flask(__name__)

AVAILABLE_STOCKS = ["ibm", "msft", "tsla", "race"]

# In seconds
POLLING_INTERVAL = 3

# TODO: RETRIEVE FROM EXTERNAL FILE
# DO NOT PUSH TO REPO
API_KEY = None

@app.route("/")
def hello_world():
    current_stock_data = get_all_stock_prices()
    # Pass dynamic data for HTML templating as named parameters.
    return render_template("index.html", stock_data=current_stock_data)


# Returns a dictionary of stock prices from the API.
def get_all_stock_prices():
    stocks_list = []

    for stock in AVAILABLE_STOCKS:
        stocks_list.append(get_stock_data(stock))

    return {
        "stocks": stocks_list
    }


def get_stock_data(stock):
    try:
        http_response = requests.get(f'https://echios.tech/price/{stock}?apikey={API_KEY}')
        json_response = http_response.json()

        return {
            "symbol": json_response["symbol"],
            "price": json_response["price"],
            "time": json_response["time"]
        }
    except requests.exceptions.RequestException as e:
        return {
            "error": f'Could not fetch stock price for {stock}.'
        }
