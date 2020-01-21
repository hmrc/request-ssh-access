#!/usr/bin/env python3

import argparse
import getpass
import logging
import sys
import re

from . import config
from . import vault

logging.basicConfig(
    level=logging.WARN, format="%(asctime)s %(levelname)-5s %(message)s"
)


logger = logging.getLogger(__name__)


def main(args=None):
    class bcolors:
        HEADER = "\033[95m"
        OKBLUE = "\033[94m"
        OKGREEN = "\033[92m"
        WARNING = "\033[93m"
        FAIL = "\033[91m"
        ENDC = "\033[0m"
        BOLD = "\033[1m"
        UNDERLINE = "\033[4m"

    if args is None:
        args = sys.argv[1:]
    args = parse_args(args)

    if args.ttl > config.MAX_TTL:
        sys.tracebacklimit = -1
        max_ttl_message = (
            bcolors.FAIL
            + f"FAILED: The TTL requested is greater than MAX_TTL which is set {config.MAX_TTL}\n"
            + bcolors.ENDC
        )
        raise Exception(max_ttl_message)

    print_lambda_command_to_copy(args.user_name, args.environment, ttl=args.ttl)

    wrapped_token = get_input(
        bcolors.OKGREEN
        + "Enter the Vault wrapped token you received back from the authorised user: "
        + bcolors.ENDC
    )
    wrapped_token = wrapped_token.strip(" '\"")

    prompt = (
        "Now we're ready to unwrap the signed certificate for you.\n"
        + bcolors.OKGREEN
        + f"Please enter the LDAP password for {args.user_name} in '{args.environment}': "
        + bcolors.ENDC
    )

    ldap_password = getpass.getpass(prompt=prompt)
    unwrapped_cert = vault.unwrap(
        args.environment,
        vault.login(args.environment, args.user_name, ldap_password),
        wrapped_token,
    )

    write_cert_to_file(get_output_cert_path(args), unwrapped_cert)
    print(
        "\nyou are now authorised to log in using the following command: \n",
        'ssh -o "IdentityAgent none" -i {} -i {} "${{REMOTE_HOST}}"\n'.format(
            args.input_ssh_cert, get_output_cert_path(args)
        ),
        "\nor add the following to the appropriate Hosts section in your ~/.ssh/confg\n",
        "\n\tUser {}".format(args.user_name),
        "\n\tIdentitiesOnly yes",
        "\n\tIdentityFile {}".format(args.input_ssh_cert),
        "\n\nand then log in with the following command: \n",
        'ssh "${{REMOTE_HOST}}"\n',
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
        "--input-ssh-cert",
        help="Certificate to be signed (default: '{}')".format(
            config.DEFAULT_PUBKEY_PATH
        ),
        default=config.DEFAULT_PUBKEY_PATH,
        type=str,
        required=True,
    )

    parser.add_argument(
        "--output-ssh-cert", help="Path to write signed certificate", type=str,
    )

    parser.add_argument(
        "--ttl",
        help="TTL in seconds for the Vault generated ssh certificate lease which defaults to 1 hour",
        type=int,
        required=False,
        default=config.DEFAULT_TTL,
    )

    args = parser.parse_args(argv)
    return args


def get_input(prompt=""):
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
    with open(output_ssh_cert, "w") as f:
        f.write(unwrapped_cert)
    print("signed certificate written to '{}'.".format(output_ssh_cert))


if __name__ == "__main__":
    main()
