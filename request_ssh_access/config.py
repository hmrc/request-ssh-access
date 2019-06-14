import os

COMMAND_TEMPLATE = """
(Note that this is for convenience only and you may modify these values to whatever you need)

Please email, slack, text, or pigeon-mail to an authorised person the following command: 

`aws lambda do-it --user-name={user_name} --public-key="{public_key}" --ttl={ttl}`

"""

DEFAULT_TTL = 60 * 60 * 8  # 8 hours
DEFAULT_PUBKEY_PATH = os.path.expanduser("~/.ssh/id_rsa.pub")
DEFAULT_CERT_PATH = os.path.expanduser("~/.ssh/id_rsa-cert.pub")
TEMPORARY_TOKEN = "s.mpFPfSSRNnCj2VVUbSfOhTj3"
DEFAULT_PROFILE_NAME = "webops-users"
