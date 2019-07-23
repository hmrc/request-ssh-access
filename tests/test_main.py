import json
import re
from unittest.mock import Mock

import attr
import pytest
import responses

import request_ssh_access.__main__ as main


@attr.s
class Args:
    user_name = attr.ib()
    environment = attr.ib()
    ssh_public_key = attr.ib()
    output_ssh_cert = attr.ib()


@pytest.fixture
def mocked_responses():
    with responses.RequestsMock() as rsps:
        yield rsps


def test_happy_path(tmp_path, monkeypatch, mocked_responses, capsys):

    args = Args(
        "user_name",
        "integration",
        str(tmp_path / "id_rsa.pub"),
        str(tmp_path / "id_rsa-cert.pub"),
    )

    with open(args.ssh_public_key, "w") as f:
        f.write("ssh-rsa AAA aa")

    fake_get_input = Mock(return_value="s.wrapped_token")
    monkeypatch.setattr(main, "get_input", fake_get_input)
    monkeypatch.setattr(main.getpass, "getpass", Mock(return_value="toor"))

    mocked_responses.add(
        mocked_responses.POST,
        url=re.compile(r".*auth/ldap/login.*"),
        body=json.dumps({"auth": {"client_token": "vault-token"}}),
    )

    mocked_responses.add(
        mocked_responses.POST,
        url=re.compile(r".*sys/wrapping/unwrap"),
        body=json.dumps({"data": {"signed_key": "signed_key"}}),
    )

    main.main(args)


def test_parse_args():
    main.parse_args(
        [
            "--user-name",
            "USER_NAME",
            "--environment",
            "integration",
            "--ssh-public-key",
            "SSH_PUBLIC_KEY",
            "--output-ssh-cert",
            "OUTPUT_SSH_CERT",
        ]
    )
