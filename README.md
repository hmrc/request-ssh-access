# request-ssh-access

A workflow helper utility to assist with requesting ssh access.


### Requirements
- Python 3.7
- [AWS CLI](https://aws.amazon.com/cli/) (required in order to execute the `aws lambda invoke` command)

### Installation
```bash
pip install -i https://artefacts.tax.service.gov.uk/artifactory/api/pypi/pips/simple request-ssh-access
```

### Usage
```
request-ssh-access --user aws.username --environment integration
```

- The utility will print the command for the authorised user to execute. Copy and send it to them.
- The authorised user will execute the command and receive a [Vault Cubbyhole token](https://www.vaultproject.io/docs/secrets/cubbyhole/index.html) and will send it back to you.
- Input the cubbyhole token and your LDAP credentials back in the utility. 
- The utility will fetch the signed certificate from the appropriate Vault server.
- The utility will print a template `ssh` command which you can use to log into a remote ssh host.

##### Command line options:
###### `--output-ssh-cert`
Path to write signed key certificate, default `~/.ssh/id_rsa-cert.pub`.

When overriding this, use `ssh -i` when logging onto the remote host in order
to point to the public key and certificate, like so:

```
ssh -i /location/of/public/key -i /location/of/certificate ${REMOTE_HOST}
```


### Development environment
1. Install tox
```
pip install tox pre-commit
```

2. Clone the repository
```
git clone git@github.com:hmrc/request-ssh-access.git
cd request-ssh-access
```

3. To run linters and tests
```
tox
```

4. To run formatter
```
tox -e black
```

### Releasing to artifactory
Each push to `master` will trigger a job in [build](https://build.tax.service.gov.uk/job/platform-security/job/request-ssh-access/) which will run tests, upload the package to artefacts.tax.service.gov.uk, and create a release in this repo.

### License

This code is open source software licensed under the [Apache 2.0 License]("http://www.apache.org/licenses/LICENSE-2.0.html").
