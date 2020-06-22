# Requirements
### Python modules
- `paramiko`
## Requirements installation
```bash
pip install paramiko
```
# Description
Bruteforce the SSH login
# Usage

- First go to the folder where the script is
```bash
cd PATH_TO_SCRIPT_LOCATION
```

- Then you can execute it something like
```bash
python -m bftool -w host:list-of-hosts.txt -w -w username:list-of-usernames.txt -w password:list-of-passwords.txt ssh-login.py check_creds
```
