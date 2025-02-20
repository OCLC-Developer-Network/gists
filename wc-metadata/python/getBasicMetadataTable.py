import pandas as pd
import json
import yaml
import requests
from oauthlib.oauth2 import BackendApplicationClient
from requests.auth import HTTPBasicAuth
from requests_oauthlib import OAuth2Session

with open("config.yml", 'r') as stream:
    config = yaml.safe_load(stream)

scope = ['WorldCatMetadataAPI:view_brief_bib']



auth = HTTPBasicAuth(config.get('key'), config.get('secret'))
client = BackendApplicationClient(client_id=config.get('key'), scope=scope)
oauth_session = OAuth2Session(client=client)

identifiers = {
    "isbn": "bn",
    "issn": "in"
}

def getMetadata(identifier, type='oclcNumber'):
    if type == 'oclcNumber':
        metadata = getRecord(identifier)
    else:
        metadata = searchMetadata(identifier, type)

    return pd.Series(metadata)

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
                    metadata = getRecord(oclcNumber)
                else:
                    metadata = None
                    status = "failed"
            except json.decoder.JSONDecodeError:
                metadata = None
                status = 'failed'
        except requests.exceptions.HTTPError as err:
            metadata = None
            status = "failed"
    else:
        raise ValueError('Invalid type value. Valid type values are' + ','.join(str(identifiers.keys)))
    return metadata


def getRecord(oclcNumber):
    requestURL = "https://metadata.api.oclc.org/worldcat/search/bibs/" + str(oclcNumber)
    try:
        r = oauth_session.get(requestURL, headers={"Accept":"application/json"})
        r.raise_for_status()
        try:
            result = r.json()
            if result.get('identifier'):
                title = result.get('title').get('mainTitle').get('text')
                creatorList = result.get('contributors').get('creator')
                creators = []
                for creator in creatorList:
                    name = getCreatorName(creator)
                    creators.append(name)
                creators = ','.join(creators)
                subjectList = result.get('subjects')
                subjects = []
                for subject in subjectList:
                    # just filter to bisacsh
                    if subject.get('vocabulary') == 'bisacsh':
                        subjects.append(subject.get('subjectName').get('text'))
                subjects = ','.join(subjects)
                genres = result.get('description').get('genres').join(',')
                metadata = [title,creators,subjects,genres]
            else:
                metadata = []
        except json.decoder.JSONDecodeError:
            status = "failed"
            metadata = None
    except requests.exceptions.HTTPError as err:
        status = "failed"
        metadata = None

    return metadata

def getCreatorName(creator):
    if creator.get('nonPersonName'):
        name = creator.get('nonPersonName').get('text')
    else:
        name = creator.get('firstName').get('text') + ' ' + creator.get('secondName').get('text')
    return name

item_file = "getMetadata.csv"
file = open(item_file, "r")
csv_read = pd.read_csv(file, index_col=False, encoding='utf-8', nrows=25000)

try:
    token = oauth_session.fetch_token(token_url="https://oauth.oclc.org/token", auth=auth)
    csv_read[['title','creators','subjects','genres']] = csv_read.apply (lambda row: getMetadata(row['oclcNumber']), axis=1)

    output_dir = "getMetadata-result.csv"
    csv_read.to_csv(output_dir, index=False)
except BaseException as err:
    print(err)