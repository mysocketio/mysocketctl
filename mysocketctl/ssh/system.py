import subprocess


class SystemSSH(object):
    def __init__(self, path="ssh"):
        self.ssh_path = path

    def is_enabled(self):
        try:
            subprocess.run(
                [self.ssh_path, "-V"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return True
        except FileNotFoundError:
            pass
        return False

    def connect(
        self, port, remote_bind_port, ssh_server, ssh_user, client_host="localhost"
    ):
        ssh_cmd = (
            self.ssh_path,
            "-R",
            f"{remote_bind_port}:{client_host}:{port}",
            "-l",
            ssh_user,
            "-o",
            "StrictHostKeyChecking=no",
            "-o",
            "UserKnownHostsFile=/dev/null",
            "-o",
            "ExitOnForwardFailure=yes",
            "-o",
            "PasswordAuthentication=no",
            "-o",
            "ServerAliveInterval=30",
            "-o",
            "LogLevel=ERROR",
            str(ssh_server),
        )

        cmd_output = subprocess.run(
            ssh_cmd,
            # stdout=subprocess.STDOUT,
            # stderr=subprocess.STDOUT,
            # universal_newlines=False,
        )
