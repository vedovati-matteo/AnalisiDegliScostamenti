from flask import Flask, render_template

app = Flask(__name__)

prova = "Ciao"

@app.route("/")
def hello_world():
    return render_template("home.html", p=(('c', 'a', 'c', 'a'),('p','i','p','p')))

if __name__ == '__main__':
	app.run(host='127.0.0.1', port=5000, debug=True)