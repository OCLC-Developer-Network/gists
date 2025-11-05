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

def getLatestEdition(oclcNumber):
    requestURL = "https://metadata.api.oclc.org/worldcat/search/brief-bibs/" + str(oclcNumber) + "/other-editions?inLanguage=eng&limit=1&orderBy=publicationDateDesc"
    try:
        r = oauth_session.get(requestURL, headers={"Accept":"application/json"})
        r.raise_for_status()
        try:
            result = r.json()
            if result.get('briefRecords'):
                if (str(oclcNumber) == result.get('briefRecords')[0].get('oclcNumber')):
                    isLatestEdition = "true"
                elif (result.get('briefRecords')[0].get('mergedOclcNumbers') and str(oclcNumber) in result.get('briefRecords')[0].get('mergedOclcNumbers')):
                    isLatestEdition = "true"
                else:
                    isLatestEdition = "false"
                latestEditionOCN = result.get('briefRecords')[0].get('oclcNumber')
                latestEditionYear = result.get('briefRecords')[0].get('date')
            else:
                isLatestEdition = ""
                latestEditionOCN = ""
                latestEditionYear = ""
        except json.decoder.JSONDecodeError:
            isLatestEdition = ""
            latestEditionOCN = ""
            latestEditionYear = ""
    except requests.exceptions.HTTPError as err:
        status = "failed"

    return pd.Series([isLatestEdition, latestEditionOCN, latestEditionYear])

item_file = "findLatestEdition.csv"
file = open(item_file, "r")
csv_read = pd.read_csv(file, index_col=False, encoding='utf-8')

try:
    token = oauth_session.fetch_token(token_url=token_url, auth=auth)
    csv_read[['isLatestEdition', 'latestEditionOCN', 'latestEditionYear']] = csv_read.apply (lambda row: getLatestEdition(row['oclcNumber']), axis=1)

    output_dir = "findLatestEdition-result.csv"
    csv_read.to_csv(output_dir, index=False)
except BaseException as err:
    print(err)