import os

from flask import Flask,render_template,url_for, request,send_from_directory, redirect
import geopandas as gpd
import pandas as pd
from werkzeug.utils import secure_filename
from sqlalchemy import create_engine
from shapely import wkt


app = Flask(__name__, static_url_path = '/static')
app.config.from_object('config.local')
db_connection_string = app.config["DBCONN"]







@app.route('/')
def firstpage():
    con = create_engine(db_connection_string)
    sql = "select * from direstrato where ciudad = 'Bogota' order by random() limit 1000;"
    df = gpd.read_postgis(sql, con)
    df2 = df.groupby('estrato', group_keys=False).apply(lambda x: x.sample(1))
    print(df2)
    sample = df2.to_json()
    archivo = os.path.join(app.root_path, 'static/downloads/', '', 'Muestreo.xlsx')
    download = df2.to_excel(archivo, index=False, header=True)
    con.connect().close()
    return render_template("prototype.html", sample=sample)


def muestreoloc(ciudad,proporcion, puntos1, puntos2):
    con = create_engine(db_connection_string)
    sql = "SELECT locnombre, dir.geom, dir.direccion FROM loca as loc join direstrato as dir on ST_WITHIN(dir.geom, loc.geom) and dir.ciudad =  '" + ciudad + "' order by random() limit 35000"
    df = gpd.read_postgis(sql, con)
    if proporcion == "prop1":
        df = df.groupby('locnombre', group_keys=False).apply(lambda x: x.sample(puntos1))
    elif proporcion == "prop2":
        df = df.groupby('locnombre', group_keys=False).apply(lambda x: x.sample(frac=puntos2 / 1000))
    else:
        df = df.groupby('locnombre', group_keys=False).apply(lambda x: x.sample(5))
    df = df.rename(columns={"locnombre": "estrato"})
    con.connect().close()
    return df


def muestreoes(ciudad, proporcion, puntos1, puntos2):
    con = create_engine(db_connection_string)
    sql = "select * from direstrato where ciudad = '" + ciudad + "' order by random() limit 30000;"
    df = gpd.read_postgis(sql, con)
    if proporcion == "prop1":
        df = df.groupby('estrato', group_keys=False).apply(lambda x: x.sample(puntos1))
    elif proporcion == "prop2":
        df = df.groupby('estrato', group_keys=False).apply(lambda x: x.sample(frac=puntos2 / 1000))
    else:
        df = df.groupby('estrato', group_keys=False).apply(lambda x: x.sample(5))
    con.connect().close()
    return df


def muestreocsus(ciudad, proporcion, puntos1, puntos2):
    con = create_engine(db_connection_string)
    sql = "select * from dircsus_2 where ciudad = '" + ciudad + "' order by random() limit 50000;"
    df = gpd.read_postgis(sql, con)
    if proporcion == "prop1":
        df = df.groupby('cat', group_keys=False).apply(lambda x: x.sample(puntos1))
    elif proporcion == "prop2":
        df = df.groupby('cat', group_keys=False).apply(lambda x: x.sample(frac=puntos2 / 1000))
    else:
        df = df.groupby('cat', group_keys=False).apply(lambda x: x.sample(5))
    con.connect().close()
    return df


@app.route('/muestreo', methods =['POST'])
def muestreo():
    con = create_engine(db_connection_string)
    con.connect()
    ciudad = request.form['ciudad']
    puntos1 = int(request.form['puntos1'])
    puntos2 = int(request.form['puntos2'])
    proporcion = request.form['proporcion']
    tipoes = request.form['tipoes']
    if tipoes == 'es':
        df = muestreoes(ciudad, proporcion, puntos1, puntos2)
    elif tipoes == "csus":
        df = muestreocsus(ciudad, proporcion, puntos1, puntos2)
    else:
        df = muestreoloc(ciudad,proporcion, puntos1, puntos2)
    sample = df.to_json()
    print(df)
    archivo = os.path.join(app.root_path, 'static/downloads/', '', 'Muestreo.xlsx')
    df.to_excel(archivo, index = False, header=True)

    if tipoes == 'csus':
        rtemplate = "csus.html"
    else:
        rtemplate = "prototype.html"
    return render_template(rtemplate, sample=sample)


@app.route('/prox', methods =['GET','POST'])
def prox():
    con = create_engine(db_connection_string)
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
            sql2 = "Select dir.* from ccom2 as tpm left join diresplano as dir on ST_Dwithin(tpm.geom,dir.geom,{}) where dir.ciudad='{}' order by random() limit 10000".format(
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
    df2=df2.set_crs('epsg:3857')
    df2 = df2.to_crs({'init': 'epsg:4326'})
    df2.to_excel(archivo, index=False, header=True)
    con.connect().close()
    return render_template("prototype2.html", sample=sample)


@app.route('/systematic' ,methods =['GET','POST'])
def systematic():
    con = create_engine(db_connection_string)
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


@app.route('/download/muestreosys')
def download_muestreosys():
    path = os.path.join(app.root_path, 'static/downloads/',)
    return send_from_directory(path, 'Muestreo3.xlsx')


@app.route('/uploader')
def uploader():
    return render_template("uploader.html")


@app.route('/readPoints', methods=['POST'])
def readpoints():
    if request.method == 'POST':
        try:
            # check if the post request has the file part
            if 'file' not in request.files:
                return redirect(request.url)
            file = request.files['file']
            df = pd.read_excel(file)
            df['geom'] = gpd.GeoSeries.from_wkt(df['geom'])
            df = gpd.GeoDataFrame(df, geometry='geom')
            df = df.to_json()

            # If the user does not select a file, the browser submits an
            # empty file without a filename.
            if file:
                return render_template("readFile.html", sample=df)
        except Exception as e:
            print(e)
            return "Archivo no Seleccionado"
    else:
        return redirect(url_for('uploader'))