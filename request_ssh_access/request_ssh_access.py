#!/usr/bin/env python3

"""
TODO:
- SQS/S3 integration - read the token from the user's queue
- Check for wrapped tokens on the user's queue at startup.
- Error handling for Everything
"""

import argparse
import getpass
import logging
import os

import boto3
import requests

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(levelname)-5s %(message)s"
)
logger = logging.getLogger(__name__)

webops_users = boto3.session.Session(profile_name="webops-users")
iam = webops_users.client("iam")

COMMAND_TEMPLATE = """
Here's the command to copy and paste:
aws lambda do-it --user-name={user_name} --public-key="{public_key}" --ttl={ttl}
"""

DEFAULT_TTL = 60 * 60 * 8  # 8 hours
DEFAULT_CERT_PATH = os.path.expanduser("~/.ssh/id_rsa-cert.pub")


def main():
    parser = argparse.ArgumentParser(
        description="Utility that will help with generating signed ssh certificates to use to login onto EC2"
    )
    parser.add_argument(
        "--environment",
        help="Environment to run against",
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
        "--output-ssh-cert",
        help="Path to write signed certificate (default: '{}')".format(
            DEFAULT_CERT_PATH
        ),
        default=DEFAULT_CERT_PATH,
        type=str,
    )

    args = parser.parse_args()

    print_lambda_command_to_copy()

    prompt = "LDAP password for '{env}': ".format(env=args.environment)
    ldap_password = getpass.getpass(prompt=prompt)

    unwrapped_cert = vault_unwrap(
        vault_login(get_aws_user_name(), ldap_password), get_wrapped_secret_from_sqs()
    )

    write_cert_to_file(args.output_ssh_cert, unwrapped_cert)


def get_aws_user_name():
    return iam.get_user()["User"]["UserName"]


def print_lambda_command_to_copy():
    iam = webops_users.client("iam")
    user_name = get_aws_user_name()
    ssh_keys = iam.list_ssh_public_keys(UserName=user_name)
    ssh_keys = [k for k in ssh_keys["SSHPublicKeys"] if k["Status"] == "Active"]
    ssh_key_id = ssh_keys.pop()["SSHPublicKeyId"]

    try:
        response = iam.get_ssh_public_key(
            UserName=user_name, SSHPublicKeyId=ssh_key_id, Encoding="SSH"
        )
        public_key = response.get["SSHPublicKey"]["SSHPublicKeyBody"]
    except:
        logger.warn("ugh")
        public_key = "ssh-rsa XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
    logger.info(public_key)
    print(
        COMMAND_TEMPLATE.format(
            user_name=user_name, public_key=public_key, ttl=DEFAULT_TTL
        )
    )


def vault_login(ldap_user_name, ldap_password):
    url = "https://vault.tools.development.tax.service.gov.uk/v1/auth/ldap/login/{ldap_user_name}".format(
        ldap_user_name=ldap_user_name
    )
    logger.info("trying to log in with user={}".format(ldap_user_name))
    payload = {"password": ldap_password}
    response = requests.post(url, json=payload)
    logger.debug("login response {} {}".format(response.status_code, response.text))

    return response.json()["auth"]["client_token"]


def vault_unwrap(vault_token, wrapped_token):
    url = "https://vault.tools.development.tax.service.gov.uk/v1/sys/wrapping/unwrap"

    payload = {"token": wrapped_token}
    headers = {"X-Vault-Token": vault_token}

    try:
        response = requests.post(url, json=payload, headers=headers)
        logger.debug("{} {}".format(response.status_code, response.text))

        return response.json()["data"]["signed_key"]
    except KeyError:
        logger.warn(
            "error while unwrapping the certificate, perhaps the token is expired?"
        )


def get_wrapped_secret_from_sqs():
    return "s.CMIPnk3wZS8kdWeKYBlYR5fM"


def write_cert_to_file(output_ssh_cert, unwrapped_cert):
    with open(output_ssh_cert, "w") as f:
        f.write(unwrapped_cert)


if __name__ == "__main__":
    main()
