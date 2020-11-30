import click

from mysocketctl.utils import *


@click.group()
def tunnel():
    """Manage your tunnels"""
    pass


def get_ssh_username(authorization_header):
    user_id = get_user_id()
    api_answer = requests.get(f"{api_url}user/{user_id}", headers=authorization_header)
    validate_response(api_answer)
    data = api_answer.json()
    return data["user_name"]


def get_tunnels(authorization_header, socket_id):
    api_answer = requests.get(
        f"{api_url}socket/{socket_id}/tunnel", headers=authorization_header
    )
    validate_response(api_answer)
    return api_answer.json()


def get_tunnel_info(authorization_header, socket_id, tunnel_id):
    api_answer = requests.get(
        f"{api_url}socket/{socket_id}/tunnel/{tunnel_id}",
        headers=authorization_header,
    )
    validate_response(api_answer)
    return api_answer.json()


def new_tunnel(authorization_header, socket_id):

    params = {}
    api_answer = requests.post(
        f"{api_url}socket/{socket_id}/tunnel",
        data=json.dumps(params),
        headers=authorization_header,
    )
    validate_response(api_answer)
    return api_answer.json()


def delete_tunnel(authorization_header, socket_id, tunnel_id):
    api_answer = requests.delete(
        f"{api_url}socket/{socket_id}/tunnel/{tunnel_id}",
        headers=authorization_header,
    )
    validate_response(api_answer)
    return api_answer


def print_tunnels(tunnels, socket_id):
    table = PrettyTable(
        field_names=["socket_id", "tunnel_id", "tunnel_server", "relay_port"]
    )
    table.align = "l"
    table.border = True

    for tunnel in tunnels:
        row = [
            socket_id,
            tunnel["tunnel_id"],
            tunnel["tunnel_server"],
            tunnel["local_port"],
        ]
        table.add_row(row)
    print(table)


@tunnel.command()
@click.option("--socket_id", required=True, type=str)
def ls(socket_id):
    authorization_header = get_auth_header()
    tunnels = get_tunnels(authorization_header, socket_id)
    print_tunnels(tunnels, socket_id)


@tunnel.command()
@click.option("--socket_id", required=True, type=str)
def create(socket_id):
    authorization_header = get_auth_header()
    tunnel = new_tunnel(authorization_header, socket_id)
    print_tunnels([tunnel], socket_id)


@tunnel.command()
@click.option("--socket_id", required=True, type=str)
@click.option("--tunnel_id", required=True, type=str)
def delete(socket_id, tunnel_id):
    authorization_header = get_auth_header()
    delete_tunnel(authorization_header, socket_id, tunnel_id)
    print(f"Tunnel {tunnel_id} deleted")


@tunnel.command()
@click.option("--socket_id", required=True, type=str)
@click.option("--tunnel_id", required=True, type=str)
@click.option("--port", required=True, type=str)
@click.option("--host", hidden=True, type=str, default="localhost")
@click.option(
    "--engine", default="auto", type=click.Choice(("auto", "system", "paramiko"))
)
def connect(socket_id, tunnel_id, port, engine, host):
    authorization_header = get_auth_header()
    tunnel = get_tunnel_info(authorization_header, socket_id, tunnel_id)
    ssh_username = get_ssh_username(authorization_header)
    ssh_server = "ssh.mysocket.io"

    ssh_tunnel(port, tunnel["local_port"], ssh_server, ssh_username, host, engine)
