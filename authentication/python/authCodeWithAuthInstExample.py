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
# when specifying a particular institution to authenticate at 

import os
import oauthlib
from dotenv import load_dotenv
from oauthlib.oauth2 import BackendApplicationClient
from requests.auth import HTTPBasicAuth
from requests_oauthlib import OAuth2Session
import requests
from flask import Flask, request, redirect, session, url_for, render_template
from pickle import NONE

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
app = Flask(__name__)

# Load environment variables from .env file
load_dotenv()

app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'SIJFhkdoufoerljdfjto')

# Get configuration from environment variables
oclc_key = os.getenv('OCLC_KEY')
oclc_secret = os.getenv('OCLC_SECRET')
token_url = os.getenv('OCLC_TOKEN_URL', 'https://oauth.oclc.org/token')
auth_url = os.getenv('OCLC_AUTH_URL', 'https://oauth.oclc.org/auth')
wms_availability_url = os.getenv('WMS_AVAILABILITY_URL', 'https://circ.sd00.worldcat.org/availability')
registry_id = os.getenv('OCLC_REGISTRY_ID', '128807')

if not oclc_key or not oclc_secret:
    raise ValueError("OCLC_KEY and OCLC_SECRET environment variables must be set")

# get a token
scope = ['WMS_NCIP', 'WMS_Availability', 'SCIM:read_self', f'context:{registry_id}', 'refresh_token']
app.config['auth'] = HTTPBasicAuth(oclc_key, oclc_secret)
app.config['oauth_session'] = OAuth2Session(oclc_key, redirect_uri='http://localhost:5000/', scope=scope)

@app.before_request
def getToken():
    if request.args.get('error'):
        #render error page
        return "error " + request.args['error']
    elif request.args.get('code'):    
        try:
            token = app.config['oauth_session'].fetch_token(token_url=token_url, authorization_response=request.url, auth=app.config.get('auth'))
            # redirect
            return None
        except (ValueError, oauthlib.oauth2.rfc6749.errors.MissingTokenError) as err:
            #render error page
            return err.description
    else:   
        #redirect to a specific institution for login   
        authorization_url, state = app.config.get('oauth_session').authorization_url(auth_url + f"/{registry_id}")

        session['oauth_state'] = state
        return redirect(authorization_url)


@app.route('/')
def getBib(): 
    try:
        oauth_session = app.config.get('oauth_session');
        r = oauth_session.get(wms_availability_url + f"/sru/service?x-registryId={registry_id}&query=no:932367058", headers={"Accept":'application/xml'})
        r.raise_for_status
        xml = r.content
        return xml
    except requests.exceptions.HTTPError as err:
        status = "failed"
        return status