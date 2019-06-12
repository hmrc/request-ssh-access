import getpass

import boto3

import config


class MFASession:
    def __init__(self, profile_name):
        self.profile_name = profile_name
        self.session = boto3.session.Session(profile_name=profile_name)
        self._user_name = None

    @property
    def user_name(self):
        if self._user_name is None:
            self._user_name = self.session.client("iam").get_user()["User"]["UserName"]
        return self._user_name

    def mfa_login(self):
        mfa = getpass.getpass(prompt="Enter AWS MFA code: ")
        session_token_response = self.session.client("sts").get_session_token(
            DurationSeconds=config.DEFAULT_TTL,
            SerialNumber="arn:aws:iam::638924580364:mfa/{}".format(self.user_name),
            TokenCode=mfa,
        )
        credentials = session_token_response["Credentials"]
        self.session = boto3.session.Session(
            aws_session_token=credentials["SessionToken"],
            aws_access_key_id=credentials["AccessKeyId"],
            aws_secret_access_key=credentials["SecretAccessKey"],
        )
