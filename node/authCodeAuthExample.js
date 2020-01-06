/**
 * Using simple-oauth2 (https://github.com/lelylan/simple-oauth2) 
 * and making a request to WorldCat Metadata API to get a Bibliographic record
 */ 
"use strict";
const express = require('express');
const session = require('express-session')
const bodyParser = require('body-parser');
const fs = require('fs');
const yaml = require('js-yaml');
const axios = require("axios");
 
let configFile = fs.readFileSync(require('path').resolve(__dirname, '../config.yml')).toString();
global.config = yaml.load(configFile);
 
const credentials = {
  client: {
    id: config['key'],
    secret: config['secret']
  },
  auth: {
	authorizePath: '/auth',  
    tokenHost: 'https://oauth.oclc.org',
    tokenPath: '/token',
  }
};
 
const scopes = "WorldCatMetadataAPI refresh_token";
 
const oauth2 = require('simple-oauth2').create(credentials);

const redirect_uri = 'http://localhost:8000/'

const app = express();

app.engine('html', require('ejs').renderFile);
app.set('view engine', 'html');
app.set('views', 'views'); 
 
app.use(bodyParser.urlencoded({ extended: true }));
app.use(express.static('public'));
app.use(session({secret: 'Nx^P6u', cookie: {secure: false, maxAge: 60000}, resave: false, saveUninitialized: false}));

async function getAccessToken (req, res, next){
	
	if (req.query['error']){
		console.log(req.query['error']);
		console.log(req.query['error_description']);		
	} else if (req.session.accessToken && req.session.accessToken.refreshToken) {	
		// need to figure out how to use a refresh token when don't have an Access Token object anymore
        next();
	} else if (req.query['code']) {
		const tokenConfig = {
				code: req.query['code'],
				redirect_uri: redirect_uri,
				scope: scopes
		};

		// Save the access token
		try {
		  let result = await oauth2.authorizationCode.getToken(tokenConfig)
		  let accessToken = oauth2.accessToken.create(result);
		  req.session.accessToken = accessToken;
          //redirect to the state parameter
          let state = decodeURIComponent(req.query['state']);
          res.redirect(state);
		} catch (error) {
		  console.log(error);
		  console.log('Access Token Error', error.message);		 
		}
	}else {
		// redirect to login + state parameter
		let loginURL = oauth2.authorizationCode.authorizeURL({
			  redirect_uri: redirect_uri,
			  scope: scopes,
			  state: encodeURIComponent(req.originalUrl)
			});
		console.log(loginURL);
		res.redirect(loginURL);
	}
}

app.use(function (req, res, next) {
	getAccessToken(req, res, next);
});

app.get('/', (req, res) => {
    let config = {
            headers: {
                'Authorization': 'Bearer ' + req.session.accessToken.token,
                'User-Agent': 'node.js KAC client'
            }
        };
    let url = config['service_url'] + '/bib/data/1';
	axios.get(url, config)
	.then(results => {
		console.log(results);
	})
	.catch (error => {
		console.log(error);
	})
});

let port = process.env.PORT || 8000;

//Server
app.listen(port, () => {
 console.log(`Listening on: http://localhost:${port}`);
});