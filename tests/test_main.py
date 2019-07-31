import json
import re
from unittest.mock import Mock

import pytest
import responses

import request_ssh_access.__main__ as main


@pytest.fixture
def mocked_responses():
    with responses.RequestsMock() as rsps:
        yield rsps


def test_happy_path(tmp_path, monkeypatch, mocked_responses, capsys):
    ssh_public_key = str(tmp_path / "id_rsa.pub")
    output_ssh_cert = str(tmp_path / "id_rsa-cert.pub")
    args = (
        "--user-name",
        "user_name",
        "--environment",
        "integration",
        "--ssh-public-key",
        ssh_public_key,
        "--output-ssh-cert",
        output_ssh_cert,
    )

    with open(ssh_public_key, "w") as f:
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


def test_fail():
    assert False
