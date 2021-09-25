# Modulo principal de nuestra web que funciona de backend
import os
import requests
from flask import Flask, session, flash, render_template, request, redirect, session, url_for, jsonify
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
if not os.getenv("DB_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DB_URL"))
db = scoped_session(sessionmaker(bind=engine))

# wrap de seguridad para evitar que el usuario no autenticado pueda acceder a nuestra web
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

# Manejo de codigos de error
@app.errorhandler(404)
def page_not_found(error):
    return 'This page does not exist', 404

# Ruta por defecto de nuestra Web
@app.route("/")
@login_required

def home():
    return render_template("index.html")

# Ruta de inicio de sesion de nuestra Web
@app.route("/login", methods=["GET", "POST"])
def login():
    # En caso que el usuario envie sus datos de inicio de sesion por metodo POST se procede a realizar la consulta de las credenciales
    if request.method == "POST":

        # Se leen las entradas del usuario
        username = request.form.get("username")
        password = request.form.get("password")

        # Se consulta si el nombre de usuario de la persona existe en los usuarios registrados
        Datos = db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).fetchone()
        if Datos is None:
            # En caso de que no exista se le notifica al usuario que ese User no esta registrado
            return render_template("error.html", Mensaje="Error, Nombre de usuario no existe,registrese o verifique su usuario")

        # Si la contraseña almacenada en forma de hash no es la misma que la que se ingreso, se muestra una pantalla de error
        if not bcrypt.check_password_hash(Datos[2].encode('utf-8'), password.encode('utf-8')):
            return render_template("error.html", Mensaje="Error, contraseña o nombre de usuario incorrectos")

        # se almacena la info de el usuario y se cambia su estado a autenticado
        session["user_id"]=Datos[0]
        session["username"]=Datos[1]
        session["Auth"]= True

        # se le notifica con un flash que inicio sesion
        flash("Inicio de sesion correcto")
        return redirect(url_for("home"))
    else:
        # si el usuario intenta hacer una consulta GET se le redirecciona denuevo al inicio de sesion
        return render_template("login.html")

# Ruta de Registro de usuario de nuestra Web
@app.route("/register", methods=["GET", "POST"])
def register():
    # se limpia la sesion
    session.clear()
    # En caso que el usuario envie sus datos de registro por metodo POST se procede a realizar la insersion de las credenciales
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # si no se ingresa usuario o contraseña se le notifica al usuario
        if (not password or not username):
             return render_template("error.html", Mensaje="No puedes registrarte con campos en blanco", Titulo="Error")

        # se consulta si el nombre de usuario se encuentra disponible
        Datos = db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).fetchone()
        if Datos:
            # caso contrario se le notifica al usuario
            return render_template("error.html", Mensaje="El usuario ya se encuentra registrado", Titulo="Error")

        # si esta disponible el usuario y se ingreso una contraseña se procede a convertir la contraseña a un hash
        Hash = bcrypt.generate_password_hash(password).decode('utf-8')

        # se registar el usuario y contraseña en la BD
        db.execute("INSERT INTO users (username, password) VALUES (:username, :password)",{"username": username, "password": Hash})
        db.commit()

        # se notifica que el registro se dio con exito
        flash("Registro de usuario correcto")

        # se redirije el usaurio a la pagina de inicio de sesion para que ingrese sus credenciales
        return redirect(url_for("login"))
    else:
        # en caso que se consulte por medio del metodo get se le redrije a la pagina de registro
        return render_template("register.html")

# modulo que realiza el cierre de sesion del usuario actual
@app.route("/logout")
def logout():
    # se limpia la sesion del usuario
    session.clear()
    # se le notifica al usuario y se le redirije a la pagina de inicio de sesion
    flash("Sesion cerrada")
    return redirect(url_for("login"))

# Ruta que realiza la consulta a nuestra BD sobre el dato ingresado por el usuario
@app.route("/search", methods=["GET"])
@login_required
def search():

    # se realiza la consulta en la DB con datos que se parezcan al ingresado por el usuario
    Consulta = ('%' + request.args.get("consulta") + '%').title()
    Res= db.execute("SELECT isbn,titulo,autor,año FROM books WHERE isbn LIKE :Consulta OR titulo LIKE :Consulta OR autor LIKE :Consulta OR año LIKE :Consulta LIMIT 100", {"Consulta": Consulta})
    db.commit()

    # si no hay ningun resultado se le notifica y se limpia el campo de busqueda
    if Res.rowcount == 0:
        flash("No se encontro ningun libro que coincida con lo ingresado")
        return redirect(url_for("home"))

    # sino se cargan todos los resultados y son enviados al modulo de resultado de libros
    libros = Res.fetchall()

    return render_template("books.html", Data=libros)

# ruta para que el usuario pueda dejar una review y visualizar estadisticas detalladas del libro
@app.route("/review/<code>", methods=["GET","POST"])
@login_required
def review(code):
    # en caso de que se realice una consulta del tipo GET se carla la pagina de reviews
    if request.method == "GET":

        # en base al ISBN se busca el libro y se obtiene su info
        consulta = db.execute("SELECT isbn,titulo,autor,año FROM books WHERE isbn = :isbncode",{"isbncode": code})
        db.commit()
        data = consulta.fetchone()

        # en caso que el usuario manipule la URL e ingrese un ISBN no disponible o erroneo se le retorna el error 404 not found
        if data is None:
            return render_template('404.html'),404

        # si existe el libro se consulta sus estadisticas de puntuacion en la API de google books
        response = requests.get("https://www.googleapis.com/books/v1/volumes?q=isbn:"+code)
        responsejson = response.json()

        # en caso que la api no retorne respuesta o no se encuentre se mostraria un error
        if response.status_code == 442 or response.status_code == 404:
            raise Exception("Error: problema con la api, no se puede procesar o no se encuentra")

        # Se revisa si existe un conteo de reviews en el JSON retornado por la API de google
        existeR =  "ratingsCount" in responsejson["items"][0]["volumeInfo"]
        if existeR:
            rating_counts = responsejson["items"][0]["volumeInfo"]["ratingsCount"]
        else:
            # caso contrario se agrega lo siguiente en ese campo
            rating_counts = "No existen puntuaciones"

        # Se revisa si existe un promedio de reviews en el JSON retornado por la API de google
        existeA =  "averageRating" in responsejson["items"][0]["volumeInfo"]
        if existeA:
            average_rating = responsejson["items"][0]["volumeInfo"]["averageRating"]
        else:
            # caso contrario se agrega lo siguiente en ese campo
            average_rating = "No se tienen promedio"

        # Se revisa si existe un promedio de reviews en el JSON retornado por la API de google
        existeD =  "description" in responsejson["items"][0]["volumeInfo"]
        if existeD:
            description = responsejson["items"][0]["volumeInfo"]["description"]
        else:
            # caso contrario se agrega lo siguiente en ese campo
            description = "No se tienen una descripcion sobre este libro"

        # se consulta el ID del libro que concuerde con el ISBN solicitado
        consulta2 = db.execute("SELECT id FROM books WHERE isbn = :isbncode",{"isbncode": code})
        db.commit()
        book_id = consulta2.fetchone()[0]

        # se consulta los comentarios, su puntuacion y el usuario que puntuo para cargarlos en la pgina del libro
        consulta3 = db.execute("SELECT comentario ,puntuacion ,username FROM users JOIN reviews ON users.id = reviews.user_id WHERE book_id = :id_book",{"id_book": book_id})
        db.commit()
        comentarios = consulta3.fetchall()

        # se envian los datos solicitados del libro y sus comentarios
        return render_template("review.html", rating_counts=rating_counts,average_rating=average_rating,Libro=data, description=description,Comentarios=comentarios)

    # en caso de que se realice una consulta del tipo POST se solicita subir un comentario
    else:
        # se guarda en una variable el UserName de usuario
        Usuario = session["user_id"]

        # se consulta el id del libro que corresponde a ese ISBN
        consulta = db.execute("SELECT id FROM books WHERE isbn = :isbncode",{"isbncode": code})
        db.commit()
        id_book = consulta.fetchone()[0]

        # se verifica que ese usuario no haya realizado anteriormente un comentario sobre ese libro
        check =  db.execute("SELECT id FROM reviews WHERE user_id = :Usuario AND book_id = :id_book",{"Usuario": Usuario, "id_book": id_book})
        db.commit()
        if check.rowcount == 1:
            flash("Ya has realizado una reseña de este libro, no puedes hacer otra")
            return redirect("/review/"+code)

        # se obtiene la puntuacion y el comentario dejado por el usuario que aun no ha comentado sobre es ese libro
        rating = request.form.get("Puntuacion")
        comentary = request.form.get("Comentario")

        # se convierte su puntuacion a un entero
        rating = int(rating)

        # se procede a añadir el comentario con su puntuacion, sus relaciones entre el id unico del usuario y el del libro
        db.execute("INSERT INTO reviews (comentario, puntuacion, user_id, book_id) VALUES (:comentary,:rating, :Usuario, :id_book)",{"comentary": comentary,"rating": rating,"Usuario": Usuario,"id_book": id_book})
        db.commit()

        # se le notifica que su comentario se subio con exito y se recarga la pagina para mostrar los nuevos comentarios
        flash("Se ha subido su reseña con exito")
        return redirect("/review/"+code)

# la ruta de la API personal
@app.route("/api/<code>", methods=["GET"])
def API(code):
    # se consulta los datos de el libro dado un ISBN ingresado en la URL
    consulta = db.execute("SELECT isbn,titulo,autor,año,id FROM books WHERE isbn = :isbncode",{"isbncode": code}).fetchone()
    db.commit()

    # si no se encuentra el libro dado, se retorna error 404
    if consulta is None:
        return jsonify({"error":"404","ErrorDescription":"No se encuentra el libro con ese ISBN"}),404

    # se almacenan los datos consultados en variables
    isbn = consulta[0]
    titulo = consulta[1]
    autor = consulta[2]
    año = consulta[3]
    book_id = consulta[4]

    # se saca el numero de comentarios y su promedio dentro de mi web
    rating_count = db.execute("SELECT COUNT(comentario) FROM reviews WHERE book_id = :id_book",{"id_book": book_id}).fetchone()
    db.commit()
    # si no se ha comentado aun
    if rating_count[0] == 0:
        rating=int(0)
    else:
        rating=int(rating_count[0])
    average_rating = db.execute("SELECT AVG(puntuacion) FROM reviews WHERE book_id = :id_book",{"id_book": book_id}).fetchone()
    db.commit()
    if average_rating[0] == None:
        average=int(0)
    else:
        average=int(average_rating[0])

    # se crea un diccionario que contendra los datos solicitados por python
    json = {
        "title": titulo,
        "author": autor,
        "year": año,
        "isbn": code,
        "review_count": rating,
        "average_score": average
    }
    # se convierte y se retorna el JSON
    return jsonify(json)
