import os

COMMAND_TEMPLATE = """
(Note that this is for convenience only and you may modify these values to whatever you need)

Please email, slack, text, or pigeon-mail to an authorised person the following JSON:
```
{
    "user_name": "{user_name}",
    "ttl": {ttl}
}
```

Send them the following link for documentation:
https://github.com/hmrc/grant-ssh-access/blob/master/README.md#instructions-for-granting-ssh-access-to-an-engineer

Or if the person has AWS CLI setup, they can run the following

aws --profile=platform_owner lambda invoke --function-name {function_arn} --payload "{{\\"user_name\\": \\"{user_name}\\", \\"ttl\\": \\"{ttl}\\"}}" /tmp/grant_outfile && cat /tmp/grant_outfile

"""

DEFAULT_TTL = 60 * 60 * 8  # 8 hours
DEFAULT_PUBKEY_PATH = os.path.expanduser("~/.ssh/id_rsa.pub")
DEFAULT_CERT_PATH = os.path.expanduser("~/.ssh/id_rsa-cert.pub")

LAMBDA_ARN = {
    "integration": "arn:aws:lambda:eu-west-2:150648916438:function:grant-ssh-access",
    "development": "arn:aws:lambda:eu-west-2:618259438944:function:grant-ssh-access",
    "qa": "arn:aws:lambda:eu-west-2:248771275994:function:grant-ssh-access",
    "staging": "arn:aws:lambda:eu-west-2:186795391298:function:grant-ssh-access",
    "externaltest": "arn:aws:lambda:eu-west-2:970278273631:function:grant-ssh-access",
    "production": "arn:aws:lambda:eu-west-2:490818658393:function:grant-ssh-access",
}
