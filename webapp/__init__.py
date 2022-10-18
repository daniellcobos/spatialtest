import os

from flask import Flask,render_template,url_for, request,send_from_directory
import geopandas as gpd
import pyogrio
from sqlalchemy import create_engine
import numpy as np

app = Flask(__name__, static_url_path = '/static')
app.config.from_object('config.local')
db_connection_string = app.config["DBCONN"]

con = create_engine(db_connection_string)





@app.route('/')
def firstpage():
    con.connect()
    sql = "select * from direstrato where ciudad = 'Bogota' order by random() limit 1000;"
    df = gpd.read_postgis(sql, con)
    df2 = df.groupby('estrato', group_keys=False).apply(lambda x: x.sample(1))
    print(df2)
    sample = df2.to_json()
    archivo = os.path.join(app.root_path, 'static/downloads/', '', 'Muestreo.xlsx')
    download = df2.to_excel(archivo, index=False, header=True)
    con.connect().close()
    return render_template("prototype.html", sample=sample)


@app.route('/muestreo', methods =['POST'])
def muestreo():
    con.connect()
    ciudad = request.form['ciudad']
    puntos1 = int(request.form['puntos1'])
    puntos2 = int(request.form['puntos2'])
    proporcion = request.form['proporcion']
    sql = "select * from direstrato where ciudad = '" + ciudad + "' order by random() limit 30000;"
    df = gpd.read_postgis(sql, con)
    if proporcion == "prop1":
        df3 = df.groupby('estrato', group_keys=False).apply(lambda x: x.sample(puntos1))
    elif proporcion == "prop2":
        df3 = df.groupby('estrato', group_keys=False).apply(lambda x: x.sample(frac=puntos2/100))
    else:
        df3 = df.groupby('estrato', group_keys=False).apply(lambda x: x.sample(5))
    sample = df3.to_json()
    archivo = os.path.join(app.root_path, 'static/downloads/', '', 'Muestreo.xlsx')
    df3.to_excel (archivo, index = False, header=True)
    print(sql)
    con.connect().close()
    return render_template("prototype.html", sample=sample)

@app.route('/prox', methods =['GET','POST'])
def prox():
    con.connect()
    if request.method == 'POST':

        distancia = int(request.form['distancia'])
        ciudad = request.form['ciudad']
        tipo = request.form['tipo']
        if tipo == "Educacion":
            sql2 = "Select dir.* from Colegios as col left join diresplano as dir on ST_Dwithin(col.geom,dir.geom,{}) where dir.ciudad='{}' order by random() limit 10000".format(distancia, ciudad)
        elif tipo == "Transporte":
            sql2 = "Select dir.* from transporte_publico_webmerc as tpm left join diresplano as dir on ST_Dwithin(tpm.geom,dir.geom,{}) where dir.ciudad='{}' order by random() limit 10000".format(
                distancia, ciudad)
        elif tipo == "Comercio":
            sql2 = vir.format(
                distancia, ciudad)
    else:
        sql2 = "Select dir.* from Colegios as col left join diresplano as dir on ST_Dwithin(col.geom,dir.geom,75)  where dir.ciudad='Bogota'  order by random() limit 10000"
    df = gpd.read_postgis(sql2, con)
    print(sql2)
    if request.method == 'POST':
        puntos = int(request.form['puntos'])
    else:
        puntos = 15
    df2 = df.sample(puntos)
    sample = df2.to_json()
    archivo = os.path.join(app.root_path, 'static/downloads/', '', 'Muestreo2.xlsx')
    df2.to_excel(archivo, index=False, header=True)
    con.connect().close()
    return render_template("prototype2.html", sample=sample)

@app.route('/systematic' ,methods =['GET','POST'])
def systematic():
    if request.method == 'GET' :
        sql = "select * from direstratosys where ciudad = 'Bogota' order by random() limit 30000;"
        intervalo = 5
    else:
        print(request.form)
        ciudad = request.form['ciudad']
        intervalo = int(request.form['intervalo'])
        sql = "select * from direstratosys where ciudad = '" + ciudad + "' order by random() limit 30000;"
    con.connect()
    df = gpd.read_postgis(sql, con)
    df2 = df.groupby('gridid', group_keys=False).apply(lambda x: x.sample(1))
    df2 = df2.iloc[::intervalo, :]
    print(df2)
    sample = df2.to_json()
    archivo = os.path.join(app.root_path, 'static/downloads/', '', 'Muestreo3.xlsx')
    download = df2.to_excel(archivo, index=False, header=True)
    con.connect().close()
    return render_template("muestreosistematico.html", sample=sample)

@app.route('/download/muestreo')
def download_file():
    path = os.path.join(app.root_path, 'static/downloads/',)
    return send_from_directory(path, 'Muestreo.xlsx')

@app.route('/download/muestreoprox')
def download_muestreo():
    path = os.path.join(app.root_path, 'static/downloads/',)
    return send_from_directory(path, 'Muestreo2.xlsx')

