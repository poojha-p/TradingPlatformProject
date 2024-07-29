import requests
import json
from threading import Thread, Lock
import time

from flask import Flask, render_template, request, Response
from flask_socketio import SocketIO, send
from jproperties import Properties

app = Flask(__name__)
socketio = SocketIO(app)
configs = Properties()

AVAILABLE_STOCKS = ["ibm", "msft", "tsla", "race"]

# In seconds
POLLING_INTERVAL = 3

current_stock = "ibm"

# Load in config file.
with open('app-config.properties', 'rb') as config_file:
    configs.load(config_file)

API_KEY = configs.get("API_KEY").data

# Homepage
@app.route("/")
def hello_world():
    # Pass dynamic data for HTML templating as named parameters.
    return render_template("index.html")


# API endpoints
@app.route("/all-stocks", methods=['GET'])
def get_all_stock_prices_endpoint():
    return Response(response=get_all_stock_data_as_json(), status=200, mimetype='application/json')


@app.route("/stock", methods=['GET'])
def get_stock_data_endpoint():
    stock = request.args.get("stock")
    return Response(response=get_stock_data_as_json(stock), status=200, mimetype='application/json')


# socket IO
@socketio.on('connect')
def handle_connect():
    send('A new user has connected.', broadcast=True)
    socketio.emit('selected-stock-update', current_stock)


@socketio.on('select-stock')
def handle_select_stock(data):
    global current_stock
    current_stock = data
    socketio.emit('selected-stock-update', current_stock)


# Logic
def get_all_stock_data_as_json():
    return json.dumps({"stocks": get_all_stock_data()})


def get_stock_data_as_json(stock):
    return json.dumps(get_stock_data(stock))


def get_all_stock_data():
    stocks_list = []

    for stock in AVAILABLE_STOCKS:
        stocks_list.append(dict(get_stock_data(stock)))

    return list(stocks_list)


# Call to Echios API made here.
def get_stock_data(stock):
    try:
        print("pinging API")
        http_response = requests.get(f'https://echios.tech/price/{stock}?apikey={API_KEY}')

        json_response = http_response.json()

        print(f'Length: {len(json_response)}')
        if not json_response:
            print("DID NOT RECIEVE REPSONSE")

        print(json_response)

        return {
            "symbol": json_response["symbol"],
            "price": json_response["price"],
            "time": json_response["time"]
        }
    except requests.exceptions.RequestException as e:
        print('ERROR! REQUEST EXCEPTION: ', str(e))
        return {
            "error": f'Could not fetch stock price for {stock}.'
        }


# Background thread that polls the Echios API (based on the POLLING_INTERVAL) for the selected stock.
def background_thread():
    while True:
        current_stock_data = get_stock_data(current_stock)

        if 'error' in current_stock_data or current_stock_data.get('symbol').lower() == current_stock:
            socketio.emit('stock_update', current_stock_data)

        time.sleep(POLLING_INTERVAL)


if __name__ == '__main__':
    thread = Thread(target=background_thread)
    thread.daemon = True
    thread.start()

    socketio.run(app, allow_unsafe_werkzeug=True)
