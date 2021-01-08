import click

from mysocketctl.utils import *
from validate_email import validate_email


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
    cloudauth,
    allowed_email_addresses_list,
    allowed_email_domain_list,
):

    if not cloudauth:
        cloudauth = False
    else:
        cloudauth = True

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
        "cloud_authentication_enabled": cloudauth,
        "cloud_authentication_email_allowed_addressses": allowed_email_addresses_list,
        "cloud_authentication_email_allowed_domains": allowed_email_domain_list,
    }
    api_answer = requests.post(
        api_url + "socket", data=json.dumps(params), headers=authorization_header
    )
    validate_response(api_answer)
    return api_answer.json()


def delete_socket(authorization_header, socket_id):
    api_answer = requests.delete(
        f"{api_url}socket/{socket_id}", headers=authorization_header
    )
    validate_response(api_answer)
    return api_answer


@socket.command()
def ls():
    authorization_header = get_auth_header()
    sockets = get_sockets(authorization_header)
    print_sockets(sockets)


@socket.command()
@click.option("--name", required=True, type=str)
@click.option("--protected/--not-protected", default=False)
@click.option("--username", required=False, type=str, default="")
@click.option("--password", required=False, type=str, default="")
@click.option(
    "--cloudauth/--no-cloudauth", default=False, help="Enable oauth/oidc authentication"
)
@click.option(
    "--allowed_email_addresses",
    required=False,
    type=str,
    default="",
    help="comma seperated list of allowed Email addresses when using cloudauth",
)
@click.option(
    "--allowed_email_domains",
    required=False,
    type=str,
    default="",
    help="comma seperated list of allowed Email domain (i.e. 'example.com', when using cloudauth",
)
@click.option(
    "--type",
    required=False,
    type=click.Choice(["http", "https", "tcp", "tls"], case_sensitive=False),
    default="http",
    help="Socket type, http, https, tcp, tls",
)
def create(
    name,
    protected,
    username,
    password,
    type,
    cloudauth,
    allowed_email_addresses,
    allowed_email_domains,
):

    if cloudauth:
        cloudauth = True

        allowed_email_addresses_list = []
        if allowed_email_addresses:
            for email in allowed_email_addresses.split(","):
                if validate_email(email.strip()):
                    allowed_email_addresses_list.append(email.strip())
                else:
                    print("Warning: ignoring invalid email " + email.strip())

        allowed_email_domain_list = []
        if allowed_email_domains:
            for domain in allowed_email_domains.split(","):
                allowed_email_domain_list.append(domain.strip())

        # check if both email and domain list are empty and warn
        if not allowed_email_domain_list and not allowed_email_addresses_list:
            print(
                "Error: no allowed email addresses or domains provided. You will be unabled to get to your socket"
            )
            sys.exit(1)

    else:
        cloudauth = False
        allowed_email_domain_list = []
        allowed_email_addresses_list = []

    if protected:
        if not username:
            print("--username required when using --protected")
            sys.exit(1)
        if not password:
            print("--password required when using --protected")
            sys.exit(1)

    authorization_header = get_auth_header()
    socket = new_socket(
        authorization_header,
        name,
        protected,
        str(username),
        str(password),
        str(type),
        cloudauth,
        allowed_email_addresses_list,
        allowed_email_domain_list,
    )

    print_sockets([socket])
    if protected:
        print_protected(username, password)
    if cloudauth:
        print_cloudauth(allowed_email_addresses_list, allowed_email_domain_list)


@socket.command()
@click.option("--socket_id", required=True, type=str)
def delete(socket_id):
    authorization_header = get_auth_header()
    delete_socket(authorization_header, socket_id)
    print(f"Socket {socket_id} deleted")
