from flask import Flask, render_template, request, Response, jsonify
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

socketio = SocketIO(app)
configs = Properties()

# adding configuration for using a sqlite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
# Creating an SQLAlchemy instance
db = SQLAlchemy(app)
# Settings for migrations
migrate = Migrate(app, db)

class StockNameEnum(enum.Enum):
    ibm = "ibm"
    msft = "msft"
    tsla = "tsla"
    race = "race"

class PurchaseType(enum.Enum):
    BUY = "BUY"
    SELL = "SELL"


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

    def to_dict(self):
        return {
            'id': self.id,
            'buy_sell': self.buy_sell,
            'order_type': self.order_type,
            'price': self.price,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'stock_name': self.stock_name.name if self.stock_name else None,
            'username': self.username
        }

    def __repr__(self):
        return f"<Trade {self.stock_name} {self.buy_sell} {self.price} {self.timestamp} >"


AVAILABLE_STOCKS = ["ibm", "msft", "tsla", "race"]

# In seconds
POLLING_INTERVAL = 3

current_stock = "ibm"

# At the start of your file
current_stock_lock = Lock()

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


@app.route('/all-trades', methods=['GET'])
def get_trades():
    trades = Trades.query.all()
    trades_list = [trade.to_dict() for trade in trades]
    return jsonify({"trades": trades_list})


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/signup')
def signup():
    return render_template('signup.html')


@app.route("/buy-stock", methods=['POST'])
def buy_stock():
    return process_trade(PurchaseType.BUY, request.get_json())


@app.route("/sell-stock", methods=['POST'])
def sell_stock():
    return process_trade(PurchaseType.SELL, request.get_json())


def process_trade(buy_or_sell, data):
    is_buying = buy_or_sell == PurchaseType.BUY

    # Check if data was received correctly
    if not data:
        return jsonify({"error": "Invalid or missing JSON"}), 400

    # Process the data (for example, print it or use it)
    username = data.get('username')
    symbol = data.get('symbol')
    price = data.get('price')
    time = data.get('time')

    if is_buying:
        print(f'Buying stock {symbol} for user {username}!')
    else:
        print(f'Selling stock {symbol} for user {username}!')

    stock_name = None

    match symbol:
        case 'ibm':
            stock_name = StockNameEnum.ibm
        case 'tsla':
            stock_name = StockNameEnum.tsla
        case 'msft':
            stock_name = StockNameEnum.msft
        case 'race':
            stock_name = StockNameEnum.race

    new_trade = Trades(buy_sell=is_buying, order_type='market', price=price, timestamp=datetime.utcfromtimestamp(int(time)),
                       stock_name=stock_name, username=username)
    db.session.add(new_trade)
    db.session.commit()

    if is_buying:
        print(f'Bought stock {symbol} for user {username}!')
    else:
        print(f'Sold stock {symbol} for user {username}!')


    # Respond back with a success message or some processed result
    return jsonify({"message": "Trade processed", "data": data}), 200

# socket IO
@socketio.on('connect')
def handle_connect():
    send('A new user has connected.', broadcast=True)
    socketio.emit('stock-info-update', current_stock)


# @socketio.on('select-stock')
# def handle_select_stock(data):
#     global current_stock
#     current_stock = data
#     socketio.emit('stock-info-update', current_stock)
#     print(f'SELECTED STOCK {data}! CURRENT STOCK: {current_stock}')

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
# def background_thread():
#     while True:
#         global current_stock
#         print(f'WOOOOO')
#         current_stock_data = get_stock_data(current_stock)
#
#         print(f'CURRENT STOCK IN BACKGROUND THREAD: {current_stock}')
#         if 'error' in current_stock_data or current_stock_data.get('symbol').lower() == current_stock:
#             socketio.emit('stock_update', current_stock_data)
#
#         time.sleep(POLLING_INTERVAL)

@socketio.on('select-stock')
def handle_select_stock(data):
    global current_stock
    with current_stock_lock:
        current_stock = data
    socketio.emit('stock-info-update', current_stock)
    print(f'SELECTED STOCK {data}! CURRENT STOCK: {current_stock}')

def background_thread():
    global current_stock
    while True:
        with current_stock_lock:
            stock_to_fetch = current_stock
        print(f'Fetching data for {stock_to_fetch}')
        current_stock_data = get_stock_data(stock_to_fetch)

        if 'error' not in current_stock_data:
            print(f'CURRENT STOCK IN BACKGROUND THREAD: {stock_to_fetch}')
            socketio.emit('stock_update', current_stock_data)

        time.sleep(POLLING_INTERVAL)



if __name__ == '__main__':
    thread = Thread(target=background_thread)
    thread.daemon = True
    thread.start()

    socketio.run(app, allow_unsafe_werkzeug=True)