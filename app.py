from flask import Flask, flash
from flask import render_template, request, redirect
from flaskext.mysql import MySQL
from datetime import datetime
import os
from flask import send_from_directory

def borrar_upload(foto_vieja):
    if foto_vieja != "":
        try:
            os.remove(os.path.join(app.config["CARPETA"], foto_vieja))
        except FileNotFoundError: 
            flash("careful, could not remove")
            print()
            print()
            print(f"the picture file for id {id} wasnt there btw")
            print()
            print()
    return

app = Flask(__name__)
app.secret_key="Clave"

mysql = MySQL()
mysql.init_app(app)

app.config["MYSQL_DATABASE_HOST"] = "localhost"
app.config["MYSQL_DATABASE_USER"] = "root"
app.config["MYSQL_DATABASE_PASSWORD"] = ""
app.config["MYSQL_DATABASE_DB"] = "sistemaempleados"
app.config["CARPETA"] = os.path.join("uploads/")

@app.route("/uploads/<path:nombreFoto>")
def uploads(nombreFoto):
    return send_from_directory(app.config["CARPETA"], nombreFoto)

@app.route('/')
def index():
    query = "SELECT * from empleados" #the query
    conn = mysql.connect() #connect
    cursor = conn.cursor() #controller
    cursor.execute(query)
    conn.commit()

    empleados = cursor.fetchall()

    return render_template("/empleados/index.html", empleados=empleados)


@app.route("/create")
def create():
    return render_template("/empleados/create.html")


@app.route("/store", methods=['POST'])
def storage():
    _nombre = request.form['txtnombre']
    _correo = request.form['txtcorreo']
    _foto = request.files['txtfoto']  #!= porque es un archivo

    now = datetime.now()
    tiempo = now.strftime("%Y%H%M%S")

    if _foto.filename != "":
        nuevoNombreFoto = tiempo + _foto.filename
        _foto.save(os.path.join(app.config["CARPETA"], nuevoNombreFoto))
    else:
        nuevoNombreFoto = ""
    
    datos = (_nombre, _correo, nuevoNombreFoto)

    query = "INSERT INTO empleados(id,nombre,correo,foto) VALUES(NULL, %s, %s, %s);" #the query
    conn = mysql.connect() #connect
    cursor = conn.cursor() #controller
    cursor.execute(query, datos) #do the q
    conn.commit()
    
    return redirect("/")

@app.route("/destroy/<int:id>")
def destroy(id):
    conn = mysql.connect() #connect
    cursor = conn.cursor() #controller


    cursor.execute("SELECT foto FROM empleados WHERE id=%s", id)
    foto_vieja = cursor.fetchall()[0][0]
    borrar_upload(foto_vieja)

    query = "DELETE FROM empleados WHERE id=%s;" #the query
    cursor.execute(query, id) #do the q

    conn.commit()

    return redirect("/")


@app.route("/edit/<int:id>")
def edit(id):
    query = "SELECT * FROM empleados WHERE id=%s" #the query
    conn = mysql.connect() #connect
    cursor = conn.cursor() #controller
    cursor.execute(query, id) #do the q
    empleados = cursor.fetchall()
    conn.commit()

    return render_template("empleados/edit.html", empleados=empleados)

@app.route("/update/<int:id>", methods=["POST"])
def update(id):
    _nombre = request.form['txtnombre']
    _correo = request.form['txtcorreo']
    _foto = request.files['txtfoto']  #!= porque es un archivo
    
    datos = (_nombre, _correo, id)

    query = "UPDATE empleados SET nombre=%s, correo=%s WHERE id=%s;" #the query
    conn = mysql.connect() #connect
    cursor = conn.cursor() #controller
    cursor.execute(query, datos) #do the q


    #nombre nueva foto
    now = datetime.now()
    tiempo = now.strftime("%Y%H%M%S")

    if _foto.filename != "":
        nuevoNombreFoto = tiempo + _foto.filename
        _foto.save(app.config["CARPETA"]+nuevoNombreFoto)

        # Eliminar la foto
        cursor.execute("SELECT foto FROM empleados WHERE id=%s", id)
        foto_vieja = cursor.fetchall()[0][0]
        borrar_upload(foto_vieja)
        

        cursor.execute("UPDATE empleados SET foto=%s WHERE id=%s", (nuevoNombreFoto, id))
    
    else:
        flash("deberías completar esto eh")
    conn.commit()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)