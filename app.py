from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, migrate
from datetime import datetime
import enum

app = Flask(__name__)
app.debug = True

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

@app.route("/")
def hello_world():
    # Pass dynamic data for HTML templating as named parameters.
    return render_template("index.html", name="Tyler")