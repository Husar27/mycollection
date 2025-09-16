from flask import Flask, request, jsonify, send_from_directory, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS

import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app = Flask(__name__, static_folder=BASE_DIR, static_url_path='')
app.secret_key = 'supersecretkey'  # zmień na własny w produkcji
login_manager = LoginManager()
login_manager.init_app(app)
CORS(app)
DB_PATH = 'mycollection.db'

# --- Cloudinary blueprint ---
from cloudinary_uploads.blueprint import cloudinary_upload
app.register_blueprint(cloudinary_upload)

# Model użytkownika dla Flask-Login
class User(UserMixin):
    def __init__(self, id, login, password):
        self.id = id
        self.login = login
        self.password = password

    @staticmethod
    def get(user_id):
        conn = get_db()
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user = c.fetchone()
        conn.close()
        if user:
            return User(user['id'], user['login'], user['password'])
        return None

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    # Tabela użytkowników
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        login TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )''')
    # Tabela kolekcji
    c.execute('''CREATE TABLE IF NOT EXISTS bottles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        brand TEXT,
        qty INTEGER,
        price TEXT,
        order_no TEXT,
        date TEXT,
        user_id INTEGER,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )''')
    # Tabela zamówień
    c.execute('''CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bottle_name TEXT,
        qty INTEGER,
        price TEXT,
        order_date TEXT,
        user_id INTEGER,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )''')
    # Tabela sprzedaży
    c.execute('''CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bottle_name TEXT,
        qty INTEGER,
        price TEXT,
        sale_date TEXT,
        user_id INTEGER,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )''')
    # Dodaj tylko dwóch użytkowników jeśli nie istnieją
    users = [
        ("adam", generate_password_hash("Jack19klub2025")),
        ("mariusz", generate_password_hash("Re18dom2025"))
    ]
    for login, password in users:
        c.execute('SELECT id FROM users WHERE login = ?', (login,))
        if not c.fetchone():
            c.execute('INSERT INTO users (login, password) VALUES (?, ?)', (login, password))
    conn.commit()
    conn.close()



@app.route('/login', methods=['POST'])
def login():
    data = request.json
    login_ = data.get('login')
    password = data.get('password')
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE login = ?', (login_,))
    user = c.fetchone()
    conn.close()
    if user and check_password_hash(user['password'], password):
        user_obj = User(user['id'], user['login'], user['password'])
        login_user(user_obj)
        return jsonify({'success': True, 'user_id': user['id']})
    return jsonify({'error': 'Nieprawidłowy login lub hasło'}), 401

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'success': True})

# Dodawanie, pobieranie, zamówienia, sprzedaż itd. można dodać analogicznie

@app.route('/')
def serve_index():
    return send_from_directory(BASE_DIR, 'index.html')

@app.route('/mycollection.html')
@login_required
def serve_collection():
    return send_from_directory(BASE_DIR, 'mycollection.html')

if __name__ == '__main__':
    init_db()
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
