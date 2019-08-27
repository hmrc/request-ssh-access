import os

COMMAND_TEMPLATE = """
(Note that this is for convenience only and you may modify these values to whatever you need)

Please email, slack, text, or pigeon-mail to an authorised person the following command:

aws --profile=platform_owner lambda invoke --function-name {function_arn} --payload "{{\\"user_name\\": \\"{user_name}\\", \\"ttl\\": \\"{ttl}\\"}}" /tmp/grant_outfile && cat /tmp/grant_outfile

"""

DEFAULT_TTL = 60 * 60 * 8  # 8 hours
DEFAULT_PUBKEY_PATH = os.path.expanduser("~/.ssh/id_rsa.pub")
DEFAULT_CERT_PATH = os.path.expanduser("~/.ssh/id_rsa-cert.pub")

LAMBDA_ARN = {
    "integration": "arn:aws:lambda:eu-west-2:150648916438:function:grant-ssh-access"
}
