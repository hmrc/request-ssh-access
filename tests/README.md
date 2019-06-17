## Note on testing
Because this tool is a helper utility that only 
interfaces with external services, and we cannot
store credentials for any environment in git, our
best option for testing is manual test.

To make testing easier, we've supplied a small 
script that will generate and wrap a vault token
in the `integration` environment, and will execute 
the tool for you with test parameters.  To run it, 
execute the following commands:

```
python setup.py install
cd tests
./store-cert-in-vault.sh ${LDAP_USERNAME}
```

The script will: 
1. Authenticate with `integration` Vault for
you.
2. Wrap a mock certificate in Vault.
3. Give you the token to supply later.
4. Run the request-ssh-access script.

The resulting ssh certificate will be written to 
`./id_rsa-cert.pub`.

