#!/usr/bin/env python3
import click


@click.group()
def cli():
    pass


# Import sub commands from commands
from .account import account
from .login import login
from .connect import connect
from .socket import socket
from .tunnel import tunnel

cli.add_command(account, "account")
cli.add_command(login, "login")
cli.add_command(connect, "connect")
cli.add_command(socket, "socket")
cli.add_command(tunnel, "tunnel")


if __name__ == "__main__":
    cli()
