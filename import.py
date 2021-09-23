# Modulo para importar el .CSV a nuestra BD
import os, csv

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# Obtenemos la conexion a la BD por medio de la variable de entorno que almacena nuestra URI
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
    # Abrimos el archivo csv en cuestion para poder leerlo
    with open("books.csv") as file:
        # Marcamos nuestro delimitador entre libro y libro
        Libro = csv.reader(file, delimiter=',')
        next(Libro, None)

        # Procedemos a insertar el libro leido en la BD
        for isbn, title, author, year in Libro:
            db.execute("INSERT INTO books (isbn, titulo, autor, año) \
                VALUES (:isbn , :titulo, :autor, :año)",\
                {"isbn": isbn, "titulo": title, "autor": author, "año": year})
                print(f"{isbn},{title},{author},{year},")
            db.commit()
        # Le notificamos al master que nuestra importacion ha finalizado
        print("c'est fini")

if __name__ == "__main__":
    main()