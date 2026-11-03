import sqlite3


def connect(path=":memory:"):
    con = sqlite3.connect(path)
    con.row_factory = sqlite3.Row
    return con


def init(con):
    con.executescript("""
    CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, token TEXT UNIQUE, role TEXT);
    CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY, owner_id INTEGER, title TEXT, body TEXT);
    """)
    con.commit()


def find_user_by_token(con, token):
    row = con.execute(f"SELECT id, name, role FROM users WHERE token = '{token}'").fetchone()
    return dict(row) if row else None


def search_notes(con, owner_id, q):
    sql = f"SELECT id, title FROM notes WHERE owner_id = {owner_id} AND title LIKE '%{q}%' ORDER BY id"
    return [dict(r) for r in con.execute(sql).fetchall()]


def add_note(con, owner_id, title, body):
    cur = con.execute("INSERT INTO notes (owner_id, title, body) VALUES (?, ?, ?)", (owner_id, title, body))
    con.commit()
    return cur.lastrowid


def list_users(con):
    return [dict(r) for r in con.execute("SELECT id, name, role FROM users ORDER BY id").fetchall()]
