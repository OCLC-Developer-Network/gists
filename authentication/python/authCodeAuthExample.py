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
import oauthlib
from oauthlib.oauth2 import BackendApplicationClient
from requests.auth import HTTPBasicAuth
from requests_oauthlib import OAuth2Session
import requests
from flask import Flask, request, redirect, session, url_for, render_template
from pickle import NONE
import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
app = Flask(__name__)
 
app.config['SECRET_KEY'] = 'SIJFhkdoufoerljdfjto'
 
with open("../config.yml", 'r') as stream:
    app.app_config = yaml.safe_load(stream)
     
# get a token
scope = ['WorldCatMetadataAPI']
app.config['auth'] = HTTPBasicAuth(app.app_config.get('key'), app.app_config.get('secret'))
app.config['oauth_session'] = OAuth2Session(app.app_config.get('key'), redirect_uri='http://localhost:5000/', scope=scope)

@app.before_request
def getToken():
    if request.args.get('error'):
        #render error page
        return "error " + request.args['error']
    elif request.args.get('code'):    
        try:
            token = app.config['oauth_session'].fetch_token(token_url=app.app_config.get('token_url'), authorization_response=request.url, auth=app.config.get('auth'))
            # redirect
            return None
        except (ValueError, oauthlib.oauth2.rfc6749.errors.MissingTokenError) as err:
            #render error page
            return err.description
    else:      
        authorization_url, state = app.config.get('oauth_session').authorization_url(app.app_config.get('auth_url'))

        session['oauth_state'] = state
        return redirect(authorization_url)


@app.route('/')
def getBib(): 
    try:
        oauth_session = app.config.get('oauth_session');
        r = oauth_session.get(app.app_config.get('metadata_service_url') + "/bib/data/1", headers={"Accept":'application/atom+xml;content="application/vnd.oclc.marc21+xml"'})
        r.raise_for_status
        xml = r.content
        return xml
    except requests.exceptions.HTTPError as err:
        status = "failed"
        return status