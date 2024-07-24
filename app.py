from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def hello_world():
    # Pass dynamic data for HTML templating as named parameters.
    return render_template("index.html", name="Tyler")
