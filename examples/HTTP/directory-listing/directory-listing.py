import requests
import os.path


def check_file(url: str, file: str, extension: str):
    complete_url = (os.path.join(url, file)).replace("\\", "/")
    if extension:
        complete_url += f".{extension}"
    response = requests.get(complete_url)
    if response.status_code in (200, 204, 301, 302, 307, 401, 403):
        return "[+] " + complete_url
