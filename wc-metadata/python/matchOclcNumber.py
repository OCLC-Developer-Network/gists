import pandas as pd
import json
import os
import requests
from oauthlib.oauth2 import BackendApplicationClient
from requests.auth import HTTPBasicAuth
from requests_oauthlib import OAuth2Session
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Load configuration from environment variables
oclc_key = os.getenv('OCLC_KEY')
oclc_secret = os.getenv('OCLC_SECRET')
token_url = os.getenv('OCLC_TOKEN_URL', 'https://oauth.oclc.org/token')

if not oclc_key or not oclc_secret:
    raise ValueError("OCLC_KEY and OCLC_SECRET environment variables must be set. Please create a .env file with your API credentials.")

scope = ['WorldCatMetadataAPI:view_brief_bib']

auth = HTTPBasicAuth(oclc_key, oclc_secret)
client = BackendApplicationClient(client_id=oclc_key, scope=scope)
oauth_session = OAuth2Session(client=client)

identifiers = {
    "isbn": "bn",
    "issn": "in"
}

def matchOclcNumber(identifier, type):
    if type in identifiers.keys():
        searchString = identifiers.get(type) + ':' + identifier

        requestURL = "https://metadata.api.oclc.org/worldcat/search/brief-bibs?" + searchString + "&limit=1&orderBy=mostWidelyHeld&groupRelatedEditions=true"
        try:
            r = oauth_session.get(requestURL, headers={"Accept":"application/json"})
            r.raise_for_status()
            try:
                result = r.json()
                if result.get('briefRecords'):
                    oclcNumber = result.get('briefRecords')[0].get('oclcNumber')
                else:
                    oclcNumber = None
                    status = "failed"
            except json.decoder.JSONDecodeError:
                oclcNumber = None
                status = 'failed'
        except requests.exceptions.HTTPError as err:
            oclcNumber = None
            status = "failed"
    else:
        raise ValueError('Invalid type value. Valid type values are' + ','.join(str(identifiers.keys)))
    return oclcNumber


item_file = "getMetadata.csv"
file = open(item_file, "r")
csv_read = pd.read_csv(file, index_col=False, encoding='utf-8', nrows=25000)

try:
    token = oauth_session.fetch_token(token_url=token_url, auth=auth)
    csv_read[['oclcNumber']] = csv_read.apply (lambda row: matchOclcNumber(row['isbn'], "isbn"), axis=1)

    output_dir = "getMetadata-result.csv"
    csv_read.to_csv(output_dir, index=False)
except BaseException as err:
    print(err)