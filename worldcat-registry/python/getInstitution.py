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
 
with open("../config.yml", 'r') as stream:
    config = yaml.safe_load(stream)
     
serviceURL = config.get('registry_service_url')   
# get a token
scope = ['configPlatform']
auth = HTTPBasicAuth(config.get('key'), config.get('secret'))
client = BackendApplicationClient(client_id=config.get('key'), scope=scope)
wskey = OAuth2Session(client=client)

try:
    token = wskey.fetch_token(token_url=config.get('token_url'), auth=auth) 
    try:
        r = wskey.get(serviceURL + "/institution/data/128807", headers={"Accept":"application/json"})
        r.raise_for_status
        result = r.json()
        if result.get('content').get('institution'):
            print(result.get('content').get('institution').get('nameLocation').get('institutionName'))
        else:
            print(result.get('content').get('section').get('nameLocation').get('institutionName'))
    except requests.exceptions.HTTPError as err:
        print(err)
except BaseException as err:
    print(err)        