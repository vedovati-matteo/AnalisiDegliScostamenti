from flask import Flask, render_template

app = Flask(__name__)

prova = "Ciao"

@app.route("/")
def index():
    return render_template("home.html", p=((407000,67840,242200,80000,16960),(366300,61056,217000,80000,7264),(363500,60160,217000,80000,6340),(370000,63920,220780,80000,5300)))

if __name__ == '__main__':
	app.run(host='127.0.0.1', port=5000, debug=True)