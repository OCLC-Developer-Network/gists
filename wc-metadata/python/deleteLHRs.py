import pandas as pd
import json
import yaml
import requests
from oauthlib.oauth2 import BackendApplicationClient
from requests.auth import HTTPBasicAuth
from requests_oauthlib import OAuth2Session

with open("config.yml", 'r') as stream:
    config = yaml.safe_load(stream)

scope = ['WorldCatMetadataAPI:view_my_holdings', 'WorldCatMetadataAPI:manage_institution_lhrs']

auth = HTTPBasicAuth(config.get('key'), config.get('secret'))
client = BackendApplicationClient(client_id=config.get('key'), scope=scope)
oauth_session = OAuth2Session(client=client)

identifiers = {
    "oclcNumber": "oclcNumber",
    "barcode": "barcode"
}

def removeLHR(identifier, type='lhrID', holdingLocation = ""):
    if type == 'lhrID':
        metadata = deleteLHR(identifier)
    else:
        metadata = searchLHR(identifier, type, holdingLocation)

    return pd.Series(metadata)

def searchLHR(identifier, type, holdingLocation):
    if type in identifiers.keys():
        searchString = identifiers.get(type) + '=' + identifier

        requestURL = "https://metadata.api.oclc.org/worldcat/search/my-holdings?" + searchString + "&limit=1&orderBy=mostWidelyHeld&groupRelatedEditions=true"
        try:
            r = oauth_session.get(requestURL, headers={"Accept":"application/json"})
            r.raise_for_status()
            try:
                result = r.json()
                if result.get('numberOfHoldings') == 1:
                    lhrID = result.get('detailedHoldings')[0].get('lhrControlNumber')
                    status = deleteLHR(lhrID)
                    barcode = result.get('detailedHoldings')[0].get('lhrControlNumber').get("holdingParts").get("pieceDesignation")
                elif result.get('numberOfHoldings') > 1:
                    if holdingLocation:
                        holdings = result.get('detailedHoldings')
                        lhr = [holding for holding in holdings if holding.get("location").get('sublocationCollection') == holdingLocation]
                        if len(lhr) > 1:
                            status = "failed more than 1 LHR matched"
                            lhrID = ""
                            barcode = ""
                        else:
                            lhrID = lhr[0].get('lhrControlNumber')
                            status = deleteLHR(lhrID)
                            barcode = ""
                    else:
                        status = "failed more than 1 LHR matched"
                        lhrID = ""
                        barcode = ""
                elif result.get('numberOfHoldings') > 1:
                    status = "failed more than 1 LHR matched"
                    lhrID = ""
                    barcode = ""
                else:
                    status = "failed no LHRs matched"
                    lhrID = ""
                    barcode = ""
            except json.decoder.JSONDecodeError:
                status = 'failed'
                lhrID = ""
                barcode = ""
        except requests.exceptions.HTTPError as err:
            status = "failed"
            lhrID = ""
            barcode = ""
    else:
        raise ValueError('Invalid type value. Valid type values are' + ','.join(str(identifiers.keys)))
    return pd.Series([status, lhrID, barcode])


def deleteLHR(lhrID):
    requestURL = "https://metadata.api.oclc.org/worldcat/manage/lhrs/" + str(lhrID)
    try:
        r = oauth_session.delete(requestURL, headers={"Accept":"application/json"})
        r.raise_for_status()
        try:
            status = 'success'
        except json.decoder.JSONDecodeError:
            status = "failed"
    except requests.exceptions.HTTPError as err:
        status = "failed"

    return status

item_file = "getMetadata.csv"
file = open(item_file, "r")
csv_read = pd.read_csv(file, index_col=False, encoding='utf-8', nrows=25000)

try:
    token = oauth_session.fetch_token(token_url="https://oauth.oclc.org/token", auth=auth)
    csv_read[['status', 'lhr', 'barcode']] = csv_read.apply (lambda row: removeLHR(row['oclcNumber'], 'oclcNumber'), axis=1)

    output_dir = "getMetadata-result.csv"
    csv_read.to_csv(output_dir, index=False)
except BaseException as err:
    print(err)