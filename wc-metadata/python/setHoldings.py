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

scope = ['WorldCatMetadataAPI:view_brief_bib', 'WorldCatMetadataAPI:manage_institution_holdings']

auth = HTTPBasicAuth(oclc_key, oclc_secret)
client = BackendApplicationClient(client_id=oclc_key, scope=scope)
oauth_session = OAuth2Session(client=client)

identifiers = {
    "isbn": "bn",
    "issn": "in"
}

def setHoldingByIdentifier(identifier, type='oclcNumber'):
    if type == 'oclcNumber':
        result = setHolding(identifier)
    else:
        result = searchMetadata(identifier, type)

    return pd.Series(result)

def searchMetadata(identifier, type):
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
                    results = setHolding(oclcNumber)
                else:
                    results = ['failed']
            except json.decoder.JSONDecodeError:
                results = ['failed']
        except requests.exceptions.HTTPError as err:
            results = ['failed']
    else:
        raise ValueError('Invalid type value. Valid type values are' + ','.join(str(identifiers.keys)))
    return results

def setHolding(oclcNumber):
    requestURL = "https://metadata.api.oclc.org/worldcat/manage/institution/holdings/" + str(oclcNumber) + "/set"
    try:
        r = oauth_session.get(requestURL, headers={"Accept":"application/json"})
        r.raise_for_status()
        try:
            result = r.json()
            if result.get('success') == "true":
                status = 'success'
                oclcNumber = result.get('controlNumber')
                results = [status, oclcNumber]
            else:
                results = ['failed']
        except json.decoder.JSONDecodeError:
            results = ['failed']
    except requests.exceptions.HTTPError as err:
        results = ['failed']

    return results

item_file = "setHoldings.csv"
file = open(item_file, "r")
csv_read = pd.read_csv(file, index_col=False, encoding='utf-8', nrows=25000)

try:
    token = oauth_session.fetch_token(token_url=token_url, auth=auth)
    csv_read[['status', 'oclcNumber']] = csv_read.apply (lambda row: setHoldingByIdentifier(row['oclcNumber']), axis=1)

    output_dir = "setHoldings-result.csv"
    csv_read.to_csv(output_dir, index=False)
except BaseException as err:
    print(err)