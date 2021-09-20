import os, csv

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
    with open("books.csv") as file:
        Libro = csv.reader(file, delimiter=',')
        next(Libro, None)

        for isbn, title, author, year in Libro:
            db.execute("INSERT INTO books (isbn, titulo, autor, año) \
                VALUES (:isbn , :titulo, :autor, :año)",\
                {"isbn": isbn, "titulo": title, "autor": author, "año": year})
                print(f"{isbn},{title},{author},{year},")
            db.commit()
        print("c'est fini")

if __name__ == "__main__":
    main()