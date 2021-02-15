import os


COMMAND_TEMPLATE = """
(Note that this is for convenience only and you may modify these values to whatever you need)

Please email, slack, text, or pigeon-mail to an authorised person the following JSON:
```
{{
    "user_name": "{user_name}",
    "ttl": {ttl}
}}
```

Send them the following link for documentation:
https://github.com/hmrc/grant-ssh-access/blob/master/README.md#instructions-for-granting-ssh-access-to-an-engineer

Or if the person has AWS CLI setup, they can run the following

aws --profile=platform_owner lambda invoke --function-name {function_arn} --payload "{{\\"user_name\\": \\"{user_name}\\", \\"ttl\\": \\"{ttl}\\"}}" /tmp/grant_outfile && cat /tmp/grant_outfile
"""  # noqa: E501

DEFAULT_TTL = 3600  # 1 hour
MAX_TTL = 43200  # 12 hours

DEFAULT_PUBKEY_PATH = os.path.expanduser("~/.ssh/id_rsa.pub")
DEFAULT_CERT_PATH = os.path.expanduser("~/.ssh/id_rsa-cert.pub")
FUNCTION_NAME = "grant-ssh-access"

ENVIRONMENT_ACCOUNT_IDS = {
    "integration": "150648916438",
    "development": "618259438944",
    "qa": "248771275994",
    "staging": "186795391298",
    "externaltest": "970278273631",
    "production": "490818658393",
}

LAMBDA_ARN = {
    environment_name: f"arn:aws:lambda:eu-west-2:{account_id}:function:grant-ssh-access"
    for environment_name, account_id in ENVIRONMENT_ACCOUNT_IDS.items()
}

GRANT_ROLE_ARN = {
    environment_name: f"arn:aws:iam::{account_id}:role/RoleGrantSSHAccess"
    for environment_name, account_id in ENVIRONMENT_ACCOUNT_IDS.items()
}
