import unittest
from unittest.mock import patch

import utils

# connect is reserved so have to rename it to _connect
from mysocketctl.connect import connect as _connect
from httmock import urlmatch, with_httmock, response
from click.testing import CliRunner
from test_socket import socket_delete


@urlmatch(netloc="api.mysocket.io", path="/connect")
def connect(url, request):
    return response(
        200,
        {
            "tunnels": [{"local_port": 1, "tunnel_server": "localhost"}],
            "user_name": "A",
            "socket_id": "B",
            "socket_tcp_ports": [80, 443],
            "dnsname": "connect.localhost",
            "socket_type": "http",
            "name": "a name",
        },
    )


@patch("mysocketctl.utils.open", new_callable=utils.iterable_mock_open, read_data=utils.make_jwt())
class TestConnect(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.runner = CliRunner()

    @with_httmock(connect, socket_delete)
    @patch("time.sleep", return_value=True)
    @patch("mysocketctl.ssh.system.SystemSSH.is_enabled", return_value=True)
    @patch("mysocketctl.ssh.system.SystemSSH.connect", side_effect=KeyboardInterrupt)
    def test_connect_system(self, connect, *args):
        result = self.runner.invoke(_connect, ["--port", "1", "--engine", "system"])
        connect.assert_called_once()
        self.assertEqual(result.exit_code, 0)

    def test_protected_no_creds(self, *args):
        result = self.runner.invoke(_connect, ["--port", "1", "--engine", "system", "--protected"])
        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("--username required when using --protected", result.stdout)

    def test_protected_no_password(self, *args):
        result = self.runner.invoke(
            _connect,
            ["--port", "1", "--engine", "system", "--protected", "--username", "a"],
        )
        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("--password required when using --protected", result.stdout)

    @with_httmock(connect, socket_delete)
    @patch("time.sleep", return_value=True)
    @patch("mysocketctl.ssh.system.SystemSSH.is_enabled", return_value=True)
    @patch("mysocketctl.ssh.system.SystemSSH.connect", side_effect=KeyboardInterrupt)
    def test_protected_creds(self, *args):
        result = self.runner.invoke(
            _connect,
            [
                "--port",
                "1",
                "--engine",
                "system",
                "--protected",
                "--username",
                "A",
                "--password",
                "B",
            ],
        )
        self.assertEqual(result.exit_code, 0)


if __name__ == "__main__":
    unittest.main()
