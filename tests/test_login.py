import unittest
from unittest.mock import patch

import utils
from httmock import urlmatch, with_httmock, response
from mysocketctl.login import login
from click.testing import CliRunner


FAKE_TOKEN = "NotAValidTokenButWhoCares"
SERVER_ERR_CODE = 500
SERVER_ERR_MESG = "SERVER ERROR"


@urlmatch(netloc="api.mysocket.io", path="/login")
def invalid_login(url, request):
    return response(401, {"error": "Authentication failed"})


@urlmatch(netloc="api.mysocket.io", path="/login")
def valid_login(url, request):
    return response(200, {"token": FAKE_TOKEN})


@urlmatch(netloc="api.mysocket.io", path="/login")
def server_error(url, request):
    return response(SERVER_ERR_CODE, SERVER_ERR_MESG)


@patch("mysocketctl.utils.open", new_callable=utils.iterable_mock_open, read_data=utils.make_jwt())
class TestLogin(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.runner = CliRunner()

    def test_bare_login(self, *args):
        result = self.runner.invoke(login)
        self.assertNotEqual(result.exit_code, 0)

    @with_httmock(invalid_login)
    def test_invalid_login(self, *args):
        result = self.runner.invoke(login, ["--email", "X", "--password", "Y"])
        self.assertIn("Login failed", result.stdout)
        self.assertNotEqual(result.exit_code, 0)

    @with_httmock(valid_login)
    @patch("mysocketctl.login.open", new_callable=utils.iterable_mock_open)
    def test_valid_login(self, write_token, *args):
        result = self.runner.invoke(login, ["--email", "X", "--password", "Y"])
        write_token.assert_called_once()
        write_token().write.assert_called_once_with(FAKE_TOKEN)
        self.assertIn("Logged in!", result.stdout)
        self.assertEqual(result.exit_code, 0)

    @with_httmock(server_error)
    def test_server_error(self, *args):
        result = self.runner.invoke(login, ["--email", "X", "--password", "Y"])
        self.assertIn(f"{SERVER_ERR_CODE}: {SERVER_ERR_MESG}", result.stdout)
        self.assertNotEqual(result.exit_code, 0)


if __name__ == "__main__":
    unittest.main()
