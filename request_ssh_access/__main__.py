#!/usr/bin/env python3

"""
- TODO: Add ARNs for the lambdas in non-integration environments
- TODO: Error Handling for Everything
- TODO: ci pipeline
"""

import argparse
import getpass
import logging
import sys

from . import config
from . import vault

logging.basicConfig(
    level=logging.WARN, format="%(asctime)s %(levelname)-5s %(message)s"
)


logger = logging.getLogger(__name__)


def main(args):
    public_key = get_public_key(public_key_path=args.ssh_public_key)

    print_lambda_command_to_copy(public_key, args.user_name, args.environment)

    wrapped_token = get_input(
        "Enter the Vault wrapped token you received back from the authorised user: "
    )
    wrapped_token = wrapped_token.strip(" '\"")

    prompt = (
        "Now we're ready to unwrap the signed certificate for you.\n"
        "Please enter the LDAP password for '{user}' in '{env}': ".format(
            user=args.user_name, env=args.environment
        )
    )

    ldap_password = getpass.getpass(prompt=prompt)
    unwrapped_cert = vault.unwrap(
        args.environment,
        vault.login(args.environment, args.user_name, ldap_password),
        wrapped_token,
    )

    write_cert_to_file(args.output_ssh_cert, unwrapped_cert)
    ssh_private_key = args.ssh_public_key.replace(".pub", "")
    print(
        "\nyou are now authorised to log in using the following command: \n"
        'ssh -i {} -i {} "${{REMOTE_HOST}}"\n'.format(
            args.output_ssh_cert, ssh_private_key
        )
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
            # "externaltest",
            # "production",
            # "staging",
            # "qa",
            # "development",
        ],
    )
    parser.add_argument(
        "--ssh-public-key",
        help="Path to read ssh public key from (default: '{}')".format(
            config.DEFAULT_PUBKEY_PATH
        ),
        default=config.DEFAULT_PUBKEY_PATH,
        type=str,
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


def get_public_key(public_key_path):
    with open(public_key_path, "r") as f:
        # Clean up public key here:
        # "ssh-rsa AAB...3odo3Xsjd user@host\n" -> "ssh-rsa AAB...3odo3Xsjd"
        return " ".join(f.readline().rstrip().split(" ")[:2])


def print_lambda_command_to_copy(public_key, user_name, environment):
    function_arn = config.LAMBDA_ARN[environment]
    print(
        config.COMMAND_TEMPLATE.format(
            function_arn=function_arn,
            user_name=user_name,
            public_key=public_key,
            ttl=config.DEFAULT_TTL,
        )
    )


def write_cert_to_file(output_ssh_cert, unwrapped_cert):
    with open(output_ssh_cert, "w") as f:
        f.write(unwrapped_cert)
    print("signed certificate written to '{}'.".format(output_ssh_cert))


if __name__ == "__main__":
    main(parse_args(sys.argv[1:]))
