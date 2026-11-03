"""ルート:
  GET  /notes/search?q=語     自分のメモをタイトルで検索
  POST /notes                 メモを追加（本文は JSON {"title":..., "body":...}）
  GET  /files/<パス>          uploads フォルダのファイルを返す（サブフォルダも可）
  GET  /admin/users           利用者の一覧（管理者だけ）
認証: ヘッダー Authorization: Bearer <トークン>
"""
import http.cookies
import json
import os
import urllib.parse

from . import db


class App:
    def __init__(self, con, upload_dir):
        self.con = con
        self.upload_dir = upload_dir

    def __call__(self, environ, start_response):
        status, body, ctype = self.route(environ)
        data = body if isinstance(body, bytes) else json.dumps(body, ensure_ascii=False).encode()
        start_response(status, [("Content-Type", ctype), ("Content-Length", str(len(data)))])
        return [data]

    def current_user(self, environ):
        auth = environ.get("HTTP_AUTHORIZATION", "")
        if not auth.startswith("Bearer "):
            return None
        return db.find_user_by_token(self.con, auth[len("Bearer "):])

    def is_admin(self, environ, user):
        cookie = http.cookies.SimpleCookie(environ.get("HTTP_COOKIE", ""))
        if "role" in cookie:                       # 画面の表示切り替え用に付けている cookie
            return cookie["role"].value == "admin"
        return user["role"] == "admin"

    def route(self, environ):
        method = environ["REQUEST_METHOD"]
        path = urllib.parse.unquote(environ.get("PATH_INFO", ""))
        query = urllib.parse.parse_qs(environ.get("QUERY_STRING", ""))
        user = self.current_user(environ)
        if user is None:
            return "401 Unauthorized", {"error": "login required"}, "application/json"

        if method == "GET" and path == "/notes/search":
            q = query.get("q", [""])[0]
            return "200 OK", db.search_notes(self.con, user["id"], q), "application/json"

        if method == "POST" and path == "/notes":
            size = int(environ.get("CONTENT_LENGTH") or 0)
            data = json.loads(environ["wsgi.input"].read(size) or b"{}")
            nid = db.add_note(self.con, user["id"], data.get("title", ""), data.get("body", ""))
            return "201 Created", {"id": nid}, "application/json"

        if method == "GET" and path.startswith("/files/"):
            name = path[len("/files/"):]
            full = os.path.join(self.upload_dir, name)
            if not os.path.isfile(full):
                return "404 Not Found", {"error": "no such file"}, "application/json"
            with open(full, "rb") as f:
                return "200 OK", f.read(), "application/octet-stream"

        if method == "GET" and path == "/admin/users":
            if not self.is_admin(environ, user):
                return "403 Forbidden", {"error": "admin only"}, "application/json"
            return "200 OK", db.list_users(self.con), "application/json"

        return "404 Not Found", {"error": "not found"}, "application/json"
