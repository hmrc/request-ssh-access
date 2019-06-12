import os

COMMAND_TEMPLATE = """
Here's the command to copy and paste:
`aws lambda do-it --user-name={user_name} --public-key="{public_key}" --ttl={ttl}`
"""

DEFAULT_TTL = 60 * 60 * 8  # 8 hours
DEFAULT_CERT_PATH = os.path.expanduser("~/.ssh/id_rsa-cert.pub")
TEMPORARY_TOKEN = "s.XZJOeSy8QJqyvF068obVbhMd"
