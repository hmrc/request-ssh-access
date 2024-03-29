import json
import re
import argparse
from unittest.mock import Mock, patch

import pytest
import responses

import request_ssh_access.__main__ as main


@pytest.fixture
def mocked_responses():
    with responses.RequestsMock() as rsps:
        yield rsps


@patch("request_ssh_access.__main__.boto3.client", autospec=True)
def test_production_happy_path(
    mocked_boto3_client, tmp_path, monkeypatch, mocked_responses, capsys
):
    output_ssh_cert = str(tmp_path / "id_rsa-cert.pub")
    input_ssh_cert = str(tmp_path / "id_rsa.pub")
    args = (
        "--user-name",
        "myUserName",
        "--environment",
        "production",
        "--input-ssh-cert",
        input_ssh_cert,
        "--output-ssh-cert",
        output_ssh_cert,
    )

    fake_get_input = Mock(return_value="s.wrapped_token")
    monkeypatch.setattr(main, "get_input", fake_get_input)
    monkeypatch.setattr(main.getpass, "getpass", Mock(return_value="000000"))
    monkeypatch.setattr(main.boto3, "setup_default_session", Mock())

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

    mocked_payload = Mock()
    mocked_payload.read.return_value = '{"token": "s.atimakkok"}'
    mocked_boto3_client.return_value.invoke.return_value = {"Payload": mocked_payload}

    main.main(args)


@patch("request_ssh_access.__main__.boto3.client", autospec=True)
def test_happy_path(
    mocked_boto3_client, tmp_path, monkeypatch, mocked_responses, capsys
):
    output_ssh_cert = str(tmp_path / "id_rsa-cert.pub")
    input_ssh_cert = str(tmp_path / "id_rsa.pub")
    args = (
        "--user-name",
        "myUserName",
        "--environment",
        "integration",
        "--input-ssh-cert",
        input_ssh_cert,
        "--output-ssh-cert",
        output_ssh_cert,
    )

    fake_get_input = Mock(return_value="s.wrapped_token")
    monkeypatch.setattr(main, "get_input", fake_get_input)
    monkeypatch.setattr(main.getpass, "getpass", Mock(return_value="000000"))
    monkeypatch.setattr(main.boto3, "setup_default_session", Mock())

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

    mocked_payload = Mock()
    mocked_payload.read.return_value = '{"token": "s.atimakkok"}'
    mocked_boto3_client.return_value.invoke.return_value = {"Payload": mocked_payload}

    main.main(args)


def test_get_output_cert_path_no_output_path():
    args = argparse.Namespace()

    # Test with no output cert override
    # Test passing private key
    args.__setattr__("input_ssh_cert", "/home/user/.ssh/id_rsa")
    assert main.get_output_cert_path(args) == "/home/user/.ssh/id_rsa-cert.pub"

    # Test passing public key
    args.__setattr__("input_ssh_cert", "/home/user/.ssh/id_rsa.pub")
    assert main.get_output_cert_path(args) == "/home/user/.ssh/id_rsa-cert.pub"

    # Test passing private key
    args.__setattr__("input_ssh_cert", "/home/user/.ssh/my_hmrc_key")
    assert main.get_output_cert_path(args) == "/home/user/.ssh/my_hmrc_key-cert.pub"

    # Test passing private key
    args.__setattr__("input_ssh_cert", "/home/user/.ssh/my_hmrc_key.pub")
    assert main.get_output_cert_path(args) == "/home/user/.ssh/my_hmrc_key-cert.pub"


def test_get_output_cert_path_no_output_path_none():
    args = argparse.Namespace()
    args.__setattr__("output_ssh_cert", None)

    # Test passing private key
    args.__setattr__("input_ssh_cert", "/home/user/.ssh/id_rsa")
    assert main.get_output_cert_path(args) == "/home/user/.ssh/id_rsa-cert.pub"

    # Test passing public key
    args.__setattr__("input_ssh_cert", "/home/user/.ssh/id_rsa.pub")
    assert main.get_output_cert_path(args) == "/home/user/.ssh/id_rsa-cert.pub"

    # Test passing private key
    args.__setattr__("input_ssh_cert", "/home/user/.ssh/my_hmrc_key")
    assert main.get_output_cert_path(args) == "/home/user/.ssh/my_hmrc_key-cert.pub"

    # Test passing private key
    args.__setattr__("input_ssh_cert", "/home/user/.ssh/my_hmrc_key.pub")
    assert main.get_output_cert_path(args) == "/home/user/.ssh/my_hmrc_key-cert.pub"


def test_get_output_cert_path_with_output_path():
    args = argparse.Namespace()
    args.__setattr__("output_ssh_cert", "/home/user/.ssh/id_rsa-cert-override.pub")

    # Test passing private key
    args.__setattr__("input_ssh_cert", "/home/user/.ssh/id_rsa")
    assert main.get_output_cert_path(args) == "/home/user/.ssh/id_rsa-cert-override.pub"

    # Test passing public key
    args.__setattr__("input_ssh_cert", "/home/user/.ssh/id_rsa.pub")
    assert main.get_output_cert_path(args) == "/home/user/.ssh/id_rsa-cert-override.pub"


def test_parse_args(tmp_path, monkeypatch, mocked_responses, capsys):
    output_ssh_cert = str(tmp_path / "id_rsa-cert.pub")
    input_ssh_cert = str(tmp_path / "id_rsa.pub")
    args = (
        "--user-name",
        "myUserName",
        "--environment",
        "integration",
        "--input-ssh-cert",
        input_ssh_cert,
        "--output-ssh-cert",
        output_ssh_cert,
    )

    parsed_args = main.parse_args(args)

    assert hasattr(parsed_args, "user_name")
    assert parsed_args.user_name == "myUserName"
    assert hasattr(parsed_args, "environment")
    assert parsed_args.environment == "integration"
    assert hasattr(parsed_args, "input_ssh_cert")
    assert parsed_args.input_ssh_cert == input_ssh_cert
    assert hasattr(parsed_args, "output_ssh_cert")
    assert parsed_args.output_ssh_cert == output_ssh_cert
    assert hasattr(parsed_args, "ttl")
    assert parsed_args.ttl == 3600


def test_parse_args_no_output_cert(tmp_path):
    input_ssh_cert = str(tmp_path / "id_rsa.pub")
    args = (
        "--user-name",
        "myUserName",
        "--environment",
        "integration",
        "--input-ssh-cert",
        input_ssh_cert,
    )

    parsed_args = main.parse_args(args)

    assert hasattr(parsed_args, "user_name")
    assert parsed_args.user_name == "myUserName"
    assert hasattr(parsed_args, "environment")
    assert parsed_args.environment == "integration"
    assert hasattr(parsed_args, "input_ssh_cert")
    assert parsed_args.input_ssh_cert == input_ssh_cert
    assert hasattr(parsed_args, "output_ssh_cert")
    assert parsed_args.output_ssh_cert is None


def test_parse_args_sets_ttl(tmp_path):
    input_ssh_cert = str(tmp_path / "id_rsa.pub")
    args = (
        "--user-name",
        "myUserName",
        "--environment",
        "integration",
        "--input-ssh-cert",
        input_ssh_cert,
        "--ttl",
        "43200",
    )

    parsed_args = main.parse_args(args)

    assert hasattr(parsed_args, "user_name")
    assert parsed_args.user_name == "myUserName"
    assert hasattr(parsed_args, "environment")
    assert parsed_args.environment == "integration"
    assert hasattr(parsed_args, "input_ssh_cert")
    assert parsed_args.input_ssh_cert == input_ssh_cert
    assert hasattr(parsed_args, "output_ssh_cert")
    assert parsed_args.output_ssh_cert is None
    assert parsed_args.ttl == 43200


def test_exception_raised(tmp_path):
    input_ssh_cert = str(tmp_path / "id_rsa.pub")
    args = (
        "--user-name",
        "myUserName",
        "--environment",
        "integration",
        "--input-ssh-cert",
        input_ssh_cert,
        "--ttl",
        "43201",
    )

    parsed_args = main.parse_args(args)

    with pytest.raises(SystemExit):
        main.main(parsed_args)


@patch("request_ssh_access.__main__.boto3.client", autospec=True)
def test_invoke_grant_ssh_access_invalid_response_from_lambda_raises_exception(
    mocked_boto3_client, monkeypatch
):

    fake_get_input = Mock(return_value="s.wrapped_token")
    monkeypatch.setattr(main, "get_input", fake_get_input)
    monkeypatch.setattr(main.getpass, "getpass", Mock(return_value="000000"))
    monkeypatch.setattr(main.boto3, "setup_default_session", Mock())

    mocked_payload = Mock()
    mocked_payload.read.return_value = (
        '{"error": "an error occurred", "stacktrace": "..."}'
    )
    mocked_boto3_client.return_value.invoke.return_value = {"Payload": mocked_payload}

    with pytest.raises(Exception, match=r"Invalid response from lambda: .+"):
        main.invoke_grant_ssh_access("username", "integration", "90")
