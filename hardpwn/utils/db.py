import sqlite3
import json
import os
import time

class HardpwnDB:
    def __init__(self, path='results/hardpwn.db'):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self._init_schema()

    def _init_schema(self):
        c = self.conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS probes (
            id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT, interface TEXT, data TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS chips (
            id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT, type TEXT, vendor TEXT, name TEXT, details TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS dumps (
            id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT, path TEXT, size INTEGER)''')
        c.execute('''CREATE TABLE IF NOT EXISTS glitches (
            id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT, params TEXT, result TEXT)''')
        self.conn.commit()

    def log_probe(self, interface, data):
        ts = time.ctime()
        self.conn.execute('INSERT INTO probes (ts,interface,data) VALUES (?, ?, ?)',
                          (ts, interface, json.dumps(data)))
        self.conn.commit()

    def log_chip(self, ctype, vendor, name, details):
        ts = time.ctime()
        self.conn.execute('INSERT INTO chips (ts,type,vendor,name,details) VALUES (?,?,?,?,?)',
                          (ts, ctype, vendor, name, json.dumps(details)))
        self.conn.commit()

    def log_dump(self, path):
        ts = time.ctime()
        try:
            size = os.path.getsize(path)
        except Exception:
            size = 0
        self.conn.execute('INSERT INTO dumps (ts,path,size) VALUES (?,?,?)',
                          (ts, path, size))
        self.conn.commit()

    def log_glitch(self, params, result):
        ts = time.ctime()
        self.conn.execute('INSERT INTO glitches (ts,params,result) VALUES (?,?,?)',
                          (ts, json.dumps(params), json.dumps(result)))
        self.conn.commit()

    def export_json(self, path='results/session.json'):
        out = {'probes':[], 'chips':[], 'dumps':[], 'glitches':[]}
        c = self.conn.cursor()
        for table in out.keys():
            rows = c.execute(f'SELECT * FROM {table}').fetchall()
            cols = [d[0] for d in c.execute(f'PRAGMA table_info({table})')]
            out[table] = [dict(zip(cols,row)) for row in rows]
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path,'w') as fh:
            json.dump(out, fh, indent=2)
        return path
