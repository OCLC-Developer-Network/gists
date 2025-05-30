import yaml
from oauthlib.oauth2 import BackendApplicationClient
from requests.auth import HTTPBasicAuth
from requests_oauthlib import OAuth2Session
import requests
from io import StringIO
import time
import pymarc
from pymarc import Record, Field, Subfield, Indicators

def getLDRFromBib(oclcNumber):
    ldr = ''
    try:
        r = oauth_session.get("https://metadata.api.oclc.org/worldcat/manage/bibs/" + oclcNumber, headers={"Accept":"application/marcxml+xml"})
        r.raise_for_status()
        marcRecords = pymarc.parse_xml_to_array(StringIO(r.text))
        ldr = marcRecords[0].leader
    except requests.exceptions.HTTPError as err:
        status = "failed"
    return ldr

def createLBD(oclcNumber, ldr, note):
    record = Record(leader=ldr)
    record.add_field(Field(tag='004', data=oclcNumber))
    record.add_field(
        Field(
            indicators= Indicators(' ', ' '),
            tag = '500',
            subfields = [
                Subfield(code='a', value= note)
            ]),
        Field(
            indicators= Indicators(' ', ' '),
            tag = '935',
            subfields = [
                Subfield(code='a', value= str(time.time()))
            ]),
        Field(
            indicators= Indicators(' ', ' '),
            tag = '940',
            subfields = [
                Subfield(code='a', value= config.get('oclcSymbol'))
            ])
    )
    record = pymarc.record_to_xml(record).decode("utf-8")
    return record

with open("config.yml", 'r') as stream:
    config = yaml.safe_load(stream)

scope = ['WorldCatMetadataAPI:manage_institution_lbds', 'WorldCatMetadataAPI:view_marc_bib']

auth = HTTPBasicAuth(config.get('key'), config.get('secret'))
client = BackendApplicationClient(client_id=config.get('key'), scope=scope)
oauth_session = OAuth2Session(client=client)

oclcNumber = '42397965'
note = 'This is a test note'
try:
    token = oauth_session.fetch_token(token_url=config.get('token_url'), auth=auth)
    ldr = getLDRFromBib(oclcNumber)
    record = createLBD(oclcNumber, ldr, note)
    try:
        r = oauth_session.post("https://metadata.api.oclc.org/worldcat/manage/lbds", headers={"Accept":"application/marcxml+xml", "Content":"application/marcxml+xml"}, data=record)
        r.raise_for_status()
        marcRecords = pymarc.parse_xml_to_array(StringIO(r.text))
        lbdNumber = marcRecords[0]['001'].value()
        print(lbdNumber)
    except requests.exceptions.HTTPError as err:
        print (err)
except BaseException as err:
    print (err)