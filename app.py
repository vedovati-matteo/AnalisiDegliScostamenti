from flask import Flask, render_template

app = Flask(__name__)

exec(open('analisiScostamenti.py').read())

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/analisiScostamenti")
def analisiScostamenti():
    return render_template("home.html", p=tabellaScostamenti)

@app.route("/listaArticoliFinali")
def listaArticoliFinali():
    return render_template("listaArticoliFinali.html", p=(("ART000025",15),("ART000525",17),("ART000016",528),("ART005118",-288),("ART000845",5),("ART000954",-238),("ART000231",34)))

@app.route("/articoloSpecifico")
def articoloSpecifico():
    return render_template("articoloSpecifico.html", p=((407000,67840,242200,80000,16960),(366300,61056,217000,80000,7264),(363500,60160,217000,80000,6340),(370000,63920,220780,80000,5300)))


if __name__ == '__main__':
	app.run(host='127.0.0.1', port=5000, debug=True)