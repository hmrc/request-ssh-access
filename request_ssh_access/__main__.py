#!/usr/bin/env python3

import argparse
import boto3
import getpass
import json
import logging
import os
import sys
import re

from . import config
from . import vault

PRODUCTION_ENVS = ["production", "externaltest"]

logging.basicConfig(
    level=logging.WARN, format="%(asctime)s %(levelname)-5s %(message)s"
)


logger = logging.getLogger(__name__)


class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKGREEN = "\033[92m"
    PROMPT = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def main(args=None):
    try:
        if args is None:
            args = sys.argv[1:]
        args = parse_args(args)

        generate_signed_cert(
            args.environment,
            args.user_name,
            args.ttl,
            args.input_ssh_cert,
            get_output_cert_path(args),
        )
    except Exception as e:
        print(e)
        exit(1)


def generate_signed_cert(
    environment,
    username,
    ttl=60 * 60 * 4,
    input_ssh_cert=config.DEFAULT_PUBKEY_PATH,
    output_ssh_cert=config.DEFAULT_CERT_PATH,
):
    if ttl > config.MAX_TTL:
        max_ttl_message = (
            bcolors.FAIL
            + "FAILED: The TTL requested is greater than MAX_TTL which is set"
            + f" {config.MAX_TTL}\n"
            + bcolors.ENDC
        )
        raise Exception(max_ttl_message)

    environment = environment.lower().strip()
    if environment not in PRODUCTION_ENVS:
        wrapped_token = invoke_grant_ssh_access(username, environment, ttl)
    else:
        print_lambda_command_to_copy(username, environment, ttl)

        wrapped_token = get_input(
            bcolors.PROMPT
            + "Enter the Vault wrapped token you received back from the authorised"
            + " user: "
            + bcolors.ENDC
        )
        wrapped_token = wrapped_token.strip(" '\"")

    prompt = (
        "Now we're ready to unwrap the signed certificate for you.\n"
        + bcolors.PROMPT
        + f"Please enter the LDAP password for {username}: "
        + bcolors.ENDC
    )

    ldap_password = getpass.getpass(prompt=prompt)
    unwrapped_cert = vault.unwrap(
        environment, vault.login(environment, username, ldap_password), wrapped_token
    )

    write_cert_to_file(output_ssh_cert, unwrapped_cert)
    print(
        "\nyou are now authorised to log in using the following command: \n",
        'ssh -o "IdentityAgent none" -i {} -i {} "${{REMOTE_HOST}}"\n'.format(
            input_ssh_cert, output_ssh_cert
        ),
        "\nor add the following to the appropriate Hosts section in your"
        + " ~/.ssh/confg\n",
        "\n\tUser {}".format(username),
        "\n\tIdentitiesOnly yes",
        "\n\tIdentityFile {}".format(input_ssh_cert),
        "\n\nand then log in with the following command: \n",
        'ssh "${{REMOTE_HOST}}"\n',
    )


def get_input(prompt=""):
    """ this is here so input() could be mocked """
    return input(prompt)


def get_output_cert_path(args: argparse.Namespace):
    if hasattr(args, "output_ssh_cert") and args.output_ssh_cert is not None:
        return args.output_ssh_cert
    else:
        if args.input_ssh_cert.endswith(".pub"):
            return re.sub(r"^(.*)\.pub", r"\1-cert.pub", args.input_ssh_cert)
        else:
            return "{}-cert.pub".format(args.input_ssh_cert)


def print_lambda_command_to_copy(user_name, environment, ttl):
    function_arn = config.LAMBDA_ARN[environment]
    print(
        config.COMMAND_TEMPLATE.format(
            function_arn=function_arn, user_name=user_name, ttl=ttl
        )
    )


def write_cert_to_file(output_ssh_cert, unwrapped_cert):
    if os.path.isfile(output_ssh_cert):
        if not yes_or_no(
            f"{output_ssh_cert} already exists. Do you want to overwrite it?"
        ):
            exit(0)
    with open(output_ssh_cert, "w") as f:
        f.write(unwrapped_cert)
    print("signed certificate written to '{}'.".format(output_ssh_cert))


def invoke_grant_ssh_access(username, environment, ttl):

    sts_connection = boto3.client("sts")
    account_id = sts_connection.get_caller_identity()["Account"]
    mfa_serial = f"arn:aws:iam::{account_id}:mfa/{username}"

    # Prompt for MFA time-based one-time password (TOTP)
    mfa_token = getpass.getpass(
        prompt="Enter your MFA code (must be different to your previous MFA token): "
    )

    acct_b = sts_connection.assume_role(
        RoleArn=config.GRANT_ROLE_ARN[environment],
        RoleSessionName="GrantSSHAccess",
        SerialNumber=mfa_serial,
        TokenCode=mfa_token,
    )

    ACCESS_KEY = acct_b["Credentials"]["AccessKeyId"]
    SECRET_KEY = acct_b["Credentials"]["SecretAccessKey"]
    SESSION_TOKEN = acct_b["Credentials"]["SessionToken"]

    # create service client using the assumed role credentials, e.g. S3
    client = boto3.client(
        "lambda",
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
        aws_session_token=SESSION_TOKEN,
    )

    response = client.invoke(
        FunctionName=config.FUNCTION_NAME,
        InvocationType="RequestResponse",
        Payload=json.dumps({"user_name": username, "ttl": ttl}),
    )

    return json.loads(response["Payload"].read()).get("token")


def yes_or_no(question):
    reply = str(input(question + " (Y/n): ")).lower().strip()
    if not reply or reply == "y":
        return True
    else:
        return False


def parse_args(argv):
    parser = argparse.ArgumentParser(
        description="Helper utility to create Vault-signed SSH certificates"
    )
    parser.add_argument(
        "--user-name", help="AWS/LDAP user name", type=str, required=True
    )
    parser.add_argument(
        "--environment",
        help="Environment to run in",
        type=str,
        required=True,
        choices=[
            "integration",
            "externaltest",
            "production",
            "staging",
            "qa",
            "development",
        ],
    )

    parser.add_argument(
        "--input-ssh-cert",
        help="Certificate to be signed (default: '{}')".format(
            config.DEFAULT_PUBKEY_PATH
        ),
        default=config.DEFAULT_PUBKEY_PATH,
        type=str,
        required=False,
    )

    parser.add_argument(
        "--output-ssh-cert", help="Path to write signed certificate", type=str
    )

    parser.add_argument(
        "--ttl",
        help="TTL in seconds for the Vault generated ssh certificate lease which"
        + "defaults to 1 hour",
        type=int,
        required=False,
        default=config.DEFAULT_TTL,
    )

    args = parser.parse_args(argv)
    return args


if __name__ == "__main__":
    main()
