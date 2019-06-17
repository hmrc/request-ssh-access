#!/bin/bash
# unofficial bash strict mode, more info: http://redsymbol.net/articles/unofficial-bash-strict-mode/
set -euo pipefail
IFS=$'\n\t'

readonly USERNAME="${1}"

echo -n "Enter Integration LDAP password: "
read -r -s PASSWORD
readonly PASSWORD

readonly AUTH_REQUEST_BODY="{\"password\": \"${PASSWORD}\"}"

readonly AUTH_TOKEN=$(curl -Ss -X POST \
  https://vault.tools.integration.tax.service.gov.uk/v1/auth/ldap/login/"${USERNAME}" \
  -H "Content-Type: application/json" \
  -d "${AUTH_REQUEST_BODY}" | jq '.auth.client_token' | sed 's/"//g')


readonly WRAPPED_TOKEN=$(curl -Ss -X POST \
  https://vault.tools.integration.tax.service.gov.uk/v1/sys/wrapping/wrap \
  -H "Content-Type: application/json" \
  -H "X-Vault-Token: ${AUTH_TOKEN}" \
  -H "X-Vault-Wrap-TTL: 600" \
  -d '{
        "signed_key": "ssh-rsa-cert-v01@openssh.com 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\n"
    }' | jq '.wrap_info.token' | sed 's/"//g')


echo "Use the following token when prompted by request-ssh-access: ${WRAPPED_TOKEN}"
echo "Press any key when ready"
read -r

request-ssh-access --user "${USERNAME}" \
                   --environment integration \
                   --ssh-public-key ./id_rsa.pub \
                   --output-ssh-cert ./id_rsa-cert.pub
