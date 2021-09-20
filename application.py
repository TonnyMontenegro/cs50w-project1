import os

from flask import Flask, session, flash, render_template, request, redirect, session, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

#extension de flask para encriptar contraseñas en hashes y compararlas de manera segura
from flask_bcrypt import Bcrypt,generate_password_hash,check_password_hash

#decoradores
from functools import wraps

app = Flask(__name__)

#Encriptacion
bcrypt = Bcrypt(app)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/")
@login_required
def home():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        Datos = db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).fetchone()
        if Datos is None:
            return render_template("error.html", Mensaje="Error, Nombre de usuario no existe,registrese o verifique su usuario")

        if not bcrypt.check_password_hash(Datos[2].encode('utf-8'), password.encode('utf-8')):
            return render_template("error.html", Mensaje="Error, contraseña o nombre de usuario incorrectos")

        session["user_id"]=Datos[0]
        session["username"]=Datos[1]
        session["Auth"]= True

        flash("Inicio de sesion correcto")
        return redirect(url_for("home"))
    else:
        return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    session.clear()
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if (not password or not username):
             return render_template("error.html", Mensaje="No puedes registrarte con campos en blanco", Titulo="Error")

        Datos = db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).fetchone()
        if Datos:
            return render_template("error.html", Mensaje="El usuario ya se encuentra registrado", Titulo="Error")

        Hash = bcrypt.generate_password_hash(password).decode('utf-8')

        db.execute("INSERT INTO users (username, password) VALUES (:username, :password)",{"username": username, "password": Hash})
        db.commit()

        flash("Registro de usuario correcto")
        return redirect(url_for("login"))
    else:
        return render_template("register.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Sesion cerrada")
    return redirect(url_for("login"))


@app.route("/search", methods=["GET"])
@login_required
def search():

    Consulta = ('%' + request.args.get("consulta") + '%').title()

    Res= db.execute("SELECT isbn,titulo,autor,año FROM books WHERE isbn LIKE :Consulta OR titulo LIKE :Consulta OR autor LIKE :Consulta OR año LIKE :Consulta LIMIT 100", {"Consulta": Consulta})
    db.execute


    if Res.rowcount == 0:
        flash("No se encontro ningun libro que coincida con lo ingresado")
        return redirect(url_for("home"))

    libros = Res.fetchall()

    return render_template("books.html", Data=libros)
