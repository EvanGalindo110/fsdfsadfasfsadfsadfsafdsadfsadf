from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient

app = Flask(__name__)
app.secret_key = "clave_secreta"

cliente = MongoClient("mongodb://localhost:27017/")
db = cliente["mi_app"]
usuarios = db["usuarios"]

@app.route('/')
def inicio():
    return render_template('inicio.html')

@app.route('/inicio', methods=['POST'])
def registro():
    nombre = request.form['nombre']
    apellidos = request.form['apellidos']
    correo = request.form['correo']
    password = request.form['password']  

    if usuarios.find_one({"correo": correo}):
        return "El usuario ya existe"

    session['temp'] = {
        "nombre": nombre,
        "apellidos": apellidos,
        "correo": correo,
        "password": password  
    }

    return redirect(url_for('listas'))


@app.route('/sesion', methods=['GET', 'POST'])
def sesion():
    if request.method == 'POST':
        correo = request.form['correo']
        password = request.form['password']

        usuario = usuarios.find_one({
            "correo": correo,
            "password": password
        })

        if usuario:
            session['usuario'] = correo
            return redirect(url_for('listas'))
        else:
            return render_template('sesion.html', error="Datos incorrectos")

    return render_template('sesion.html')

@app.route('/usuario')
def usuario():
    if 'usuario' not in session:
        return redirect(url_for('sesion'))

    datos = usuarios.find_one({"correo": session['usuario']})

    if not datos:
        return "Usuario no encontrado"

    return render_template('usuario.html', datos=datos)

@app.route('/editar', methods=['GET', 'POST'])
def editar():
    if 'usuario' not in session:
        return redirect(url_for('sesion'))

    usuario = usuarios.find_one({"correo": session['usuario']})

    if request.method == 'POST':
        nombre = request.form['nombre'].strip()
        apellidos = request.form['apellidos'].strip()
        correo = request.form['correo'].strip()

        if not nombre or not apellidos or not correo:
            error = "Todos los campos son obligatorios"
            return render_template('editar.html', datos=usuario, error=error)

        if correo != session['usuario'] and usuarios.find_one({"correo": correo}):
            error = "El correo ya está en uso"
            return render_template('editar.html', datos=usuario, error=error)

        usuarios.update_one(
            {"correo": session['usuario']},
            {"$set": {
                "nombre": nombre,
                "apellidos": apellidos,
                "correo": correo
            }}
        )

        session['usuario'] = correo
        return redirect(url_for('usuario'))

    return render_template('editar.html', datos=usuario)

@app.route('/listas') 
def listas():
    return render_template('listas.html')

app.run(debug=True)


