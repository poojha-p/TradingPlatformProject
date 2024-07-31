from flask import Flask, render_template, request, Response
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, migrate
from flask_socketio import SocketIO, send
from jproperties import Properties
from datetime import datetime
import enum
import requests
import json
from threading import Thread, Lock
import time

app = Flask(__name__)
app.debug = True
socketio = SocketIO(app)
configs = Properties()

# adding configuration for using a sqlite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
# Creating an SQLAlchemy instance
db = SQLAlchemy(app)
# Settings for migrations
migrate = Migrate(app, db)

class StockNameEnum(enum.Enum):
    ibm =  "ibm"
    msft = "msft"
    tsla = "tsla"
    race = "race"


#create Models
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(60), nullable=False)
    email = db.Column(db.String(200), nullable=False, unique =True)
    trades = db.relationship('Trades', backref='user', lazy=True)

    def __repr__(self):
        return f"Name : {self.username}, ID: {self.id}"

class Trades(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    buy_sell = db.Column(db.Boolean, nullable=False)  
    order_type = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now)
    stock_name = db.Column(db.Enum(StockNameEnum), nullable=False)
    username = db.Column(db.String(50), db.ForeignKey('users.username'), nullable=False)

    def __repr__(self):
        return f"<Trade {self.stock_name} {self.buy_sell} {self.price} {self.timestamp} >"

AVAILABLE_STOCKS = ["ibm", "msft", "tsla", "race"]

# In seconds
POLLING_INTERVAL = 3

current_stock = "ibm"

# Load in config file.
with open('app-config.properties', 'rb') as config_file:
    try:
        configs.load(config_file, "utf-8")
        API_KEY = configs.get("API_KEY").data
    except Exception as e:
        print(f"Error loading config file: {e}")

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

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

# socket IO
@socketio.on('connect')
def handle_connect():
    send('A new user has connected.', broadcast=True)
    socketio.emit('stock-info-update', current_stock)


@socketio.on('select-stock')
def handle_select_stock(data):
    global current_stock
    current_stock = data
    socketio.emit('stock-info-update', current_stock)

""" @socketio.on('select-stock')
def handle_select_stock(data):
    current_stock_data = get_stock_data(data)
    socketio.emit('stock-info-update', current_stock_data)
 """
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
