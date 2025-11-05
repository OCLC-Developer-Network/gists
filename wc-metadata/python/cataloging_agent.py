import os
from oauthlib.oauth2 import BackendApplicationClient
from requests.auth import HTTPBasicAuth
from requests_oauthlib import OAuth2Session
import json
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Load configuration from environment variables
oclc_key = os.getenv('OCLC_KEY')
oclc_secret = os.getenv('OCLC_SECRET')
token_url = os.getenv('OCLC_TOKEN_URL', 'https://oauth.oclc.org/token')

if not oclc_key or not oclc_secret:
    raise ValueError("OCLC_KEY and OCLC_SECRET environment variables must be set. Please create a .env file with your API credentials.")

scope = ['WorldCatMetadataAPI:manage_institution_holdings context:91475']
oclcNumber = 1
auth = HTTPBasicAuth(oclc_key, oclc_secret)
client = BackendApplicationClient(client_id=oclc_key, scope=scope)
oauth_session = OAuth2Session(client=client)
try:
    token = oauth_session.fetch_token(token_url=token_url, auth=auth)
    try:
        r = oauth_session.post("https://metadata.api.oclc.org/worldcat/manage/institution/holdings/" + str(oclcNumber) + "/set", headers={"Accept":"application/json"})
        r.raise_for_status
        try:
            result = r.json()
            status = "success"
        except json.decoder.JSONDecodeError:
            status = "failed"
    except requests.exceptions.HTTPError as err:
        status = "failed"
except BaseException as err:
    print(err)