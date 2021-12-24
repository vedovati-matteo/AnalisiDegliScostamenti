from flask import Flask, render_template, request
import pandas as pd
import functions as fun

app = Flask(__name__)

exec(open('analisiScostamenti.py').read())

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/analisiScostamenti")
def analisiScostamenti():
    return render_template("analisiScostamenti.html", p=tabellaScostamenti)

@app.route("/listaArticoliFinali")
def listaArticoliFinali():
    return render_template("listaArticoliFinali.html", p=artScost.values.tolist())

@app.route("/articoloSpecifico", methods=['GET'])
def articoloSpecifico():
    nrArticolo = request.args.get('codiceArticolo')
    return render_template("articoloSpecifico.html", nrArticolo = nrArticolo, cliente = fun.getCliente(nrArticolo, df_articoli), valuta = fun.getValuta(nrArticolo, df_ricavi_b), p = fun.articoloFinale(nrArticolo, df_valuta_b, df_valuta_c, df_costo_b, df_costo_c, df_ricavi_b, df_ricavi_c))


@app.route("/scostamentoVolumi")
def scostamentoVolumi():
    return render_template("scostamentoVolumi.html", p=((407000,67840,242200,80000,16960),(366300,61056,217000,80000,7264),(363500,60160,217000,80000,6340),(370000,63920,220780,80000,5300)))


if __name__ == '__main__':
	app.run(host='127.0.0.1', port=5000, debug=True)
