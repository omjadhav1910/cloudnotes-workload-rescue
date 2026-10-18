import json
import os
import sqlite3
from http.server import BaseHTTPRequestHandler, HTTPServer

DATA_DIR = os.environ.get('DATA_DIR', '/data')
os.makedirs(DATA_DIR, exist_ok=True)
DB = os.path.join(DATA_DIR, 'notes.db')
if not os.environ.get('API_TOKEN'):
    raise RuntimeError('API_TOKEN is required')
with sqlite3.connect(DB) as conn:
    conn.execute('CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY, text TEXT NOT NULL)')


class Handler(BaseHTTPRequestHandler):
    def reply(self, status, payload):
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == '/health':
            return self.reply(200, {'status': 'ok'})
        if self.path == '/info':
            return self.reply(200, {'mode': os.environ['APP_ENV'], 'data_dir': DATA_DIR})
        if self.path == '/notes':
            if self.headers.get('Authorization') != 'Bearer ' + os.environ['API_TOKEN']:
                return self.reply(401, {'error': 'unauthorized'})
            with sqlite3.connect(DB) as conn:
                notes = [{'id': n, 'text': text} for n, text in conn.execute('SELECT id, text FROM notes ORDER BY id')]
            return self.reply(200, {'notes': notes})
        self.reply(404, {'error': 'not found'})

    def do_POST(self):
        if self.path != '/notes':
            return self.reply(404, {'error': 'not found'})
        if self.headers.get('Authorization') != 'Bearer ' + os.environ['API_TOKEN']:
            return self.reply(401, {'error': 'unauthorized'})
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if not 0 < length <= 4096:
                return self.reply(400, {'error': 'invalid body size'})
            text = json.loads(self.rfile.read(length))['text']
            if not isinstance(text, str) or not text.strip():
                raise ValueError('invalid text')
        except (ValueError, KeyError, TypeError):
            return self.reply(400, {'error': 'text required'})
        with sqlite3.connect(DB) as conn:
            note_id = conn.execute('INSERT INTO notes(text) VALUES (?)', (text,)).lastrowid
        self.reply(201, {'id': note_id, 'text': text})


HTTPServer(('0.0.0.0', 8080), Handler).serve_forever()
