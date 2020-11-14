import click

from mysocketctl.utils import *


@click.group()
def connect():
    """Quckly connect. Wrapper around sockets and tunnels"""
    pass


def new_connection(
    authorization_header,
    connect_name,
    protected_socket,
    protected_user,
    protected_pass,
    socket_type,
):
    if not protected_socket:
        protected_socket = False
    else:
        protected_socket = True

    params = {
        "name": connect_name,
        "protected_socket": protected_socket,
        "protected_username": protected_user,
        "protected_password": protected_pass,
        "socket_type": socket_type,
    }
    api_answer = requests.post(
        api_url + "connect", data=json.dumps(params), headers=authorization_header
    )
    validate_response(api_answer)
    return api_answer.json()


def delete_socket(authorization_header, socket_id):
    api_answer = requests.delete(
        api_url + "socket/" + socket_id, headers=authorization_header
    )
    validate_response(api_answer)
    return api_answer


@connect.command()
@click.option("--port", required=True, type=int, help="Local port to connect")
@click.option("--name", required=False, type=str, default="")
@click.option("--protected", required=False, type=str, default="")
@click.option("--protected/--not-protected", default=False)
@click.option("--username", required=False, type=str, default="")
@click.option("--password", required=False, type=str, default="")
@click.option(
    "--type",
    required=False,
    type=str,
    default="http",
    help="Socket type, http, https, tcp, tls",
)
def connect(port, name, protected, username, password, type):
    """Quckly connect, Wrapper around sockets and tunnels"""

    if protected:
        if not username:
            print("--username required when using --protected")
            sys.exit(1)
        if not password:
            print("--password required when using --protected")
            sys.exit(1)
    if not name:
        name = "Local port " + str(port)
    if type not in ["http", "https", "tcp", "tls"]:
        print("--type should be either http, https, tcp or tls")
        sys.exit(1)

    authorization_header = get_auth_header()
    new_conn = new_connection(
        authorization_header, name, protected, str(username), str(password), str(type)
    )
    remote_bind_port = new_conn["tunnels"][0]["local_port"]
    ssh_server = new_conn["tunnels"][0]["tunnel_server"]
    ssh_server = "ssh.mysocket.io"
    ssh_user = str(new_conn["user_name"])

    table = PrettyTable()

    table.align = "l"
    table.border = True
    if type in ["tcp", "tls"]:
        table.field_names = ["socket_id", "dns_name", "tcp port", "name"]
        tcp_ports = new_conn["socket_tcp_ports"]
        row = [
            new_conn["socket_id"],
            new_conn["dnsname"],
            tcp_ports[0],
            new_conn["name"],
        ]
    else:
        table.field_names = ["socket_id", "dns_name", "name"]
        row = [
            new_conn["socket_id"],
            new_conn["dnsname"],
            new_conn["name"],
        ]

    table.add_row(row)
    print(table)
    if protected:
        protectedtable = PrettyTable(field_names=["username", "password"])
        protectedtable.align = "l"
        protectedtable.border = True
        protectedtable.add_row([str(username), str(password)])
        print("\nProtected Socket, login details:")
        print(protectedtable)

    time.sleep(2)
    ssh_tunnel(str(port),str(remote_bind_port),str(ssh_server),ssh_user)
    print("cleaning up...")
    delete_socket(authorization_header, new_conn["socket_id"])
    sys.exit()
