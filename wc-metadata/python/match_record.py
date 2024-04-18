import yaml
from oauthlib.oauth2 import BackendApplicationClient
from requests.auth import HTTPBasicAuth
from requests_oauthlib import OAuth2Session

with open("config.yml", 'r') as stream:
    config = yaml.safe_load(stream)

scope = ['WorldCatMetadataAPI']

auth = HTTPBasicAuth(config.get('key'), config.get('secret'))
client = BackendApplicationClient(client_id=config.get('key'), scope=scope)
oauth_session = OAuth2Session(client=client)

with open('matchRecord.xml', 'r') as file:
    record = file.read()

try:
    token = oauth_session.fetch_token(token_url=config.get('token_url'), auth=auth)
    try:
        r = oauth_session.post("https://metadata.api.oclc.org/worldcat/manage/bibs/match", headers={"Accept":"application/json", "Content":"application/marcxml+xml"}, data=record)
        r.raise_for_status
        try:
            result = r.json()
            oclcNumber = result['briefRecords'][0]['oclcNumber']
            try:
                r2 = oauth_session.get("https://metadata.api.oclc.org/worldcat/manage/bibs/" + oclcNumber, headers={"application/marcxml+xml"})
                r2.raise_for_status
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
    return err