from flask import Flask,render_template,url_for, request
import geopandas as gpd
import pyogrio
from sqlalchemy import create_engine

app = Flask(__name__, static_url_path = '/static')

db_connection_url = "postgresql://postgres:postgres@localhost:5432/SpatialSampling"
con = create_engine(db_connection_url)





@app.route('/')
def firstpage():
    sql = "select * from direstrato where ciudad = 'Bogota' order by random() limit 30000;"
    df = gpd.read_postgis(sql, con)
    df2 = df.groupby('estrato', group_keys=False).apply(lambda x: x.sample(10))
    print(df2)
    sample = df2.to_json()
    return render_template("prototype.html", sample=sample)


@app.route('/muestreo', methods =['POST'])
def muestreo():
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
    print(sql)
    return render_template("prototype.html", sample=sample)

@app.route('/prox', methods =['GET','POST'])
def prox():
    if request.method == 'POST':
        distancia = int(request.form['distancia'])
        sql2 = "Select dir.* from colegios_2022_03 as col left join fe as dir on ST_Dwithin(col.geom,dir.geom,{})".format(distancia)
    else:
        sql2 = "Select dir.* from colegios_2022_03 as col left join fe as dir on ST_Dwithin(col.geom,dir.geom,75)"
    df = gpd.read_postgis(sql2, con)
    if request.method == 'POST':
        puntos = int(request.form['puntos'])
    else:
        puntos = 15
    df2 = df.sample(puntos)
    sample = df2.to_json()
    print(df2)
    return render_template("prototype2.html", sample=sample)

