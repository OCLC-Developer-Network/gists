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

import os
from dotenv import load_dotenv
from oauthlib.oauth2 import BackendApplicationClient
from requests.auth import HTTPBasicAuth
from requests_oauthlib import OAuth2Session
import requests

# Load environment variables from .env file
load_dotenv()

# Get configuration from environment variables
serviceURL = os.getenv('METADATA_SERVICE_URL', 'https://metadata.api.oclc.org/worldcat/manage/bibs')
token_url = os.getenv('OCLC_TOKEN_URL', 'https://oauth.oclc.org/token')
oclc_key = os.getenv('OCLC_KEY')
oclc_secret = os.getenv('OCLC_SECRET')

if not oclc_key or not oclc_secret:
    raise ValueError("OCLC_KEY and OCLC_SECRET environment variables must be set")

# get a token
scope = ['WorldCatMetadataAPI:manage_bibs', 'WorldCatMetadataAPI:view_brief_bib']
auth = HTTPBasicAuth(oclc_key, oclc_secret)
client = BackendApplicationClient(client_id=oclc_key, scope=scope)
wskey = OAuth2Session(client=client)

try:
    token = wskey.fetch_token(token_url=token_url, auth=auth) 
    try:
        r = wskey.get(serviceURL + "/1", headers={"Accept":"application/marc21+xml"})
        r.raise_for_status
        xml = r.content
        print(xml)
    except requests.exceptions.HTTPError as err:
        print(err)
except BaseException as err:
    print(err)        