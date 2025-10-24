from flask import Flask, render_template, request, session, redirect, flash, url_for
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # TODO: Ändra detta till en slumpmässig hemlig nyckel

# Databaskonfiguration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',  # Ändra detta till ditt MySQL-användarnamn
    'password': '',  # Ändra detta till ditt MySQL-lösenord
    'database': 'inlämning1'  # TODO: Ändra detta till ditt databasnamn
}

def get_db_connection():
    """Skapa och returnera en databasanslutning"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Fel vid anslutning till MySQL: {e}")
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        logout = request.form.get('logout')
        if logout.upper() == 'LOGOUT':
            session.pop('logged_in', None)
            session.pop('user_id', None)
            session.pop('username', None)
            return redirect(url_for('index'))
        else:
            flash('Ogiltigt kommando för utloggning', 'error')
            return redirect(url_for('index'))
    if not session.get('logged_in'):
        return render_template('login.html')
    return render_template('index.html')

    

@app.route('/login', methods=['POST'])
def login():
    # hantera POST request från inloggningsformuläret
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        connection = get_db_connection()
        if connection is None:
            return "Databasanslutning misslyckades", 500
        
        try:
            cursor = connection.cursor(dictionary=True)
            
            # Fråga för att kontrollera om användare finns med matchande användarnamn
            query = "SELECT * FROM users WHERE username = %s"
            cursor.execute(query, (username,))
            user = cursor.fetchone()  # hämtar en rad eller None
            
            # Kontrollera om användaren fanns i databasen och lösenordet är korrekt.
            if user and user['password'] == password:
                session['user_id'] = user.get('id')
                session['username'] = user.get('username')
                session['logged_in'] = True
                flash('Inloggning lyckades! Välkommen!', 'success')
                return render_template('index.html') 
            else:
                flash ('Ogiltigt användarnamn eller lösenord', 'error')
                return redirect(url_for('index'))
            # Om lösenordet är korrekt så sätt sessionsvariabler och skicka tillbaka en hälsning med användarens namn.
            # Om lösenordet inte är korrekt skicka tillbaka ett felmeddelande med http-status 401.

        except Error as e:
            print(f"Databasfel: {e}")
            return "Databasfel inträffade", 500
        
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

if __name__ == '__main__':
    app.run(debug=True)