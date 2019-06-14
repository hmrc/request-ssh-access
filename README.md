
# request-ssh-access

A workflow helper utility to assist with requesting ssh access.


### Requirements
- Python 3.7

### Usage
```
request-ssh-access --user aws.username --environment externaltest
```

- The utility will print the command for the authorised user to execute. Copy and send it to them.
 - The authorised user will execute the command and receive a [Vault Cubbyhole token](https://www.vaultproject.io/docs/secrets/cubbyhole/index.html) and will send it back to you.
- Input the cubbyhole token and your LDAP credentials back in the utility. 
- The utility will fetch the signed certificate from the appropriate Vault server.
- The utility will print a template `ssh` command which you can use to log into a remote ssh host.

Note that you can override:
- `--ssh-public-key` - path to public key to sign
- `--output-ssh-cert` - path to write signed key certificate


### Installation
Until we publish this tool to Artifactory, manual installation:
```bash
git clone git@github.com:hmrc/request-ssh-access.git
cd request-ssh-access
python setup.py install 
```

(Once it's on Artifactory, `pip install -i https://artefacts.tax.service.gov.uk/artifactory/api/pypi/pips/simple request-ssh-access`)

### License

This code is open source software licensed under the [Apache 2.0 License]("http://www.apache.org/licenses/LICENSE-2.0.html").
