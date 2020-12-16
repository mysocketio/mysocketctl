import socket
import select
import sys
import threading
import os

from paramiko import SSHClient
from paramiko.client import AutoAddPolicy


class LogOutput(threading.Thread):
    def __init__(self, sock):
        self.event = threading.Event()
        self._sock = sock
        super().__init__(daemon=True)

    def run(self):
        while not self.event.is_set():
            try:
                data = self._sock.recv(1024)
            except Exception as e:
                sys.stderr.write(f"Exception getting log from MySocket.io:\n{e}\n")
                sys.stderr.flush()
                break
            if not data:
                sys.stderr.write("Lost connection to MySocket.io, disconnecting...\n")
                sys.stderr.flush()
                # Let this fall through and attempt to reconnect
                break
            sys.stdout.write(data.decode("UTF-8"))
            sys.stdout.flush()
        self._sock.close()


class ForwardingThread(threading.Thread):
    def __init__(self, chan, host, port):
        self._chan = chan
        self._host = host
        self._port = port
        super().__init__(daemon=True)

    def run(self):
        sock = socket.socket()
        try:
            sock.connect((self._host, self._port))
        except Exception as e:
            sys.stderr.write(
                f"Forwarding request to {self._host}:{self._port} failed:\n{e}\n"
            )
            sys.stderr.flush()
            return

        while True:
            try:
                r, w, x = select.select([sock, self._chan], [], [])
                if sock in r:
                    data = sock.recv(1024)
                    if len(data) == 0:
                        break
                    self._chan.send(data)
                if self._chan in r:
                    data = self._chan.recv(1024)
                    if len(data) == 0:
                        break
                    sock.send(data)
            except (EOFError, OSError) as e:
                sys.stderr.write(
                    f"Disconnecting client, unable to send/recv data:\n{e}\n"
                )
                sys.stderr.flush()
                break
        self._chan.close()
        sock.close()


class Paramiko(object):
    def __init__(self):
        self.client = SSHClient()
        self.client.set_missing_host_key_policy(AutoAddPolicy)

    def is_enabled(self):
        return True

    def reverse_forward_tunnel(self, server_port, remote_host, remote_port):
        transport = self.client.get_transport()
        transport.set_keepalive(30)
        transport.request_port_forward("localhost", server_port)
        while True:
            # Wait 10 seconds for a new client
            chan = transport.accept(10)
            # Check if we have an exception in the transport
            e = transport.get_exception()
            # No client and no exception, do it again!
            if chan is None and e is None:
                continue
            elif e is not None:
                sys.stderr.write(f"Disconnected from MySocket.io tunnel:\n{e}\n")
                sys.stderr.flush()
                break
            thr = ForwardingThread(chan, remote_host, remote_port)
            thr.start()

    def connect(
        self, port, remote_bind_port, ssh_server, ssh_user, client_host="localhost"
    ):
        try:
            self.client.connect(ssh_server, username=ssh_user, timeout=10)
        except Exception as e:
            sys.stderr.write(f"Couldn't connect to MySocket.io server:\n{e}\n")
            sys.stderr.flush()
            self.client.close()
            return

        log_thread = LogOutput(
            self.client.invoke_shell(term=os.environ.get("TERM", "vt100"))
        )
        log_thread.start()

        # This enters an infinite loop, so anything important must happen before this
        try:
            self.reverse_forward_tunnel(remote_bind_port, client_host, int(port))
        # This is to match the behavior we see in SystemSSH where you need to ^C twice
        except KeyboardInterrupt:
            pass
        except Exception as e:
            sys.stderr.write(f"Error setting up MySocket.io tunnel:\n{e}\n")
            sys.stderr.flush()

        self.client.close()
        log_thread.event.set()
        log_thread.join()
