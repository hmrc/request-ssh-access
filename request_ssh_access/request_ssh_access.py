#!/usr/bin/env python3
import json

import boto3


def main():
    # boto3.setup_default_session(profile_name="webops-users")

    webops_users = boto3.session.Session(profile_name="webops-users")

    iam = webops_users.client("iam")
    user_name = iam.get_user()["User"]["UserName"]

    ssh_keys = iam.list_ssh_public_keys(UserName=user_name)

    ssh_keys = [k for k in ssh_keys["SSHPublicKeys"] if k["Status"] == "Active"]

    response = iam.get_ssh_public_key(
        UserName=user_name,
        SSHPublicKeyId=ssh_keys.pop()["SSHPublicKeyId"],
        Encoding="SSH",
    )

    print(json.dumps(response, indent=2, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
