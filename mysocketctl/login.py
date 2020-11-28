import click

from mysocketctl.utils import *


@click.group()
def login():
    pass


def get_token(user_email, user_pass):
    params = {"email": user_email, "password": user_pass}
    token = requests.post(
        api_url + "login",
        data=json.dumps(params),
        headers={"accept": "application/json", "Content-Type": "application/json"},
    )
    if token.status_code == 401:
        print("Login failed")
        sys.exit(1)
    if token.status_code != 200:
        print(token.status_code, token.text)
        sys.exit(1)
    return token.json()


@login.command()
@click.option("--email", required=True, help="your email")
@click.password_option("--password", required=True, help="your pasword")
def login(email, password):
    """Login to mysocket and get a token"""
    token = get_token(email, password)["token"]
    f = open(token_file, "w")
    f.write(token)
    f.close()
    print(f"Logged in! Token stored in {token_file}\n")
