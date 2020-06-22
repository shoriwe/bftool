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

```bash
python -m bftool -w rhost:list-of-rhosts.txt -w domain:list-of-domains.txt -w username:list-of-usernames.txt -w password:list-of-passwords.txt PATH_TO_SCRIPT_FOLDER/smb-login.py check_creds
```