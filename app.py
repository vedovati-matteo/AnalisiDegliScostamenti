from flask import Flask, render_template

app = Flask(__name__)

#exec(open('analisiScostamenti.py').read())

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/analisiScostamenti")
def analisiScostamenti():
    return render_template("analisiScostamenti.html", p=((407000,67840,242200,80000,16960),(366300,61056,217000,80000,7264),(363500,60160,217000,80000,6340),(370000,63920,220780,80000,5300)))

@app.route("/listaArticoliFinali")
def listaArticoliFinali():
    return render_template("listaArticoliFinali.html", p=(("ART000025",15),("ART000525",17),("ART000016",528),("ART005118",-288),("ART000845",5),("ART000954",-238),("ART000231",34)))

@app.route("/articoloSpecifico")
def articoloSpecifico():
    return render_template("articoloSpecifico.html", codiceArticolo='ART000045', cliente="pippo", p=(((0.2761111111111111,17.708333333333332,18.0,323.71999999999997,40,36.91869841571008,1476.7479366284033),(17.65463917525773, 97.0, 1712.5, 88, 34.52013674643542, 3037.7720336863167,1516.7479366284033))))

@app.route("/scostamentoVolumi")
def scostamentoVolumi():
    return render_template("scostamentoVolumi.html", p=((407000,456000),(456000,407000)))

@app.route("/scostamentoMix")
def scostamentoMix():
    return render_template("scostamentoMix.html", p=(('ART000045',61056,407000,456000),('ART000086',61056,363500,220780),('ART000015',63920,407000,6340)))


if __name__ == '__main__':
	app.run(host='127.0.0.1', port=5000, debug=True)
