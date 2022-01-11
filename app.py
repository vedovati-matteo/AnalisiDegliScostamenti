from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import functions as fun

app = Flask(__name__)

exec(open('analisiScostamenti.py').read())

@app.route("/")
def index():
    return redirect(url_for("analisiScostamenti"))

@app.route("/analisiScostamenti")
def analisiScostamenti():
    return render_template("analisiScostamenti.html", p=tabellaScostamenti)

@app.route("/listaArticoliVenduti")
def listaArticoliFinali():
    return render_template("listaArticoliVenduti.html", p=artScost.values.tolist())

@app.route("/articoloSpecifico", methods=['GET'])
def articoloSpecifico():
    nrArticolo = request.args.get('codiceArticolo')
    return render_template("articoloSpecifico.html", nrArticolo = nrArticolo, cliente = fun.getCliente(nrArticolo, df_articoli), valuta = fun.getValuta(nrArticolo, df_ricavi_b), p = fun.articoloFinale(nrArticolo, df_valuta_b, df_valuta_c, df_costo_b1, df_costo_c1, df_ricavi_b, df_ricavi_c))


@app.route("/scostamentoVolumi")
def scostamentoVolumi():
    return render_template("scostamentoVolumi.html", volumi = volumi, delta_volumi = delta_volumi)


@app.route("/scostamentoMixCosto")
def scostamentoMixCosto():
    return render_template("scostamentoMix.html", t='Costi', delta = delta_mix_c,p=mix_scostamento_c.values.tolist())

@app.route("/scostamentoMixVendita")
def scostamentoMixVendita():
    return render_template("scostamentoMix.html", t='Ricavi', delta = delta_mix_v, p=mix_scostamento_v.values.tolist())

@app.route("/scostamentoMD")
def scostamentoMD():
    return render_template("scostamentoDiretto.html", t='Materiale Diretto',delta = delta_md, p=md_scostamento.values.tolist())

@app.route("/scostamentoLD")
def scostamentoLD():
    return render_template("scostamentoDiretto.html", t='Lavoro Diretto',delta = delta_ld, p=ld_scostamento.values.tolist())

@app.route("/scostamentoCosti")
def scostamentoCosti():
    return render_template("scostamentoCostiTotali.html", delta = delta_costi, p=costi_scostamento.values.tolist())

@app.route("/scostamentoPrezzo")
def scostamentoPrezzo():
    return render_template("scostamentoPrezzo.html",delta = (delta_valuta, delta_ricavi), v=valuta_scostamento, p=ricavi_scostamento.values.tolist())

@app.route("/assunzioni")
def assunzioni():
    return render_template("assunzioni.html",delta = (delta_valuta, delta_ricavi), v=valuta_scostamento, p=ricavi_scostamento.values.tolist())


if __name__ == '__main__':
	app.run(host='127.0.0.1', port=5000, debug=True)
