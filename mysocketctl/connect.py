import click

import mysocketctl.socket
from mysocketctl.utils import *
from validate_email import validate_email


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
    allowed_email_addresses_list,
    allowed_email_domain_list,
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
        "cloud_authentication_email_allowed_addressses": allowed_email_addresses_list,
        "cloud_authentication_email_allowed_domains": allowed_email_domain_list,
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
@click.option(
    "--engine", default="auto", type=click.Choice(("auto", "system", "paramiko"))
)
@click.pass_context
def connect(
    ctx,
    port,
    name,
    protected,
    username,
    password,
    type,
    engine,
    cloudauth,
    allowed_email_addresses,
    allowed_email_domains,
):
    """Quckly connect, Wrapper around sockets and tunnels"""

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
        allowed_email_addresses_list,
        allowed_email_domain_list,
    )
    remote_bind_port = new_conn["tunnels"][0]["local_port"]
    ssh_server = new_conn["tunnels"][0]["tunnel_server"]
    ssh_server = "ssh.mysocket.io"
    ssh_user = str(new_conn["user_name"])

    print_sockets([new_conn])
    if protected:
        print_protected(username, password)
    if cloudauth:
        print_cloudauth(allowed_email_addresses_list, allowed_email_domain_list)

    time.sleep(2)
    ssh_tunnel(port, remote_bind_port, ssh_server, ssh_user, engine=engine)
    print("cleaning up...")
    ctx.invoke(mysocketctl.socket.delete, socket_id=new_conn["socket_id"])
