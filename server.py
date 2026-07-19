from flask import Flask, request, jsonify, send_from_directory
from pathlib import Path
import json
import uuid
from datetime import datetime, timezone
import os

app = Flask(__name__, static_folder='.')
DATA_FILE = Path(__file__).parent / 'data' / 'todos.json'

def load():
    if DATA_FILE.exists():
        with open(DATA_FILE, encoding='utf-8') as f:
            return json.load(f)
    return []

def save(todos):
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(todos, f, indent=2)

@app.route('/api/todos', methods=['GET'])
def get_todos():
    todos = load()
    return jsonify(sorted(todos, key=lambda t: t.get('createdAt', ''), reverse=True))

@app.route('/api/todos', methods=['POST'])
def create_todo():
    data = request.get_json()
    if not data or not data.get('text', '').strip():
        return jsonify({'error': 'Text is required'}), 400
    todos = load()
    todo = {
        'id': uuid.uuid4().hex,
        'text': data['text'].strip(),
        'completed': False,
        'createdAt': datetime.now(timezone.utc).isoformat(),
    }
    todos.append(todo)
    save(todos)
    return jsonify(todo), 201

@app.route('/api/todos/<todo_id>', methods=['PUT'])
def update_todo(todo_id):
    data = request.get_json()
    todos = load()
    for t in todos:
        if t['id'] == todo_id:
            if 'text' in data and data['text'].strip():
                t['text'] = data['text'].strip()
            if 'completed' in data:
                t['completed'] = data['completed']
            save(todos)
            return jsonify(t)
    return jsonify({'error': 'Not found'}), 404

@app.route('/api/todos/<todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    todos = load()
    todos = [t for t in todos if t['id'] != todo_id]
    save(todos)
    return '', 204

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
