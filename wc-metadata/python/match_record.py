import os
from oauthlib.oauth2 import BackendApplicationClient
from requests.auth import HTTPBasicAuth
from requests_oauthlib import OAuth2Session
import requests
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Load configuration from environment variables
oclc_key = os.getenv('OCLC_KEY')
oclc_secret = os.getenv('OCLC_SECRET')
token_url = os.getenv('OCLC_TOKEN_URL', 'https://oauth.oclc.org/token')

if not oclc_key or not oclc_secret:
    raise ValueError("OCLC_KEY and OCLC_SECRET environment variables must be set. Please create a .env file with your API credentials.")

scope = ['WorldCatMetadataAPI:match_bibs']

auth = HTTPBasicAuth(oclc_key, oclc_secret)
client = BackendApplicationClient(client_id=oclc_key, scope=scope)
oauth_session = OAuth2Session(client=client)

with open('matchRecord.xml', 'r') as file:
    record = file.read()

try:
    token = oauth_session.fetch_token(token_url=token_url, auth=auth)
    try:
        r = oauth_session.post("https://metadata.api.oclc.org/worldcat/manage/bibs/match", headers={"Accept":"application/json", "Content":"application/marcxml+xml"}, data=record)
        r.raise_for_status()
        try:
            result = r.json()
            oclcNumber = result['briefRecords'][0]['oclcNumber']
            try:
                r2 = oauth_session.get("https://metadata.api.oclc.org/worldcat/manage/bibs/" + oclcNumber, headers={"application/marcxml+xml"})
                r2.raise_for_status()
                recordToPull = r2.text
                with open('pulledRecord.xml', 'w') as file:
                    file.write(recordToPull)
            except requests.exceptions.HTTPError as err:
                status = "failed"
        except json.decoder.JSONDecodeError:
            status = "failed"
    except requests.exceptions.HTTPError as err:
        status = "failed"
except BaseException as err:
    print (err)