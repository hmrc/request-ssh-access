import os

COMMAND_TEMPLATE = """
Email, slack or text or pigeon-mail to an authorised person:
`aws lambda do-it --user-name={user_name} --public-key="{public_key}" --ttl={ttl}`
"""

DEFAULT_TTL = 60 * 60 * 8  # 8 hours
DEFAULT_CERT_PATH = os.path.expanduser("~/.ssh/id_rsa-cert.pub")
TEMPORARY_TOKEN = "s.mpFPfSSRNnCj2VVUbSfOhTj3"
DEFAULT_PROFILE_NAME = "webops-users"
