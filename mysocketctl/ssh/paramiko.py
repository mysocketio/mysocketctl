import socket
import select
import sys
import threading

from paramiko import SSHClient
from paramiko.client import AutoAddPolicy


class Paramiko(object):
    def __init__(self):
        self.client = SSHClient()
        self.client.set_missing_host_key_policy(AutoAddPolicy)

    def is_enabled(self):
        return True

    @staticmethod
    def handler(chan, host, port):
        sock = socket.socket()
        try:
            sock.connect((host, port))
        except Exception as e:
            sys.stderr.write(f"Forwarding request to {host}:{port} failed: {e}")
            sys.stderr.flush()
            return

        while True:
            r, w, x = select.select([sock, chan], [], [])
            try:
                if sock in r:
                    data = sock.recv(1024)
                    if len(data) == 0:
                        break
                    chan.send(data)
                if chan in r:
                    data = chan.recv(1024)
                    if len(data) == 0:
                        break
                    sock.send(data)
            except (EOFError, OSError) as e:
                break
        chan.close()
        sock.close()

    @staticmethod
    def write_logs(sock):
        while True:
            data = sock.recv(1024)
            if not data:
                # Let this fall through and attempt to reconnect
                break
            sys.stdout.write(data.decode("UTF-8"))
            sys.stdout.flush()

    def reverse_forward_tunnel(self, server_port, remote_host, remote_port):
        transport = self.client.get_transport()
        transport.request_port_forward("localhost", server_port)
        while True:
            chan = transport.accept(1000)
            if chan is None:
                continue
            thr = threading.Thread(
                target=Paramiko.handler, args=(chan, remote_host, remote_port)
            )
            thr.setDaemon(True)
            thr.start()

    def print_logs(self):
        chan = self.client.invoke_shell()
        writer = threading.Thread(target=Paramiko.write_logs, args=(chan,))
        writer.setDaemon(True)
        writer.start()

    def connect(
        self, port, remote_bind_port, ssh_server, ssh_user, client_host="localhost"
    ):
        try:
            self.client.connect(ssh_server, username=ssh_user, timeout=10)
        except Exception as e:
            print(f"Couldn't connect {e}")
            self.client.close()
            return
        self.client.get_transport().set_keepalive(30)
        self.print_logs()

        # This enters an infinite loop, so anything important must happen before this
        try:
            self.reverse_forward_tunnel(remote_bind_port, client_host, int(port))
        except KeyboardInterrupt:
            self.client.close()
        except Exception as e:
            print(f"Connection error {e}")
