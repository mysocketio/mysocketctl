import click

import mysocketctl.socket
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
    cloudauth,
):
    if not protected_socket:
        protected_socket = False
    else:
        protected_socket = True

    if not cloudauth:
        cloudauth = False
    else:
        cloudauth = True

    params = {
        "name": connect_name,
        "protected_socket": protected_socket,
        "protected_username": protected_user,
        "protected_password": protected_pass,
        "socket_type": socket_type,
        "cloud_authentication_enabled": cloudauth,
    }
    api_answer = requests.post(
        api_url + "connect", data=json.dumps(params), headers=authorization_header
    )
    validate_response(api_answer)
    return api_answer.json()


@connect.command()
@click.option("--port", required=True, type=int, help="Local port to connect")
@click.option("--name", required=False, type=str, default="")
@click.option("--protected/--not-protected", default=False)
@click.option("--username", required=False, type=str, default="")
@click.option("--password", required=False, type=str, default="")
@click.option(
    "--cloudauth/--no-cloudauth", default=False, help="Enable oauth/oidc authentication"
)
@click.option(
    "--type",
    required=False,
    type=click.Choice(["http", "https", "tcp", "tls"], case_sensitive=False),
    default="http",
    help="Socket type, http, https, tcp, tls",
)
@click.option(
    "--engine", default="auto", type=click.Choice(("auto", "system", "paramiko"))
)
@click.pass_context
def connect(ctx, port, name, protected, username, password, type, engine, cloudauth):
    """Quckly connect, Wrapper around sockets and tunnels"""

    if cloudauth:
        cloudauth = True
    else:
        cloudauth = False

    if protected:
        if not username:
            print("--username required when using --protected")
            sys.exit(1)
        if not password:
            print("--password required when using --protected")
            sys.exit(1)
    if not name:
        name = f"Local port {port}"

    authorization_header = get_auth_header()
    new_conn = new_connection(
        authorization_header,
        name,
        protected,
        str(username),
        str(password),
        str(type),
        cloudauth,
    )
    remote_bind_port = new_conn["tunnels"][0]["local_port"]
    ssh_server = new_conn["tunnels"][0]["tunnel_server"]
    ssh_server = "ssh.mysocket.io"
    ssh_user = str(new_conn["user_name"])

    print_sockets([new_conn])
    if protected:
        print_protected(username, password)

    time.sleep(2)
    ssh_tunnel(port, remote_bind_port, ssh_server, ssh_user, engine=engine)
    print("cleaning up...")
    ctx.invoke(mysocketctl.socket.delete, socket_id=new_conn["socket_id"])
