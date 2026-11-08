import os
import time
import logging

import pymysql # pyright: ignore[reportMissingModuleSource]
from flask import Flask, make_response, render_template # pyright: ignore[reportMissingImports]
from werkzeug.middleware.proxy_fix import ProxyFix # pyright: ignore[reportMissingImports]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

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
                "UPDATE week2_counter SET visits = visits + 1 WHERE id = 1"
            )
            logging.info("Incremented counter in database")
            cursor.execute(
                "SELECT visits FROM week2_counter WHERE id = 1"
            )
            logging.info("Fetched updated counter value from database")
            visits = cursor.fetchone()[0]
        connection.commit()
        return visits
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


@app.route("/")
def week2():
    visits = increment_counter()
    response = make_response(render_template("week2.html", visits=visits))
    # Selain ei saa näyttää vanhaa laskurin arvoa välimuistista
    response.headers["Cache-Control"] = "no-store"
    return response