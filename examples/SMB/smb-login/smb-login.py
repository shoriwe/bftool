import impacket.smbconnection


port = 445


def check_creds(rhost: str, domain: str, username: str, password: str):
    connection = impacket.smbconnection.SMBConnection(remoteName=rhost, remoteHost=rhost, sess_port=port)
    try:
        password_to_hash = password.split(":")
        if len(password_to_hash) == 2:
            if 32 == len(password_to_hash[0]) == len(password_to_hash[1]):
                lmhash, nthash = password_to_hash
            else:
                lmhash = nthash = ""
        else:
            lmhash = nthash = ""
        connection.login(user=username, password=password, domain=domain, lmhash=lmhash, nthash=nthash,
                         ntlmFallback=True)
        result = f"{username}:{password}"
    except Exception as e:
        if str(e) != "SMB SessionError: STATUS_LOGON_FAILURE(The attempted logon is invalid. This is either "\
                     "due to a bad username or authentication information.)":
            result = f"{username}:{password}" + f" - {e}"
        else:
            result = None
    connection.close()
    return result
