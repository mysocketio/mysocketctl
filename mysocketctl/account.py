import click
from mysocketctl.utils import *


@click.group()
def account():
    """Create a new account or see account information."""
    pass


def show_account(authorization_header, user_id):
    api_answer = requests.get(f"{api_url}user/{user_id}", headers=authorization_header)
    validate_response(api_answer)
    return api_answer.json()


def create_account(name, email, password, sshkey):
    params = {
        "name": name,
        "email": email,
        "password": password,
        "sshkey": sshkey,
    }

    api_answer = requests.post(
        api_url + "user",
        data=json.dumps(params),
        headers={"accept": "application/json", "Content-Type": "application/json"},
    )
    validate_response(api_answer)
    return api_answer.json()


@account.command()
@click.option("--name", required=True, help="your name")
@click.option("--email", required=True, help="your email")
@click.password_option("--password", required=True, help="your pasword")
@click.option(
    "--sshkey",
    required=True,
    help='your public sshkey as a string, or use:                   --sshkey "$(cat ~/.ssh/id_rsa.pub)"',
)
def create(name, email, password, sshkey):
    """Create your new mysocket.io account"""
    try:
        if os.path.exists(sshkey):
            with open(sshkey, "r") as fp:
                sshkey = fp.read()
    except PermissionError:
        print(
            f"Unable to read the file {sshkey}, please check file permissions and try again."
        )
        return
    register_result = create_account(name, email, password, sshkey)
    print(
        "Congratulation! your account has been created. A confirmation email has been sent to "
        + email
    )
    print(
        "Please complete the account registration by following the confirmation link in your email."
    )
    print(f"After that login with login --email '{email}' --password '*****'")


@account.command()
def show():
    """Show your mysocket.io account information"""
    authorization_header = get_auth_header()
    user_details = show_account(authorization_header, get_user_id())

    table = PrettyTable()
    # table.border = True
    # table.hrules=True
    table.header = False
    table.add_row(["Name", str(user_details["name"])])
    table.add_row(["Email", str(user_details["email"])])
    table.add_row(["user id", str(user_details["user_id"])])
    table.add_row(["ssh username", str(user_details["user_name"])])
    table.add_row(["ssh key", str(user_details["sshkey"])])
    table.align = "l"
    print(table)


# @click.option("--sshkey", required=True, help='your public sshkey as a string, or use:                   --sshkey "$(cat ~/.ssh/id_rsa.pub)"')
# @account.command()
# def update_sshkey(sshkey):
#    print("not implemented yet")
