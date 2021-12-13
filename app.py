from flask import Flask, render_template
from flask_bcrypt import Bcrypt

app = Flask(__name__)


@app.route("/")
def hello_world():
    return render_template("home.html")

if __name__ == '__main__':
	app.run(host='127.0.0.1', port=5000, debug=True)