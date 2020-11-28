#!/usr/bin/env python3
import click

# Import sub commands from commands
from mysocketctl.account import account
from mysocketctl.login import login
from mysocketctl.connect import connect
from mysocketctl.socket import socket
from mysocketctl.tunnel import tunnel


@click.group()
def cli():
    pass


cli.add_command(account, "account")
cli.add_command(login, "login")
cli.add_command(connect, "connect")
cli.add_command(socket, "socket")
cli.add_command(tunnel, "tunnel")


if __name__ == "__main__":
    cli()
