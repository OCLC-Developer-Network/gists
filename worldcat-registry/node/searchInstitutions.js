/* Using simple-oauth2 (https:github.com/lelylan/simple-oauth2) 
 * and making a request to WorldCat Metadata API to get a Bibliographic record
 */

const fs = require('fs');
const yaml = require('js-yaml');
const https = require('https');
const axios = require("axios");
 
let configFile = fs.readFileSync(require('path').resolve(__dirname, '../config.yml')).toString();
global.config = yaml.load(configFile);
 
const credentials = {
  client: {
    id: config['key'],
    secret: config['secret']
  },
  auth: {
    tokenHost: config['host'],
    tokenPath: '/token'    
  }
};
 
const scopes = ["configPlatform refresh_token"];
 
const oauth2 = require('simple-oauth2').create(credentials);
const tokenConfig = {
  scope: scopes
};
 
async function getData(url, config){
    try {      
        let results = await axios.get(url, config);
        return results;
    } catch (error) {
        return error;
    }
}
 
async function getToken(){
     //Get the access token object for the client
		try {
			let httpOptions = {'Accept': 'application/json'};
	        let result = await oauth2.clientCredentials.getToken(tokenConfig, httpOptions);
	        try {
	        	let accessToken = await oauth2.accessToken.create(result);
	        	return accessToken;
	        } catch (error) {
	        	return error;
	        }
		} catch (error) {
			return error;
		}
}

async function getResponse(registryId){
	try {
		let token = await getToken();
		let url = config['registry_service_url'] + '/institution/data/' + registryId
		let agent = new https.Agent({  
  		  rejectUnauthorized: false
  		});
		let axios_config = {
	            headers: {
	                'Authorization': 'Bearer ' + token.token.access_token,
	                'User-Agent': 'node.js client',
	                'Accept': 'application/json'
	            },
	            httpsAgent: agent
	        };
		let result = await getData(url, axios_config);
		console.log(result.data.content.institution.nameLocation.institutionName);
		console.log(result.data.content.institution.wms.timezone);
	}catch (error) {
		console.log(error)
	}
}

getResponse('128807');
