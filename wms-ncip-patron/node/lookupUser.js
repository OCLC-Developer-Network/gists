const fs = require('fs');
const yaml = require('js-yaml');
const https = require('https');
const axios = require("axios");
 
let configFile = fs.readFileSync(require('path').resolve(__dirname, './config.yml')).toString();
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
 
const scopes = ["WMS_NCIP refresh_token"];
 
const oauth2 = require('simple-oauth2').create(credentials);
const tokenConfig = {
  scope: scopes
};
 
async function getData(url, data, config){
    try {      
        let results = await axios.post(url, data, config);
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

async function getResponse(principalID, principalIDNS, institutionId){
	try {
		let token = await getToken();

		let url = "https://" + institutionId + ".share.worldcat.org/ncip/circ-patron?principalID=" + principalID + "&principalIDNS=" + principalIDNS;

		let data = `<?xml version="1.0" encoding="UTF-8"?>
       <NCIPMessage
           xmlns="http://www.niso.org/2008/ncip"
           xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
           xmlns:ncip="http://www.niso.org/2008/ncip"
           xmlns:ns2="http://oclc.org/WCL/ncip/2011/extensions"
           xsi:schemaLocation="http://www.niso.org/2008/ncip http://www.niso.org/schemas/ncip/v2_01/ncip_v2_01.xsd"
           ncip:version="http://www.niso.org/schemas/ncip/v2_01/ncip_v2_01.xsd">
           <LookupUser>
               <InitiationHeader>
                   <FromAgencyId>
                       <AgencyId ncip:Scheme="http://oclc.org/ncip/schemes/agencyid.scm">${institutionId}</AgencyId>
                   </FromAgencyId>
                   <ToAgencyId>
                       <AgencyId ncip:Scheme="http://oclc.org/ncip/schemes/agencyid.scm">${institutionId}</AgencyId>
                   </ToAgencyId>
                   <ApplicationProfileType ncip:Scheme="http://oclc.org/ncip/schemes/application-profile/wcl.scm">Version 2011</ApplicationProfileType>
               </InitiationHeader>
               <UserId>
               		<UserIdentifierType ncip:Scheme="http://worldcat.org/ncip/schemes/v2/extensions/useridentifiertype.scm">EIDM</UserIdentifierType>
                   <UserIdentifierValue>${principalID}</UserIdentifierValue>
               </UserId>
               <LoanedItemsDesired/>
               <RequestedItemsDesired/>
               <UserFiscalAccountDesired/>
		        <Ext>
		            <ns2:ResponseElementControl>
		                <ns2:ElementType ncip:Scheme="http://worldcat.org/ncip/schemes/v2/extensions/elementtype.scm">Account Details</ns2:ElementType>
		                <ns2:StartElement> 1</ns2:StartElement>
		                <ns2:MaximumCount>10</ns2:MaximumCount>
		                <ns2:SortField ncip:Scheme="http://worldcat.org/ncip/schemes/v2/extensions/accountdetailselementtype.scm">Accrual Date</ns2:SortField>
		                <ns2:SortOrderType ncip:Scheme="http://worldcat.org/ncip/schemes/v2/extensions/sortordertype.scm">Ascending</ns2:SortOrderType>
		            </ns2:ResponseElementControl>
		            <ns2:ResponseElementControl>
		                <ns2:ElementType ncip:Scheme="http://worldcat.org/ncip/schemes/v2/extensions/elementtype.scm">Loaned Item</ns2:ElementType>
		                <ns2:StartElement>1</ns2:StartElement>
		                <ns2:MaximumCount>10</ns2:MaximumCount>
		                <ns2:SortField ncip:Scheme="http://worldcat.org/ncip/schemes/v2/extensions/loaneditemelementtype.scm">Date Due</ns2:SortField>
		                <ns2:SortOrderType ncip:Scheme="http://worldcat.org/ncip/schemes/v2/extensions/sortordertype.scm">Ascending</ns2:SortOrderType>
		            </ns2:ResponseElementControl>
		            <ns2:ResponseElementControl>
		                <ns2:ElementType ncip:Scheme="http://worldcat.org/ncip/schemes/v2/extensions/elementtype.scm">Requested Item</ns2:ElementType>
		                <ns2:StartElement>1</ns2:StartElement>
		                <ns2:MaximumCount>10</ns2:MaximumCount>
		                <ns2:SortField ncip:Scheme="http://worldcat.org/ncip/schemes/v2/extensions/requesteditemelementtype.scm">Date Placed</ns2:SortField>
		                <ns2:SortOrderType ncip:Scheme="http://worldcat.org/ncip/schemes/v2/extensions/sortordertype.scm">Ascending</ns2:SortOrderType>
		            </ns2:ResponseElementControl>		        
		            <ns2:relyingPartyId>${principalIDNS}</ns2:relyingPartyId>
		        </Ext>               
           </LookupUser>
       </NCIPMessage>`;				
		
		let agent = new https.Agent({  
  		  rejectUnauthorized: false
  		});
		let axios_config = {
	            headers: {
	                'Authorization': 'Bearer ' + token.token.access_token,
	                'User-Agent': 'node.js KAC client',
	                'Content-Type': 'application/xml',
	                'Accept': 'application/xml'
	            },
	            httpsAgent: agent
	        };
		let result = await getData(url, data, axios_config);
		console.log(result.data);
	}catch (error) {
		console.log(error)
	}
}

getResponse("6eceaa02-fc78-4384-8411-6d7a0ab702cf", "urn:oclc:platform:128807", 128807);