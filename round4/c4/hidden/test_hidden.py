import unittest

from tests.helper import make_app, call, ALICE, BOB, ADMIN


def titles(body):
    return sorted(n["title"] for n in body) if isinstance(body, list) else []


class FeatureTest(unittest.TestCase):
    """正しい使い方は今までどおり動くこと。"""
    def setUp(self):
        self.app = make_app()

    def test_search(self):
        self.assertEqual(titles(call(self.app, "GET", "/notes/search?q=Meeting", token=ALICE)[1]), ["Meeting notes"])
        self.assertEqual(titles(call(self.app, "GET", "/notes/search?q=", token=ALICE)[1]), ["Meeting notes", "O'Brien memo"])

    def test_search_with_quote(self):
        st, body = call(self.app, "GET", "/notes/search?q=O'Brien", token=ALICE)
        self.assertEqual((st, titles(body)), (200, ["O'Brien memo"]))

    def test_add_note_with_symbols(self):
        call(self.app, "POST", "/notes", token=BOB, body={"title": "it's 100% done; --ok", "body": "x"})
        self.assertEqual(titles(call(self.app, "GET", "/notes/search?q=it's", token=BOB)[1]), ["it's 100% done; --ok"])

    def test_files(self):
        self.assertEqual(call(self.app, "GET", "/files/docs/readme.txt", token=ALICE), (200, b"hello"))
        self.assertEqual(call(self.app, "GET", "/files/a..b.txt", token=ALICE), (200, b"dots"))
        self.assertEqual(call(self.app, "GET", "/files/docs/nothing.txt", token=ALICE)[0], 404)

    def test_admin(self):
        self.assertEqual(call(self.app, "GET", "/admin/users", token=ADMIN)[0], 200)
        self.assertEqual(call(self.app, "GET", "/admin/users", token=ADMIN, cookie="role=user")[0], 200)

    def test_login(self):
        self.assertEqual(call(self.app, "GET", "/notes/search?q=a")[0], 401)
        self.assertEqual(call(self.app, "GET", "/notes/search?q=a", token="wrong")[0], 401)


class AttackTest(unittest.TestCase):
    """穴が塞がっていること。"""
    def setUp(self):
        self.app = make_app()

    def test_search_injection(self):
        for q in ["' OR 1=1 --", "%' OR '1'='1", "x' UNION SELECT id, token FROM users --"]:
            with self.subTest(q=q):
                st, body = call(self.app, "GET", "/notes/search?q=" + q, token=ALICE)
                self.assertNotIn("Bob secret plan", titles(body))
                self.assertNotIn(ADMIN, str(body))

    def test_token_injection(self):
        for tok in ["' OR '1'='1", "' OR role='admin' --", "x' OR 1=1 --"]:
            with self.subTest(tok=tok):
                self.assertEqual(call(self.app, "GET", "/notes/search?q=", token=tok)[0], 401)
                self.assertNotEqual(call(self.app, "GET", "/admin/users", token=tok)[0], 200)

    def test_path_traversal(self):
        for p in ["../secret.txt", "docs/../../secret.txt", "..%2Fsecret.txt", "%2e%2e/secret.txt", "/etc/passwd",
                  "docs/../../uploads/../secret.txt"]:
            with self.subTest(p=p):
                st, body = call(self.app, "GET", "/files/" + p, token=ALICE)
                self.assertNotEqual(st, 200)
                self.assertNotIn(b"SECRET", body if isinstance(body, bytes) else b"")

    def test_admin_cookie(self):
        for c in ["role=admin", "role=admin; theme=dark"]:
            with self.subTest(c=c):
                self.assertEqual(call(self.app, "GET", "/admin/users", token=ALICE, cookie=c)[0], 403)


if __name__ == "__main__":
    unittest.main()
