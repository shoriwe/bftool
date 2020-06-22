# Requirements
### Python modules
- `impacket`
## Requirements installation
```bash
pip install impacket
```
# Description
Bruteforce the SMB login
# Usage

- First go to the folder where the script is
```bash
cd PATH_TO_SCRIPT_LOCATION
```

- Then you can execute it something like
```bash
python -m bftool -w rhost:list-of-rhosts.txt -w domain:list-of-domains.txt -w username:list-of-usernames.txt -w password:list-of-passwords.txt smb-login.py check_creds
```
