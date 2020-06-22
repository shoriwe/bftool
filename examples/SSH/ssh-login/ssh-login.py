import paramiko


port = 22


def check_creds(username: str, password: str, host: str):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, port, username, password, timeout=2, allow_agent=False, look_for_keys=False)
        return f"{username}:{password}@{host}:{port}"
    except Exception as e:
        if not isinstance(e, paramiko.AuthenticationException):
            return f"{username}:{password}@{host}:{port}" + " - " + str(e)
    client.close()
