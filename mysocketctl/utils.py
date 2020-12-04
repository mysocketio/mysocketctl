import os
import sys
import time
import jwt

from prettytable import PrettyTable
from mysocketctl.ssh import SystemSSH, Paramiko

api_url = "https://api.mysocket.io/"
token_file = os.path.expanduser(os.path.join("~", ".mysocketio_token"))


# For debug
debug = False
if "MYSOCKET_DEBUG" in os.environ:  # pragma: no cover
    if os.environ["MYSOCKET_DEBUG"] == "TRUE":
        try:
            import http.client as http_client

            print("DEBUG ENABLED")
        except ImportError:
            print("unable to import http.client for debug")
        http_client.HTTPConnection.debuglevel = 10
        debug = True


def read_token_file(want_token=True):
    try:
        with open(token_file, "r") as myfile:
            for token in myfile:
                token = token.strip()
                try:
                    data = jwt.decode(token, verify=False)
                    return token if want_token else data
                except (TypeError, jwt.InvalidTokenError):
                    print(f"barf on {token}")
                    continue
    except IOError:
        print("Could not read file:", token_file)
        print("Please login again")
        sys.exit(1)

    print(f"No valid token in {token_file}. Please login again")
    sys.exit(1)


def get_user_id():
    return read_token_file(False)["user_id"]


def get_auth_header():
    token = read_token_file()

    authorization_header = {
        "x-access-token": token,
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    return authorization_header


def validate_response(http_repsonse):
    if debug:  # pragma: no cover
        print("Server responded with data:")
        print(http_repsonse.text)

    if http_repsonse.status_code == 200:
        return http_repsonse.status_code
    if http_repsonse.status_code == 204:
        return http_repsonse.status_code

    elif http_repsonse.status_code == 401:
        print("Login failed")
    else:
        print(http_repsonse.status_code, http_repsonse.text)

    sys.exit(1)


def ssh_tunnel(port, remote_bind_port, ssh_server, ssh_username, host="localhost", engine="auto"):
    print(f"\nConnecting to Server: {ssh_server}\n")

    while True:
        if engine == "auto":
            for ssh in [SystemSSH, Paramiko]:
                client = ssh()
                if client.is_enabled():
                    break
        elif engine == "system":
            client = SystemSSH()
            if not client.is_enabled():
                print("System SSH does not appear to be avaiable")
                return
        elif engine == "paramiko":
            client = Paramiko()

        try:
            client.connect(port, remote_bind_port, ssh_server, ssh_username, host)
        except KeyboardInterrupt:
            print("Bye")
            return

        try:
            print("Disconnected... Automatically reconnecting now..")
            print("Press ctrl-c to exit")
            time.sleep(2)
        except KeyboardInterrupt:
            print("Bye")
            return


def print_sockets(sockets):
    table = PrettyTable()

    table.align = "l"
    table.border = True
    table.field_names = ["socket_id", "dns_name", "port(s)", "type", "name"]
    for socket in sockets:
        ports_str = " ".join([str(elem) for elem in socket["socket_tcp_ports"]])
        row = [
            socket["socket_id"],
            socket["dnsname"],
            ports_str,
            socket["socket_type"],
            socket["name"],
        ]
        table.add_row(row)

    print(table)


def print_protected(username, password):  # pragma: no cover
    protectedtable = PrettyTable(field_names=["username", "password"])
    protectedtable.align = "l"
    protectedtable.border = True
    protectedtable.add_row([str(username), str(password)])
    print("\nProtected Socket, login details:")
    print(protectedtable)
