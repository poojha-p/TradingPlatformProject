# Dependencies
- Use the command `pip install -r requirements.txt` to install dependencies.

# Running the app
- Use the command `flask run`.

# Resources on HTML templating 
- https://www.geeksforgeeks.org/flask-rendering-templates/
- https://flask.palletsprojects.com/en/3.0.x/tutorial/templates/

# Additional Notes
- HTML files must be placed in the /templates directory to be picked up by the templating engine.

# Database
- Use the command `pip install -r requirements.txt` to install dependencies.
- Use the command `flask db upgrade`, a sqlite file named database.db would be created under folder "instance"
- Test the database by running python3 test_db.py. Output should be something like this:
    All Users: [Name : john_doe, ID: 1, Name : jane_doe, ID: 2]
    All Trades: [<Trade StockNameEnum.ibm True 150.0 2024-07-26 15:30:44.873919 >, <Trade StockNameEnum.tsla False 250.0 2024-07-26 15:30:44.873925 >]
