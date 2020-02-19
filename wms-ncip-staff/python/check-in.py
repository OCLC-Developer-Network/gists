#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ###############################################################################
# Copyright 2014 OCLC
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
###############################################################################

# Example of retrieving a token with Client Credentials Grant and https://github.com/requests/requests-oauthlib

import yaml
from oauthlib.oauth2 import BackendApplicationClient
from requests.auth import HTTPBasicAuth
from requests_oauthlib import OAuth2Session
import requests
 
with open("config.yml", 'r') as stream:
    config = yaml.safe_load(stream)
     
# get a token
scope = ['WMS_NCIP']
auth = HTTPBasicAuth(config.get('key'), config.get('secret'))
client = BackendApplicationClient(client_id=config.get('key'), scope=scope)
ncip_requests = OAuth2Session(client=client)

url = "https://circ.sd00.worldcat.org/ncip"

payload = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<NCIPMessage xmlns=\"http://www.niso.org/2008/ncip\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\"\n    xmlns:ncip=\"http://www.niso.org/2008/ncip\"\n    xsi:schemaLocation=\"http://www.niso.org/2008/ncip http://www.niso.org/schemas/ncip/v2_01/ncip_v2_01.xsd\"\n    ncip:version=\"http://www.niso.org/schemas/ncip/v2_01/ncip_v2_01.xsd\">\n    <CheckInItem>\n        <InitiationHeader>\n            <FromAgencyId>\n                <AgencyId ncip:Scheme=\"http://oclc.org/ncip/schemes/agencyid.scm\">129479</AgencyId>\n            </FromAgencyId>\n            <ToAgencyId>\n                <AgencyId>129479</AgencyId>\n            </ToAgencyId>\n            <ApplicationProfileType ncip:Scheme=\"http://oclc.org/ncip/schemes/application-profile/platform.scm\">Version 2011</ApplicationProfileType>\n        </InitiationHeader>\n        <ItemId>\n            <AgencyId>128807</AgencyId>\n            <ItemIdentifierValue>K123456789</ItemIdentifierValue>\n        </ItemId>\n    </CheckInItem>\n</NCIPMessage>"
headers = {
  'Content-Type': 'application/xml'
}

try:
    token = ncip_requests.fetch_token(token_url=config.get('token_url'), auth=auth) 
    try:
        r = ncip_requests.post(url, headers=headers, data=payload)
        r.raise_for_status
        xml = r.content
        print(xml)
    except requests.exceptions.HTTPError as err:
        print(err)
except BaseException as err:
    print(err)