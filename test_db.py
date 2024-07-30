from app import app, db, Users, Trades, StockNameEnum

with app.app_context():
    
    db.create_all()

    # Create some users
    user1 = Users(username='john_doe', password='password123', email='john@example.com')
    user2 = Users(username='jane_doe', password='password456', email='jane@example.com')

    # Add users to the session
    db.session.add(user1)
    db.session.add(user2)

    # Commit the session
    db.session.commit()

    # Query the users
    users = Users.query.all()
    print("All Users:", users)

    # Create some trades
    trade1 = Trades(buy_sell=True, order_type='market', price=150.0, stock_name=StockNameEnum.ibm, username='john_doe')
    trade2 = Trades(buy_sell=False, order_type='limit', price=250.0, stock_name=StockNameEnum.tsla, username='jane_doe')

    # Add trades to the session
    db.session.add(trade1)
    db.session.add(trade2)

    # Commit the session
    db.session.commit()

    # Query the trades
    trades = Trades.query.all()
    print("All Trades:", trades)

    # Clean up / delete the created records for testing purposes
    Users.query.delete()
    Trades.query.delete()
    db.session.commit()
