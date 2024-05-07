from flask import Flask, render_template
import psycopg2
import os

external_database_url = "postgres://codecamp_user:KC9jN7cuakTRTCuuvSApzEOkwCvs59fp@dpg-cosv5q2cn0vc73ere0l0-a.frankfurt-postgres.render.com/codecamp"

app = Flask(__name__)

def get_connection():
    return psycopg2.connect(external_database_url)

@app.route('/')
def index():
    columns = UserName()
    return render_template('home.html', columns=columns)

def UserName():
    columns = []
    connection = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        select_all = """SELECT FirstName FROM Users"""
        cursor.execute(select_all)
        rows = cursor.fetchall()
        for row in rows:
            columns.append(row[0])

    except psycopg2.Error as ex:
        print(f'Błąd połączenia z bazą danych: {ex}')
    finally:
        if connection:
            connection.close()
    return columns

def is_server_running():
    lock_file_path = "flask.lock"
    return os.path.exists(lock_file_path)

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
