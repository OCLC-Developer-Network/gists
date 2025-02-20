import pandas as pd
import json
import yaml
import requests
from oauthlib.oauth2 import BackendApplicationClient
from requests.auth import HTTPBasicAuth
from requests_oauthlib import OAuth2Session


with open("config.yml", 'r') as stream:
    config = yaml.safe_load(stream)

scope = ['WorldCatMetadataAPI']

auth = HTTPBasicAuth(config.get('key'), config.get('secret'))
client = BackendApplicationClient(client_id=config.get('key'), scope=scope)
oauth_session = OAuth2Session(client=client)

identifiers = {
    "isbn": "bn",
    "issn": "in"
}

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

item_file = "getHoldings.csv"
file = open(item_file, "r")
csv_read = pd.read_csv(file, index_col=False, encoding='utf-8', nrows=25000)

try:
    token = oauth_session.fetch_token(token_url="https://oauth.oclc.org/token", auth=auth)
    csv_read[['status', 'oclcNumber']] = csv_read.apply (lambda row: setHolding(row['oclcNumber']), axis=1)

    output_dir = "getHoldings-result.csv"
    csv_read.to_csv(output_dir, index=False)
except BaseException as err:
    print(err)