# Setup requirements

## Dependencies
- Use the command `pip install -r requirements.txt` to install dependencies.

## Config Properties
- Create an `app-config.properties` file with key-value pair API_KEY=[INSERT API KEY HERE].

# Running the app
- Use the command `flask run`.

# Resources on HTML templating 
- https://www.geeksforgeeks.org/flask-rendering-templates/
- https://flask.palletsprojects.com/en/3.0.x/tutorial/templates/

# Additional Notes
- HTML files must be placed in the /templates directory to be picked up by the templating engine.

# API Documentation
## Retrieve most recent stock data for all stocks

Returns the most recent stock data for all stocks in the Echios API. Available stocks are:
- ibm
- msft
- tsla
- race

**URL** : `/all-stocks`

**Method** : `GET`

## Success Response

**Code** : `200 OK`

**Content examples**

```json
{
    "id": 1234,
    "first_name": "Joe",
    "last_name": "Bloggs",
    "email": "joe25@example.com"
}
```