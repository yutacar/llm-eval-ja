"""テスト用の小さなクライアントと、テストデータ。"""
import io
import json
import os
import tempfile
import urllib.parse

from memoapp import db
from memoapp.app import App

ALICE, BOB, ADMIN = "tok-alice-7f3a", "tok-bob-91c2", "tok-admin-5d0e"


def make_app():
    con = db.connect()
    db.init(con)
    con.executemany("INSERT INTO users (id, name, token, role) VALUES (?, ?, ?, ?)",
                    [(1, "alice", ALICE, "user"), (2, "bob", BOB, "user"), (3, "root", ADMIN, "admin")])
    con.commit()
    db.add_note(con, 1, "Meeting notes", "議事録")
    db.add_note(con, 1, "O'Brien memo", "取引先")
    db.add_note(con, 2, "Bob secret plan", "ボブの秘密")
    root = tempfile.mkdtemp()
    up = os.path.join(root, "uploads")
    os.makedirs(os.path.join(up, "docs"))
    with open(os.path.join(up, "docs", "readme.txt"), "w") as f:
        f.write("hello")
    with open(os.path.join(up, "a..b.txt"), "w") as f:
        f.write("dots")
    with open(os.path.join(root, "secret.txt"), "w") as f:
        f.write("TOP SECRET")
    return App(con, up)


def call(app, method, path, token=None, cookie=None, body=None):
    raw_path, _, qs = path.partition("?")
    data = json.dumps(body).encode() if body is not None else b""
    env = {"REQUEST_METHOD": method, "PATH_INFO": urllib.parse.unquote(raw_path), "QUERY_STRING": qs,
           "CONTENT_LENGTH": str(len(data)), "wsgi.input": io.BytesIO(data)}
    if token is not None:
        env["HTTP_AUTHORIZATION"] = f"Bearer {token}"
    if cookie:
        env["HTTP_COOKIE"] = cookie
    got = {}

    def start_response(status, headers):
        got["status"] = int(status.split()[0])

    out = b"".join(app(env, start_response))
    try:
        return got["status"], json.loads(out)
    except ValueError:
        return got["status"], out
