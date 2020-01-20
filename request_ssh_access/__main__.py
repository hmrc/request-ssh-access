#!/usr/bin/env python3

import argparse
import boto3
import getpass
import json
import logging
import os
import sys

from . import config
from . import vault

PRODUCTION_ENVS = ['production', 'externaltest']

logging.basicConfig(
    level=logging.WARN, format="%(asctime)s %(levelname)-5s %(message)s"
)


logger = logging.getLogger(__name__)


def main(args=None):
    if args is None:
        args = sys.argv[1:]
    args = parse_args(args)

    generate_signed_cert(args.environment, args.user_name, args.ttl, args.output_ssh_cert)


def generate_signed_cert(environment, username, ttl=60*60*4, output_ssh_cert=config.DEFAULT_CERT_PATH):
    if environment.lower().strip() not in PRODUCTION_ENVS:
        wrapped_token = invoke_grant_ssh_access(username, environment, ttl)
    else:
        print_lambda_command_to_copy(username, environment)

        wrapped_token = get_input(
            "Enter the Vault wrapped token you received back from the authorised user: "
        )
        wrapped_token = wrapped_token.strip(" '\"")

    prompt = (
        "Now we're ready to unwrap the signed certificate for you.\n"
        "Please enter the LDAP password for '{user}' in '{env}': ".format(
            user=username, env=environment
        )
    )

    ldap_password = getpass.getpass(prompt=prompt)
    unwrapped_cert = vault.unwrap(
        environment,
        vault.login(environment, username, ldap_password),
        wrapped_token,
    )

    write_cert_to_file(output_ssh_cert, unwrapped_cert)
    print(
        "\nyou are now authorised to log in using the following command: \n"
        'ssh "${{REMOTE_HOST}}"\n'
    )


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
        "--ttl",
        help="TTL for certificate in seconds",
        type=int,
        required=False,
        default=60*60*4  # 4 hours
    )

    parser.add_argument(
        "--output-ssh-cert",
        help="Path to write signed certificate (default: '{}')".format(
            config.DEFAULT_CERT_PATH
        ),
        default=config.DEFAULT_CERT_PATH,
        type=str,
    )

    args = parser.parse_args(argv)

    return args


def get_input(prompt=""):
    return input(prompt)


def print_lambda_command_to_copy(user_name, environment):
    function_arn = config.LAMBDA_ARN[environment]
    print(
        config.COMMAND_TEMPLATE.format(
            function_arn=function_arn, user_name=user_name, ttl=config.DEFAULT_TTL
        )
    )


def write_cert_to_file(output_ssh_cert, unwrapped_cert):
    if os.path.isfile(output_ssh_cert):
        if not yes_or_no(f"{output_ssh_cert} already exists. Do you want to overwrite it?"):
            exit(0)
    with open(output_ssh_cert, "w") as f:
        f.write(unwrapped_cert)
    print("signed certificate written to '{}'.".format(output_ssh_cert))


def invoke_grant_ssh_access(username, environment, ttl):

    boto3.setup_default_session(profile_name="webops-users")

    sts_connection = boto3.client('sts')
    account_id = sts_connection.get_caller_identity()["Account"]
    mfa_serial = f"arn:aws:iam::638924580364:mfa/{username}"

    # Prompt for MFA time-based one-time password (TOTP)
    mfa_token = getpass.getpass(prompt="Enter your MFA code: ")

    acct_b = sts_connection.assume_role(
        RoleArn=config.GRANT_ROLE_ARN[environment],
        RoleSessionName="GrantSSHAccess",
        SerialNumber=mfa_serial,
        TokenCode=mfa_token
    )

    ACCESS_KEY = acct_b['Credentials']['AccessKeyId']
    SECRET_KEY = acct_b['Credentials']['SecretAccessKey']
    SESSION_TOKEN = acct_b['Credentials']['SessionToken']

    # create service client using the assumed role credentials, e.g. S3
    client = boto3.client(
        'lambda',
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
        aws_session_token=SESSION_TOKEN,
    )

    response = client.invoke(
        FunctionName=config.FUNCTION_NAME,
        InvocationType='RequestResponse',
        Payload=json.dumps({
            "user_name": username,
            "ttl": ttl
        })
    )

    return json.loads(response['Payload'].read()).get('token')

def yes_or_no(question):
    reply = str(input(question + ' (Y/n): ')).lower().strip()
    if not reply or reply[0] == 'n':
        return False
    else:
        return True

if __name__ == "__main__":
    main()
