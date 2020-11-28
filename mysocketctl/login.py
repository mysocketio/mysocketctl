import json
import click
import requests

from mysocketctl.utils import *


@click.group()
def login():  # pragma: no cover
    pass


def get_token(ctx, user_email, user_pass):
    params = {"email": user_email, "password": user_pass}
    token = requests.post(
        api_url + "login",
        data=json.dumps(params),
        headers={"accept": "application/json", "Content-Type": "application/json"},
    )
    if token.status_code == 401:
        ctx.fail("Login failed")
    if token.status_code != 200:
        ctx.fail(f"{token.status_code}: {token.text}")
    return token.json()


@login.command()
@click.option("--email", required=True, help="your email")
@click.password_option("--password", required=True, help="your pasword")
@click.pass_context
def login(ctx, email, password):
    """Login to mysocket and get a token"""
    token = get_token(ctx, email, password)["token"]
    with open(token_file, "w") as f:
        f.write(token)
    os.chmod(token_file, 0o600)
    print(f"Logged in! Token stored in {token_file}\n")
