import unittest

from tests.helper import make_app, call, ALICE, BOB, ADMIN


class AppTest(unittest.TestCase):
    def setUp(self):
        self.app = make_app()

    def test_login_required(self):
        self.assertEqual(call(self.app, "GET", "/notes/search?q=a")[0], 401)

    def test_search_own_notes(self):
        st, body = call(self.app, "GET", "/notes/search?q=Meeting", token=ALICE)
        self.assertEqual((st, [n["title"] for n in body]), (200, ["Meeting notes"]))

    def test_add_note(self):
        st, body = call(self.app, "POST", "/notes", token=BOB, body={"title": "new", "body": "x"})
        self.assertEqual(st, 201)
        self.assertEqual([n["title"] for n in call(self.app, "GET", "/notes/search?q=new", token=BOB)[1]], ["new"])

    def test_file(self):
        self.assertEqual(call(self.app, "GET", "/files/docs/readme.txt", token=ALICE), (200, b"hello"))

    def test_admin(self):
        self.assertEqual(call(self.app, "GET", "/admin/users", token=ADMIN)[0], 200)
        self.assertEqual(call(self.app, "GET", "/admin/users", token=ALICE)[0], 403)


if __name__ == "__main__":
    unittest.main()
