import requests
import logging

logger = logging.getLogger(__name__)


def login(environment, ldap_user_name, ldap_password):
    url = "https://vault.tools.{}.tax.service.gov.uk/v1/auth/ldap/login/{}".format(
        environment, ldap_user_name
    )
    payload = {"password": ldap_password}
    response = requests.post(url, json=payload)
    logger.debug("login response {} {}".format(response.status_code, response.text))

    client_token = response.json()["auth"]["client_token"]
    if client_token:
        logger.info("logged in to vault with user={}".format(ldap_user_name))
    return client_token


def unwrap(environment, vault_token, wrapped_token):
    url = "https://vault.tools.{}.tax.service.gov.uk/v1/sys/wrapping/unwrap".format(
        environment
    )

    payload = {"token": wrapped_token}
    headers = {"X-Vault-Token": vault_token}

    response = requests.post(url, json=payload, headers=headers)
    logger.debug("{} {}".format(response.status_code, response.text))
    errors = response.json().get("errors", [])
    if errors:
        raise Exception(str(errors))
    return response.json()["data"]["signed_key"]
