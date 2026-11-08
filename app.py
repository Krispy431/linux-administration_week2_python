import os

import pymysql
from flask import Flask, make_response, render_template
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)

# Nginx kertoo alkuperäisen yhteyden tiedot ja sovelluksen alipolun (/viikko2).
app.wsgi_app = ProxyFix(
    app.wsgi_app,
    x_for=1,
    x_proto=1,
    x_prefix=1,
)


def increment_counter():
    connection = pymysql.connect(
        unix_socket="/run/mysqld/mysqld.sock",
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        database="linux_administration",
        charset="utf8mb4",
        autocommit=False,
    )
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE laskuri SET kaynnit = kaynnit + 1 WHERE id = 1"
            )
            cursor.execute(
                "SELECT kaynnit FROM laskuri WHERE id = 1"
            )
            kaynnit = cursor.fetchone()[0]
        connection.commit()
        return kaynnit
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


@app.route("/")
def etusivu():
    visits = increment_counter()
    response = make_response(render_template("week2.html", visits=visits))
    # Selain ei saa näyttää vanhaa laskurin arvoa välimuistista
    response.headers["Cache-Control"] = "no-store"
    return response