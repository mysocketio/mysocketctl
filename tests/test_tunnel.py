import unittest
import mysocketctl.tunnel
from unittest.mock import patch

import utils
from httmock import urlmatch, with_httmock, response
from mysocketctl.tunnel import tunnel
from click.testing import CliRunner
from test_account import account


@urlmatch(netloc="api.mysocket.io", path=r"/socket/[^/]+/tunnel", method="GET")
def get_tunnels(url, request):
    return response(
        200,
        [{"tunnel_id": "tun", "tunnel_server": "tunnel.example.com", "local_port": 1}],
    )


@urlmatch(netloc="api.mysocket.io", path=r"/socket/[^/]+/tunnel/[^/]+", method="GET")
def get_tunnel(url, request):
    return response(
        200,
        {"tunnel_id": "tun", "tunnel_server": "tunnel.example.com", "local_port": 1},
    )


@urlmatch(netloc="api.mysocket.io", path=r"/socket/[^/]+/tunnel", method="POST")
def create_tunnel(url, request):
    return response(
        200,
        {"tunnel_id": "tun", "tunnel_server": "tunnel.example.com", "local_port": 1},
    )


@urlmatch(netloc="api.mysocket.io", path=r"/socket/[^/]+/tunnel/[^/]+", method="DELETE")
def delete_tunnel(url, request):
    return response(200, {})


class TestUtilityFunctions(unittest.TestCase):
    @with_httmock(account)
    def test_ssh_username(self):
        mysocketctl.tunnel.get_ssh_username(None)

    @with_httmock(get_tunnels)
    def test_get_tunnels(self):
        mysocketctl.tunnel.get_tunnels(None, "socket")

    @with_httmock(get_tunnel)
    def test_get_tunnel_info(self):
        mysocketctl.tunnel.get_tunnel_info(None, "socket", "tunnel")

    @with_httmock(create_tunnel)
    def test_new_tunnel(self):
        mysocketctl.tunnel.new_tunnel(None, "socket")

    @with_httmock(delete_tunnel)
    def test_delete_tunnel(self):
        mysocketctl.tunnel.delete_tunnel(None, "socket", "tunnel")


@patch("mysocketctl.utils.open", new_callable=utils.iterable_mock_open, read_data=utils.make_jwt())
class TestTunnels(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.runner = CliRunner()

    @with_httmock(create_tunnel)
    def test_create(self, tokenfile):
        result = self.runner.invoke(tunnel, ["create", "--socket_id", "A"])
        self.assertEqual(0, result.exit_code)
        self.assertIn("tunnel.example.com", result.stdout)

    @with_httmock(delete_tunnel)
    def test_delete(self, tokenfile):
        tunnel_id = "B"
        result = self.runner.invoke(
            tunnel, ["delete", "--socket_id", "A", "--tunnel_id", tunnel_id]
        )
        self.assertEqual(0, result.exit_code)
        self.assertIn(f"Tunnel {tunnel_id} deleted", result.stdout)

    @with_httmock(get_tunnel, account)
    @patch("time.sleep", return_value=True)
    @patch("mysocketctl.ssh.system.SystemSSH.is_enabled", return_value=True)
    @patch("mysocketctl.ssh.system.SystemSSH.connect", side_effect=KeyboardInterrupt)
    def test_connect(self, connect, enabled, _sleep, tokenfile):
        result = self.runner.invoke(
            tunnel,
            [
                "connect",
                "--socket_id",
                "A",
                "--tunnel_id",
                "B",
                "--port",
                "1",
                "--engine",
                "system",
            ],
        )
        self.assertEqual(0, result.exit_code)
        connect.assert_called_once()

    @with_httmock(get_tunnels)
    def test_list(self, tokenfile):
        result = self.runner.invoke(tunnel, ["ls", "--socket_id", "A"])
        self.assertEqual(0, result.exit_code)
        self.assertIn("tunnel.example.com", result.stdout)


if __name__ == "__main__":
    unittest.main()
