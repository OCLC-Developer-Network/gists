import yaml
from oauthlib.oauth2 import BackendApplicationClient
from requests.auth import HTTPBasicAuth
from requests_oauthlib import OAuth2Session

with open("config.yml", 'r') as stream:
    config = yaml.safe_load(stream)

scope = ['WorldCatMetadataAPI context:91475']
oclcNumber = 1
auth = HTTPBasicAuth(config.get('key'), config.get('secret'))
client = BackendApplicationClient(client_id=config.get('key'), scope=scope)
oauth_session = OAuth2Session(client=client)
try:
    token = oauth_session.fetch_token(token_url=config.get('token_url'), auth=auth)
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
    return err