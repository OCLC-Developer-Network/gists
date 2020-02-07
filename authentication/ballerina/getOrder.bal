// ###############################################################################
// Copyright 2020 OCLC
//
// Licensed under the Apache License, Version 2.0 (the "License"); you may not
// use this file except in compliance with the License. You may obtain a copy of
// the License at
//
// http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
// ###############################################################################


// Setup internal Ballerina imports. No external libraries needed.
import ballerina/http;
import ballerina/log;
import ballerina/oauth2;
import ballerina/crypto;

// Define the PurchaseOrder namespace to use in example number 1 later.
xmlns "http://worldcat.org/xmlschemas/acquisitions/PurchaseOrder" as nsPO;

// Ballerina DOC
# Oauth2 authentication example using the Ballerina.io integration language
# Retrieve and parse purchaseOrder XML from the OCLC WMS Acquisitions API

// Set up WSkey/Secret/DataCenter
string wskey = "YOUR_WSKEY";//TODO
string secret = "YOUR_SECRET";//TODO
string scope="WMS_ACQ";

//sd01 for public sandbox and the Americas, sd02 for EMEA
string dataCenter = "sd01";//TODO

// Add default Ballerina Truststore for TLS connections
// If BALLERINA_HOME is not set in your environment replace ${ballerina.home} 
// with the correct path.
crypto:KeyStore keyStore = {path: "${ballerina.home}/bre/security/ballerinaTruststore.p12", password: "ballerina"};

// Set up OAuth2 provider and handler for WorldShare Platform
oauth2:OutboundOAuth2Provider oauth2Provider = new({
    tokenUrl: "https://oauth.oclc.org/token?grant_type=client_credentials&scope=" + scope,
    clientId: wskey,
    clientSecret: secret,
    clientConfig: {
        secureSocket: {
            trustStore: keyStore
        }
    }
});

http:BearerAuthHandler oauth2Handler = new(oauth2Provider);

//Define WMS Acquisitions API EndPoint
http:Client clientEP = new("https://acq." + dataCenter  + ".worldcat.org", {
    auth: {
        authHandler: oauth2Handler
    },
    secureSocket: {
        trustStore: keyStore
    }
});

function getOrder(string orderNumber) {

    // GET purchaseOrder data from WMS Acquisitions API
    http:Request req =new;
    req.addHeader("Accept", "application/xml");
    var response = clientEP->get("/purchaseorders/" + orderNumber, req);
    if (response is http:Response) {
        var purchaseOrder = response.getXmlPayload();
        if (purchaseOrder is xml) {

        // Log full order XML
        log:printInfo(purchaseOrder.toString());

        //Example 1: Use PurchaseOrder namespace as defined above to select XML element
        log:printInfo("orderName is: " + purchaseOrder[nsPO:orderName].getTextValue());

        //Example 2: Select XML element without using pre-defined namespace
        log:printInfo("Vendor is: " + purchaseOrder.vendor.vendorName.getTextValue());

        } else {
            log:printError("Failed to retrieve payload from endpoint: " + "https://acq." + dataCenter  + ".worldcat.org");
            log:printError(purchaseOrder.toString());
            }
    } else {
        log:printError("Failed to call the endpoint: ", response);
        }
    }

public function main() {

    // Example orderID PO-2012-36 is an existing order in the public Sandbox
    getOrder("PO-2012-36");//TODO
    }
