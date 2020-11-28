import json
import unittest
from unittest.mock import patch, mock_open

import mysocketctl.socket
import utils
from httmock import urlmatch, with_httmock, response
from mysocketctl.socket import socket
from click.testing import CliRunner


@urlmatch(netloc="api.mysocket.io", path="/socket")
def socket_create(url, request):
    body = json.loads(request.body)
    return response(
        200,
        {
            "socket_id": "A",
            "dnsname": "socket.example.com",
            "socket_tcp_ports": [80, 443],
            "socket_type": body["socket_type"],
            "name": body["name"],
        },
    )


@urlmatch(netloc="api.mysocket.io", path="/connect")
def get_sockets(url, request):
    return response(
        200,
        [
            {
                "socket_id": "A",
                "dnsname": "socket.example.com",
                "socket_tcp_ports": [80, 443],
                "socket_type": "http",
                "name": "test socket",
            }
        ],
    )


@urlmatch(netloc="api.mysocket.io", path=r"/socket/[^/]+", method="delete")
def socket_delete(url, request):
    return response(200)


@patch("mysocketctl.utils.open", new_callable=mock_open, read_data=utils.make_jwt())
class TestGetSockets(unittest.TestCase):
    @with_httmock(get_sockets)
    def test_success(self, tokenfile):
        mysocketctl.socket.get_sockets(None)


@patch("mysocketctl.utils.open", new_callable=mock_open, read_data=utils.make_jwt())
class TestSockets(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.runner = CliRunner()

    @with_httmock(socket_create)
    def test_create(self, tokenfile):
        result = self.runner.invoke(socket, ["create", "--name", "test", "--type", "http"])
        self.assertEqual(result.exit_code, 0)
        # Case insensitive
        result = self.runner.invoke(socket, ["create", "--name", "test", "--type", "hTTp"])
        self.assertEqual(result.exit_code, 0)

    @with_httmock(socket_create)
    def test_create_protected(self, tokenfile):
        result = self.runner.invoke(
            socket, ["create", "--name", "test", "--type", "http", "--protected"]
        )
        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("--username required when using --protected", result.stdout)

        result = self.runner.invoke(
            socket,
            [
                "create",
                "--name",
                "test",
                "--type",
                "http",
                "--protected",
                "--username",
                "A",
            ],
        )
        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("--password required when using --protected", result.stdout)

        result = self.runner.invoke(
            socket,
            [
                "create",
                "--name",
                "test",
                "--type",
                "http",
                "--protected",
                "--username",
                "A",
                "--password",
                "B",
            ],
        )
        self.assertEqual(result.exit_code, 0)

    @with_httmock(get_sockets)
    def test_ls(self, tokenfile):
        result = self.runner.invoke(socket, ["ls"])
        self.assertEqual(result.exit_code, 0)

    @with_httmock(socket_delete)
    def test_delete(self, tokenfile):
        socket_name = "A"
        result = self.runner.invoke(socket, ["delete", "--socket_id", socket_name])
        self.assertEqual(result.exit_code, 0)
        self.assertIn(f"Socket {socket_name} deleted", result.stdout)


if __name__ == "__main__":
    unittest.main()
