# request-ssh-access

A workflow helper utility to assist with requesting ssh access.


### Requirements
- Python 3.9
- [AWS CLI](https://aws.amazon.com/cli/) (required in order to execute the `aws lambda invoke` command)

### Installation
```bash
pip install --user -i https://artefacts.tax.service.gov.uk/artifactory/api/pypi/pips/simple request-ssh-access
```

### Usage
Prepend the following with your favourite profile manager, e.g. `aws-profile -p webops-users` or `aws-vault exec webops-users --`.
```
request-ssh-access --input-ssh-cert ~/path/to/ssh/key --user aws.username --environment integration --ttl (optional)
```

- The utility will print the command for the authorised user to execute. Copy and send it to them.
- The authorised user will execute the command and receive a [Vault Cubbyhole token](https://www.vaultproject.io/docs/secrets/cubbyhole/index.html) and will send it back to you.
- Input the cubbyhole token and your LDAP credentials back in the utility.
- The utility will fetch the signed certificate from the appropriate Vault server.
- The utility will write the signed certificate to the correct location (based on the input ssh certificate)
- The utility will print a template `ssh` command which you can use to log into a remote ssh host.

##### Command line options:
###### `--input-ssh-cert`
Path to the SSH key you use to sign in, default `~/.ssh/id_rsa.pub`.

When overriding this, you can specify either the private or public key and the
utility will work out the correct path for the signed certificate.

###### `--output-ssh-cert`
Path to write signed key certificate, if not supplied the default will be based
on the value supplied with the `--input-ssh-cert` parameter. Using the defaults
will result in a default value of `~/.ssh/id_rsa-cert.pub`.

###### `--ttl`
Optional TTL in seconds for the Vault generated ssh certificate lease which defaults to 1 hour.

### Logging in
To log in with a signed certificate, you must have SSH configured to use your
key *and* the associated signed certificate.

SSH needs to know both your key and the signed certificate in order to
authenticate. There are a few ways to pass this information to SSH.

These examples assume a private key of `~/.ssh/id_rsa` and a corresponding
public key `~/.ssh/id_rsa.pub`. If your key is named differently, make the
appropriate changes to the commands.

1. Specify both on the command line using the `-i` option:
   ```
   ssh -i <path to key> -i <path to signed certificate> user.name@host
   ```
1. Save the signed certificate with `-cert.pub` suffix. For example, if your
   public key is `~/.ssh/id_rsa.pub` then save your signed certificate as
   `~/.ssh/id_rsa-cert.pub` and SSH will automatically find the signed
   certificate when using this key.
   ```
   ssh -i ~/.ssh/id_rsa.pub user.name@host
   ```
1. Configure SSH to use the correct key and user name when connecting to a
   host, e.g. if your key is `~/.ssh/id_rsa.pub` and your username is
   `user.name` add the following to the relevant `Host` section in your
   `~/.ssh/config` file
   ```
   User user.name
   IdentityFile ~/.ssh/id_rsa
   ```

If your signed certificate is saved as `~/.ssh/id_rsa-cert.pub`, then you
should now be able to log in using:

```
ssh user.name@host
```

#### Troubleshooting
You may have difficulties using SSH to log in to our servers, as we limit
`MaxAuthTries` to 2 on our servers. This can cause problems if you are using
`ssh-agent`, as this may present multiple keys in a different order to what you
are expecting.

This can be controlled in a couple of ways.

1. Check if you have more than 1 ssh key in aws IAM
   [currently only the first key will be used](https://github.com/hmrc/grant-ssh-access/blob/77aa00aac00556a3811898343ca779fc3a8019aa/grant_ssh_access.py#L84)

1. Disable use of SSH agent for this connection, by either:
   1. Unset the `unset SSH_AUTH_SOCK` environment variable so SSH cannot
      locate the running agent.
   1. Set the `IdentityAgent` option to `none` at the command line to disable
      use of the agent, e.g. `ssh -o "IdentityAgent none" user.name@host`
   1. Set the `IdentityAgent` option to `none` in the relevant `Host` section
      of `~/.ssh/config` to disable use of the agent.
1. If you have configured your SSH connections in `~/.ssh/config` as described
   above in the logging in section, you can also set the `IdentitiesOnly`
   option to `yes`, e.g.
   ```
   User user.name
   IdentitiesOnly yes
   IdentityFile ~/.ssh/id_rsa
   ```
   This will continue allowing use of `ssh-agent`, but only use keys named using
   `IdentityFile`, or specified on the command line.
1. Some linux distributions are phasing out `ssh+rsa` keys in favor of `ED25519` however this is not yet supported by AWS
   if you are getting an error in verbose mode such as `no mutual signature algorithm` 
   then add the following lines to your `~/.ssh/config`
   ```ssh
   PubkeyAcceptedKeyTypes +ssh-rsa
   ```
1. If you are getting the error `Load key "./my-key.pub": invalid format`
   you are using your public key. Please use your private key in the `-i` flag

### Development environment

1. Install pipenv

   ```bash
   pip3 install pipenv pre-commit
   ```

1. Clone the repository

   ```bash
   git clone git@github.com:hmrc/request-ssh-access.git
   cd request-ssh-access
   ```

1. Remove old virtual environment and install all dependencies

   ```bash
   pipenv --rm
   pipenv install
   ```

1. To run linters and tests

   ```bash
   pipenv run tox
   ```

1. To run formatter

   ```bash
   pipenv run tox -e black
   ```

### Releasing to artifactory

Each push to `master` will trigger a job in [build](https://build.tax.service.gov.uk/job/platform-security/job/request-ssh-access/) which will run tests, upload the package to artefacts.tax.service.gov.uk, and create a release in this repo.

### License

This code is open source software licensed under the [Apache 2.0 License]("http://www.apache.org/licenses/LICENSE-2.0.html").
