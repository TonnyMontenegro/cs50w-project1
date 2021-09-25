# Books-AltStore Docs

---

## Archivos destacables

- static
    - styles
        - `favicon.ico`
        - `layoutStyle.css`
        - `pattern.jpg`
- templates
    - `404.html`
    - `books.html`
    - `error.html`
    - `index.html`
    - `layout.html`
    - `login.html`
    - `register.html`
    - `review.html`
- `application.py`
- `books.csv`
- `requirements.txt`
- `import.txt`

### static/styles
  Contiene todos los archivos estaticos usados dentro de nuestra app de flask como *hojas de estilos*, el *favicon* y el *fondo* para nuestra web app

### templates

  contiene todos nuestros `.HTML` entre ellos nuestro `layout.html` que es el `.HTML` principal sobre el cual se inyectaran otros *bloques html* gracias a **jinja2**

  - `404.html`: pantalla de error **404**
  - `books.html`: pantalla que carga los resultados de la busqueda realizada por el usuario en el "`index.html`"
  - `error.html`: pantalla de errores generales
  - `index.html`: pantalla principal con un recuadro de busqueda para un libro dado algun dato como *titulo*,*isbn*,*año* o *autor* ya sea de manera parcial o total
  - `layout.html`: nuestro `.HTML` principal sobre el cual se inyectan los demas, este posee el *jumbotron* que albergara el contenido, una *navbar* dinamica segun si se inicio sesion o aun no y un minimalista *footer*
  - `login.html`: pantalla de inicio de sesion que pide *contraseña* y *nombre de usuario* para poder consultar su validez en la **BD**
  - `register.html`: pantalla de registro de usuario que pide *contraseña* y *nombre de usuario* para poder insertar estos datos en la **BD** solo en caso de que no haya alguien en posesion de ese *nombre de usuario*
  - `review.html`: pantalla que contiene la *portada del libro*, sus *comentarios* dentro de nuestra web y sus informacion detallada incluyendo una consulta a la **api** de *google books* para saber su *promedio* y su *cantidad de puntuaciones*

### Raiz del projecto

  - `application.py`: nuestra app de **flask** encargada de funcionar como backend para gestionar las pantallas y nuestra web app como la conexion a la *BD* en **heroku** **postgres**
  - `books.csv`: conjunto de libros `.csv` brindados por **Web50** para importarlo a nuestra *BD* y asi tener los datos de los 5000 libros 
  - `requirements.txt`: Modulos e instalaciones necesarias para que nuestro proyecto funcione correctamente
  - `import.py`: modulo creado y empleado para poder realizar la importacion de todos nuestros *libros* provenientes de nuestro archivo `books.csv` hacia nuestra *BD*


---

## Tablas y su estructura
### Tabla de libros

| books   | TIPO                          |
|---------|-------------------------------|
| id      | int(primary,auto incremental) |
| isbn    | varchar                       |
| titulo  | varchar                       |
| autor   | varchar                       |
| año     | varchar                       |

### Tabla de usuarios

| COLUMNA  | Tipo                          |
|----------|-------------------------------|
| id       | int(primary,auto incremental) |
| username | varchar                       |
| password | varchar                       |

### Tabla de reviews(relacionada)

| COLUMNA    | TIPO                          |
|------------|-------------------------------|
| id         | int(primary,auto incremental) |
| user_id    | int(foreing,users.id)         |
| book_id    | int(foreing,books.id)         |
| comentario | varchar                       |
| puntuacion | int                           |

---
