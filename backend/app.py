from flask import Flask, request, jsonify, send_from_directory
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS

import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app = Flask(__name__, static_folder=BASE_DIR, static_url_path='')
CORS(app)
DB_PATH = 'mycollection.db'

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
    login = data.get('login')
    password = data.get('password')
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE login = ?', (login,))
    user = c.fetchone()
    conn.close()
    if user and check_password_hash(user['password'], password):
        return jsonify({'success': True, 'user_id': user['id']})
    return jsonify({'error': 'Nieprawidłowy login lub hasło'}), 401

# Dodawanie, pobieranie, zamówienia, sprzedaż itd. można dodać analogicznie

@app.route('/')
def serve_index():
    return send_from_directory(BASE_DIR, 'index.html')

@app.route('/mycollection.html')
def serve_collection():
    return send_from_directory(BASE_DIR, 'mycollection.html')

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
