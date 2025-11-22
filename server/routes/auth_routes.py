from flask import Blueprint, request, jsonify
from services.db_manager import execute_insert, execute_query
import sqlite3

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400
        
    try:
        user_id = execute_insert('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        return jsonify({'id': user_id, 'username': username}), 201
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Username already exists'}), 409

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    user = execute_query('SELECT * FROM users WHERE username = ?', (username,), one=True)
    
    if user and user['password'] == password:
        return jsonify({'id': user['id'], 'username': user['username']}), 200
    else:
        return jsonify({'error': 'Invalid credentials'}), 401
