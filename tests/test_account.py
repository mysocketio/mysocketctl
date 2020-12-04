import unittest
import mysocketctl.account
from unittest.mock import patch

import utils
from httmock import urlmatch, with_httmock, response
from click.testing import CliRunner


@urlmatch(netloc="api.mysocket.io", path=r"/user")
def account(url, request):
    return response(
        200,
        {
            "name": "user",
            "email": "test@example.com",
            "user_id": 1,
            "user_name": "test",
            "sshkey": "NotARealKey",
        },
    )


class TestUtilityFunctions(unittest.TestCase):
    @with_httmock(account)
    def test_show_account(self):
        mysocketctl.account.show_account(None, 1)

    @with_httmock(account)
    def test_create_account(self):
        mysocketctl.account.create_account(
            "user", "test@example.com", "NotAPassword", "NotARealKey"
        )


@patch("mysocketctl.utils.open", new_callable=utils.iterable_mock_open, read_data=utils.make_jwt())
class TestAccount(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.runner = CliRunner()

    @with_httmock(account)
    def test_create_with_key(self, *args):
        result = self.runner.invoke(
            mysocketctl.account.account,
            [
                "create",
                "--name",
                "user",
                "--email",
                "test@examplle.com",
                "--password",
                "NotAPassword",
                "--sshkey",
                "NotARealKey",
            ],
        )
        self.assertEqual(0, result.exit_code)
        self.assertIn("Congratulation!", result.stdout)

    @with_httmock(account)
    @patch("os.path.exists", return_value=True)
    @patch(
        "mysocketctl.account.open", new_callable=utils.iterable_mock_open, read_data="NotARealKey"
    )
    def test_create_with_file(self, mopen, *args):
        result = self.runner.invoke(
            mysocketctl.account.account,
            [
                "create",
                "--name",
                "user",
                "--email",
                "test@examplle.com",
                "--password",
                "NotAPassword",
                "--sshkey",
                "notakey.pub",
            ],
        )
        self.assertEqual(0, result.exit_code)
        self.assertIn("Congratulation!", result.stdout)
        mopen.assert_called_once_with("notakey.pub", "r")

    @with_httmock(account)
    @patch("os.path.exists", return_value=True)
    @patch("mysocketctl.account.open", side_effect=PermissionError)
    def test_create_with_nonreadable(self, mopen, *args):
        result = self.runner.invoke(
            mysocketctl.account.account,
            [
                "create",
                "--name",
                "user",
                "--email",
                "test@examplle.com",
                "--password",
                "NotAPassword",
                "--sshkey",
                "notakey.pub",
            ],
        )
        self.assertEqual(0, result.exit_code)
        self.assertIn("Unable to read", result.stdout)

    @with_httmock(account)
    def test_show(self, *args):
        result = self.runner.invoke(
            mysocketctl.account.account,
            [
                "show",
            ],
        )
        self.assertEqual(0, result.exit_code)
        self.assertIn("test@example.com", result.stdout)


if __name__ == "__main__":
    unittest.main()
