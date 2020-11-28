import os
import unittest
from io import StringIO
from unittest.mock import patch, mock_open
from time import time

import jwt
import utils
import mysocketctl.utils


@patch("sys.stdout", new_callable=StringIO)
class TestSSHTunnel(unittest.TestCase):
    @patch("mysocketctl.ssh.system.SystemSSH.is_enabled", return_value=False)
    @patch("mysocketctl.ssh.system.SystemSSH.connect", side_effect=KeyboardInterrupt())
    @patch("mysocketctl.ssh.paramiko.Paramiko.connect", side_effect=KeyboardInterrupt())
    def test_fallthrough(self, paramiko_connect, sys_connect, sys_enabled, stdout):
        mysocketctl.utils.ssh_tunnel(1, 1, "ssh.example.com", "username")
        paramiko_connect.assert_called_once()
        sys_connect.assert_not_called()

    @patch("mysocketctl.ssh.system.SystemSSH.is_enabled", return_value=False)
    def test_fail_on_disabled(self, sys_enabled, stdout):
        sys_enabled.return_value = False
        mysocketctl.utils.ssh_tunnel(1, 1, "ssh.example.com", "username", engine="system")
        self.assertIn("System SSH does not appear to be avaiable", stdout.getvalue())

    @patch("mysocketctl.ssh.paramiko.Paramiko.connect", side_effect=KeyboardInterrupt())
    def test_use_paramiko(self, connect, stdout):
        mysocketctl.utils.ssh_tunnel(1, 1, "ssh.example.com", "username", engine="paramiko")
        connect.assert_called_once()

    @patch("time.sleep", side_effect=KeyboardInterrupt())
    @patch("mysocketctl.ssh.system.SystemSSH.connect", return_value=True)
    def test_die_on_keyboard_interrupt(self, connect, _sleep, stdout):
        mysocketctl.utils.ssh_tunnel(1, 1, "ssh.example.com", "username", engine="system")
        output = stdout.getvalue()
        self.assertIn("Disconnected", output)
        self.assertIn("Bye", output)
        connect.assert_called_once()


class Response(object):
    def __init__(self, status_code, text=None):
        self.status_code = status_code
        self.text = text


@patch("sys.stdout", new_callable=StringIO)
class TestValidateResponse(unittest.TestCase):
    def test_success(self, _):
        self.assertEqual(mysocketctl.utils.validate_response(Response(200)), 200)
        self.assertEqual(mysocketctl.utils.validate_response(Response(204)), 204)

    def test_auth_fail(self, stdout):
        self.assertRaises(SystemExit, mysocketctl.utils.validate_response, Response(401))
        self.assertEqual(stdout.getvalue().strip(), "Login failed")

    def test_server_error(self, stdout):
        self.assertRaises(
            SystemExit,
            mysocketctl.utils.validate_response,
            Response(500, "Server Error"),
        )
        self.assertEqual(stdout.getvalue().strip(), "500 Server Error")


@patch("sys.stdout", new_callable=StringIO)
class TestAuthHeader(unittest.TestCase):
    @patch(
        "mysocketctl.utils.open",
        new_callable=mock_open,
        read_data=jwt.encode({"user_id": "A", "exp": time() + 24 * 60 * 60}, "NotSecret"),
    )
    def test_valid_token(self, tokenfile, *args):
        mysocketctl.utils.get_auth_header()
        tokenfile.assert_called_with(
            os.path.join(os.path.expanduser("~"), ".mysocketio_token"), "r"
        )

    @patch(
        "mysocketctl.utils.open",
        new_callable=mock_open,
        read_data="This is Not a JWT Token",
    )
    def test_invalid_token(self, tokenfile, stdout):
        self.assertRaises(SystemExit, mysocketctl.utils.get_auth_header)
        tokenfile.assert_called_with(
            os.path.join(os.path.expanduser("~"), ".mysocketio_token"), "r"
        )
        output = stdout.getvalue().strip()
        self.assertIn("barf on ", output)
        self.assertIn("No valid token in", output)

    @patch("mysocketctl.utils.open", side_effect=PermissionError)
    def test_file_perms(self, tokenfile, stdout):
        self.assertRaises(SystemExit, mysocketctl.utils.get_auth_header)
        self.assertIn("Could not read file:", stdout.getvalue())


@patch("mysocketctl.utils.open", new_callable=mock_open, read_data=utils.make_jwt())
class TestGetUserId(unittest.TestCase):
    def test_getuserid(self, tokenfile):
        self.assertIsNotNone(mysocketctl.utils.get_user_id())


if __name__ == "__main__":
    unittest.main()
