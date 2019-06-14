#!/usr/bin/env python3

"""
TODO:
- SQS/S3/Lambda integration - read the token from the user's queue
- Check for wrapped tokens on the user's queue at startup.
- Error handling for Everything
- setup.py
- account IDs
"""

import argparse
import getpass
import json
import logging
import time

from mfa_session import MFASession
import config
import vault

logging.basicConfig(
    level=logging.WARN, format="%(asctime)s %(levelname)-5s %(message)s"
)

logging.getLogger("boto").setLevel(logging.WARN)

logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description="Helper utility to create Vault-signed SSH certificates"
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
        "--output-ssh-cert",
        help="Path to write signed certificate (default: '{}')".format(
            config.DEFAULT_CERT_PATH
        ),
        default=config.DEFAULT_CERT_PATH,
        type=str,
    )

    args = parser.parse_args()

    session = MFASession(profile_name=config.DEFAULT_PROFILE_NAME)
    session.mfa_login()

    public_key = get_public_key(session)

    print_lambda_command_to_copy(public_key, session.user_name)

    input("Press Enter to continue...")

    wrapped_token = get_wrapped_secret_from_sqs(session)

    prompt = "LDAP password for '{user}' in '{env}': ".format(
        user=session.user_name, env=args.environment
    )

    ldap_password = getpass.getpass(prompt=prompt)
    try:
        unwrapped_cert = vault.unwrap(
            args.environment,
            vault.login(args.environment, session.user_name, ldap_password),
            wrapped_token,
        )
    except:
        print("oops, unwrapping failed, exiting")
        raise

    write_cert_to_file(args.output_ssh_cert, unwrapped_cert)
    print("you are now authorised to log in.")


def get_public_key(session):
    ssh_keys = session.session.client("iam").list_ssh_public_keys(
        UserName=session.user_name
    )
    ssh_keys = [k for k in ssh_keys["SSHPublicKeys"] if k["Status"] == "Active"]
    ssh_key_id = ssh_keys.pop()["SSHPublicKeyId"]

    response = session.session.client("iam").get_ssh_public_key(
        UserName=session.user_name, SSHPublicKeyId=ssh_key_id, Encoding="SSH"
    )

    return response["SSHPublicKey"]["SSHPublicKeyBody"]


def print_lambda_command_to_copy(public_key, user_name):
    print(
        config.COMMAND_TEMPLATE.format(
            user_name=user_name, public_key=public_key, ttl=config.DEFAULT_TTL
        )
    )


def write_cert_to_file(output_ssh_cert, unwrapped_cert):
    with open(output_ssh_cert, "w") as f:
        f.write(unwrapped_cert)
    print("signed certificate written to '{}'.".format(output_ssh_cert))


def get_wrapped_secret_from_sqs(session):
    credentials = session.assume_role()
    sqs = session.session.client(
        "sqs",
        aws_access_key_id=credentials["AccessKeyId"],
        aws_secret_access_key=credentials["SecretAccessKey"],
        aws_session_token=credentials["SessionToken"],
    )

    queue_url_response = sqs.get_queue_url(
        QueueName="adam-test-13-june-2019", QueueOwnerAWSAccountId="132732819912"
    )
    queue_url = queue_url_response["QueueUrl"]

    message_response = get_message_from_queue(queue_url, sqs)
    return json.loads(message_response)['token']



def get_message_from_queue(queue_url, sqs):
    while True:
        print("waiting for message...")
        response = sqs.receive_message(
            QueueUrl=queue_url
        )
        if response.get('Messages', []):
            return response['Messages'].pop()['Body']

        time.sleep(10)


if __name__ == "__main__":
    main()
