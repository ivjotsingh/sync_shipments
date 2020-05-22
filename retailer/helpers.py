import requests
import json


def get_access_token(client_id, client_secret):
    try:
        login_url = "https://login.bol.com"
        data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "client_credentials",
        }
        resp = requests.post(login_url + "/token", auth=(client_id, client_secret), data=data)
        resp.raise_for_status()
        return resp.json()['access_token'], 'access_token fetched'
    except Exception as e:
        response = json.loads(e.response._content)
        return None, response['error_description']



