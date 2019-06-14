
# request-ssh-access

A workflow helper utility to assist with requesting ssh access.


### Requirements
- Python 3.7

### Usage

```request-ssh-access --user aws.username --environment externaltest```

- Print the command to copy-paste for the authorised user to execute
- The authorised user will receive a Vault cubbyhole token and will send it back to you
- Input the cubbyhole token and your LDAP credentials and the signed certificate will be fetched and 
  written to disk to `--output-ssh-cert`.
- A template `ssh` command will be printed which you can use to log into a remote ssh host.

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
