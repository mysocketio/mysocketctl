import click

from mysocketctl.utils import *


@click.group()
def socket():
    """Manage your global sockets"""
    pass


def get_sockets(authorization_header):
    api_answer = requests.get(api_url + "connect", headers=authorization_header)
    validate_response(api_answer)
    return api_answer.json()


def new_socket(
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
        api_url + "socket", data=json.dumps(params), headers=authorization_header
    )
    validate_response(api_answer)
    return api_answer.json()


def delete_socket(authorization_header, socket_id):
    api_answer = requests.delete(
        api_url + "socket/" + socket_id, headers=authorization_header
    )
    validate_response(api_answer)
    return api_answer


@socket.command()
def ls():
    table = PrettyTable(
        field_names=["socket_id", "dns_name", "type", "port(s)", "name"]
    )
    table.align = "l"
    table.border = True

    authorization_header = get_auth_header()
    sockets = get_sockets(authorization_header)
    for socket in sockets:
        ports_str = listToStr = " ".join(
            [str(elem) for elem in socket["socket_tcp_ports"]]
        )
        row = [
            socket["socket_id"],
            socket["dnsname"],
            socket["socket_type"],
            ports_str,
            socket["name"],
        ]
        table.add_row(row)
    print(table)


@socket.command()
@click.option("--name", required=True, type=str)
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
def create(name, protected, username, password, type):

    if protected:
        if not username:
            print("--username required when using --protected")
            sys.exit(1)
        if not password:
            print("--password required when using --protected")
            sys.exit(1)
    if not name:
        name = ""
    if type not in ["http", "https", "tcp", "tls"]:
        print("--type should be either http, https, tcp or tls")
        sys.exit(1)

    authorization_header = get_auth_header()
    socket = new_socket(
        authorization_header, name, protected, str(username), str(password), str(type)
    )

    ssh_server = "ssh.mysocket.io"

    table = PrettyTable()

    table.align = "l"
    table.border = True
    ports_str = listToStr = " ".join([str(elem) for elem in socket["socket_tcp_ports"]])
    table.field_names = ["socket_id", "dns_name", "port(s)", "type", "name"]
    if type in ["tcp", "tls"]:
        tcp_ports = socket["socket_tcp_ports"]
        row = [
            socket["socket_id"],
            socket["dnsname"],
            ports_str,
            socket["socket_type"],
            socket["name"],
        ]
    else:
        row = [
            socket["socket_id"],
            socket["dnsname"],
            ports_str,
            socket["socket_type"],
            socket["name"],
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


@socket.command()
@click.option("--socket_id", required=True, type=str)
def delete(socket_id):
    authorization_header = get_auth_header()
    delete_socket(authorization_header, socket_id)
    print("Socket " + socket_id + " deleted")
