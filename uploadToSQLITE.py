import sqlite3
import csv

conn = sqlite3.connect('dati.db')
c = conn.cursor()


c.execute('''
CREATE TABLE Consumo ( 
	nrMovimento INTEGER,
  	BC VARCHAR(10),
	tipoMovimento VARCHAR(7),
	codiceMP VARCHAR(10),
	tipoOrigine VARCHAR(8),
	nrArticolo VARCHAR(10),
	nrDocumento VARCHAR(11),
	quantitaMP INTEGER,
	importoTot FLOAT,
  	PRIMARY KEY (nrMovimento),
	FOREIGN KEY (nrArticolo, nrDocumento) REFERENCES Impiego_orario_risorse(nrArticolo, nrOrdineProduzione)
);
''')

file = open("csv/Consumi.csv")
csvreader = csv.reader(file)
next(csvreader)
rows = []
for row in csvreader:
    c.execute('INSERT INTO Consumo VALUES (' + row[0] + ', "' + row[1] + '", "' + row[2] + '", "' + row[3] + '", "' + row[4] + '", "' + row[5] + '", "' + row[6] + '", ' + row[7] + ', ' + row[8] + ');')

file.close()

c.execute('''
CREATE TABLE Costo_orario_risorse ( 
	risorsa VARCHAR(5),
  	areaProd VARCHAR(5),
	BC VARCHAR(10),
  	costoOrarioRis INTEGER,
  	PRIMARY KEY (risorsa, areaProd, BC)
  );
''')

file = open("csv/Costo orario risorse - budget.csv")
csvreader = csv.reader(file)
next(csvreader)
rows = []
for row in csvreader:
    c.execute('INSERT INTO Costo_orario_risorse VALUES ("' + row[0] + '", "' + row[1] + '", "BUDGET", ' + row[2] + ');')

file.close()

file = open("csv/Costo orario risorse - consuntivo.csv")
csvreader = csv.reader(file)
next(csvreader)
rows = []
for row in csvreader:
    c.execute('INSERT INTO Costo_orario_risorse VALUES ("' + row[0] + '", "' + row[1] + '", "CONSUNTIVO", ' + row[2] + ');')

file.close()

c.execute('''
CREATE TABLE Impiego_orario_risorse ( 
	id INTEGER AUTO_INCREMENT,
	nrArticolo VARCHAR(10),
  	BC VARCHAR(10),
	nrOrdineProduzione VARCHAR(11),
	descrizione VARCHAR(20),
	nrAreaProd VARCHAR(5),
	risorsa VARCHAR(5),
	tempoRisorsa FLOAT,
	quantitaOutput INTEGER,
  	PRIMARY KEY (id),
	FOREIGN KEY (nrAreaProd, risorsa, BC) REFERENCES Costo_orario_risorse(areaProd, risorsa, BC)
);
''')

file = open("csv/Impiego orario risorse.csv")
csvreader = csv.reader(file)
next(csvreader)
rows = []
for row in csvreader:
    c.execute('INSERT INTO Impiego_orario_risorse (nrArticolo, BC, nrOrdineProduzione, descrizione, nrAreaProd, risorsa, tempoRisorsa, quantitaOutput) VALUES ("' + row[0] + '", "' + row[1] + '", "' + row[2] + '", "' + row[3] + '", "' + row[4] + '", "' + row[5] + '", ' + row[6] + ', ' + row[7] + ');')

file.close()

c.execute('''
CREATE TABLE Valuta (
    codiceValuta int,
      BC varchar(10),
      tassoCambio float,
      PRIMARY KEY (codiceValuta, BC)
 );
 ''')

file = open("csv/Tassi di cambio.csv")
csvreader = csv.reader(file)
next(csvreader)
rows = []
for row in csvreader:
    c.execute('INSERT INTO valuta VALUES (' + row[0] + ', "' + row[1] + '", ' + row[2] + ');')

file.close()

c.execute('''
 CREATE TABLE Cliente (
    numeroCliente VARCHAR(6), 
      codCondPagamento BOOLEAN, 
      fatturaCumulativa INT,
    valuta INT,
      PRIMARY KEY (numeroCliente),
      FOREIGN KEY (valuta) REFERENCES Valuta(codiceValuta)
); 
''')

file = open("csv/Clienti.csv")
csvreader = csv.reader(file)
next(csvreader)
rows = []
for row in csvreader:
    c.execute('INSERT INTO Cliente VALUES ("' + row[0] + '", ' + row[1] + ', ' + row[2] + ', ' + row[3] + ');')

file.close()

c.execute('''
CREATE TABLE Vendita(
	nrMovimento INT PRIMARY KEY,
	BC varchar(10),
	tipoMovimento varchar(7),
	nrArticolo varchar(10) ,
	tipoOrigine varchar(7),
	nrOrigine varchar(6),
	quantita int,
	importoTot float,
	FOREIGN key (nrArticolo) REFERENCES Impiego_orario_risorse(nrarticolo),
	FOREIGN key (nrOrigine) REFERENCES Cliente(numerocliente)
);
''')

file = open("csv/Vendite.csv")
csvreader = csv.reader(file)
next(csvreader)
rows = []
for row in csvreader:
    c.execute('INSERT INTO Vendita VALUES (' + row[0] + ', "' + row[1].upper() + '", "' + row[2] + '", "' + row[3] + '", "' + row[4] + '", "' + row[5] + '", ' + row[6] + ', ' + row[7] + ');')

file.close()
# ART0004084
c.execute('DELETE FROM Consumo WHERE nrArticolo="ART0004084"')
c.execute('DELETE FROM Impiego_orario_risorse WHERE nrArticolo="ART0004084"')
c.execute('DELETE FROM Vendita WHERE nrArticolo="ART0004084"')

# ART0004146
c.execute('DELETE FROM Consumo WHERE nrArticolo="ART0004146"')
c.execute('DELETE FROM Impiego_orario_risorse WHERE nrArticolo="ART0004146"')
c.execute('DELETE FROM Vendita WHERE nrArticolo="ART0004146"')

conn.commit()
conn.close()