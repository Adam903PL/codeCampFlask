from flask import Flask, render_template, request, redirect, url_for
import psycopg2
import webbrowser

external_database_url = "postgres://codecamp_user:KC9jN7cuakTRTCuuvSApzEOkwCvs59fp@dpg-cosv5q2cn0vc73ere0l0-a.frankfurt-postgres.render.com/codecamp"

app = Flask(__name__)


@app.route('/main.html')
def loged():
    username = request.args.get('username')
    password = request.args.get('password')
    return render_template('main.html', username=username, password=password)

def get_connection():
    return psycopg2.connect(external_database_url)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        login = request.form['Login']
        password = request.form['Password']
        result = login_attempt(login, password)
        print(result)
        if result == "Zalogowano pomyślnie":
            # Jeśli logowanie powiodło się, otwórz stronę /main.html w przeglądarce
            url = url_for('loged', username=login, password=password, _external=True)
            webbrowser.open(url)
            return redirect(url_for('loged', username=login, password=password))
        else:
            # Jeśli logowanie nie powiodło się, wyświetl informację o błędzie na stronie logowania
            return render_template('login.html', error=result)
    return render_template('login.html')

def login_attempt(login, password):
    connection = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        select_query = f"SELECT * FROM LoginCredits WHERE UserLogin = '{login}' AND UserPassword = '{password}'"
        cursor.execute(select_query)
        if cursor.fetchone():
            print("Zalogowano")
            return "Zalogowano pomyślnie"
        else:
            print('Nie zalogowano')
            return "Błąd logowania: nieprawidłowy login lub hasło"
    except psycopg2.Error as ex:
        print(f'Błąd połączenia z bazą danych: {ex}')
        return "Wystąpił błąd podczas logowania"
    finally:
        if connection:
            connection.close()


def register(login, password, email, birthdate, firstname, lastname):
    connection = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        insert_query = f"""
            INSERT INTO Users (FirstName, LastName, BirthDate)
            VALUES ('{firstname}','{lastname}','{birthdate}')
            RETURNING UserId
        """
        cursor.execute(insert_query, (firstname, lastname, birthdate))
        user_id = cursor.fetchone()[0]

        insert_login_query = f"""
            INSERT INTO LoginCredits (UserLogin, UserPassword, UserEmail)
            VALUES ('{login}','{password}','{email}')
        """
        cursor.execute(insert_login_query, (user_id, login, password, email))

        connection.commit()

        print("Użytkownik został pomyślnie zarejestrowany.")
        return "Użytkownik został pomyślnie zarejestrowany."

    except psycopg2.Error as ex:
        print(f'Błąd połączenia z bazą danych: {ex}')
        return "Wystąpił błąd podczas rejestracji użytkownika."
    finally:
        if connection:
            connection.close()


if __name__ == '__main__':
    app.run(debug=True)
