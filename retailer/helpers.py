import requests
import json
import datetime
import pytz

from utilities.loggers import logger as log


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
        log.exception(msg=f"unable to get access token, issue: {response['error_description']}")
        return None, response['error_description']


def refresh_access_token(shop):
    try:
        login_url = "https://login.bol.com"
        data = {
            "client_id": shop.client_id,
            "client_secret": shop.client_secret,
            "grant_type": "client_credentials",
        }
        resp = requests.post(login_url + "/token", auth=(shop.client_id, shop.client_secret), data=data)
        resp.raise_for_status()
        shop.stored_access_token = resp.json()['access_token']
        delta = datetime.timedelta(minutes=5)
        now = datetime.datetime.utcnow()
        now = now.replace(tzinfo=pytz.utc)
        shop.access_token_ttl = now + delta
        shop.save()
        return resp.json()['access_token']
    except Exception as e:
        log.exception(msg=f'unale to refresh access token, issue: {e}')
        return False

