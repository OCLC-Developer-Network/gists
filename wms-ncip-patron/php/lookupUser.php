<?php
// Using simple-oauth2 (https://github.com/lelylan/simple-oauth2) and making a request to WorldCat Metadata API to get a Bibliographic record
require_once('vendor/autoload.php');
use Symfony\Component\Yaml\Yaml;
use GuzzleHttp\Client;
use GuzzleHttp\Exception\RequestException;
use League\OAuth2\Client\OptionProvider\HttpBasicAuthOptionProvider;
use League\OAuth2\Client\Provider\GenericProvider;

$config = Yaml::parse(file_get_contents('../config.yml'));

$setup_options = [
    'clientId'                => $config['key'],
    'clientSecret'            => $config['secret'],
    'redirectUri'             => 'http://localhost:9090/',
    'urlAuthorize'            => 'https://oauth.oclc.org/auth',
    'urlAccessToken'          => 'https://oauth.oclc.org/token',
    'urlResourceOwnerDetails' => '',
    'scopes'            => 'WMS_NCIP refresh_token'
];

$basicAuth_provider = new HttpBasicAuthOptionProvider();
$provider = new GenericProvider($setup_options, ['optionProvider' => $basicAuth_provider]);

// If we don't have an authorization code then get one
if (!isset($_GET['code'])) {
    
    // Fetch the authorization URL from the provider; this returns the
    // urlAuthorize option and generates and applies any necessary parameters
    // (e.g. state).
    $authorizationUrl = $provider->getAuthorizationUrl();
    
    // Get the state generated for you and store it to the session.
    $_SESSION['oauth2state'] = $provider->getState();
    
    // Redirect the user to the authorization URL.
    header('Location: ' . $authorizationUrl);
    exit;
    
    // Check given state against previously stored one to mitigate CSRF attack
} elseif (empty($_GET['state']) || (isset($_SESSION['oauth2state']) && $_GET['state'] !== $_SESSION['oauth2state'])) {
    
    if (isset($_SESSION['oauth2state'])) {
        unset($_SESSION['oauth2state']);
    }
    
    print('Invalid state');
    
} else {
    
    try {
        $institutionId = $config['institutionId'];
        
        // Try to get an access token using the authorization code grant.
        $accessToken = $provider->getAccessToken('authorization_code', [
            'code' => $_GET['code']
        ]);
        
        $url =  "https://" . $institutionId . ".share.worldcat.org/ncip/circ-patron";
        $client = new Client();
        $headers = array();
        $headers['Authorization'] = "Bearer " . $accessToken->getToken();
        
        $ncipMessage = <<<XML
        <?xml version="1.0" encoding="UTF-8"?>
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
                       <AgencyId ncip:Scheme="http://oclc.org/ncip/schemes/agencyid.scm">$institutionId</AgencyId>
                   </FromAgencyId>
                   <ToAgencyId>
                       <AgencyId ncip:Scheme="http://oclc.org/ncip/schemes/agencyid.scm">$institutionId</AgencyId>
                   </ToAgencyId>
                   <ApplicationProfileType ncip:Scheme="http://oclc.org/ncip/schemes/application-profile/wcl.scm">Version 2011</ApplicationProfileType>
               </InitiationHeader>
               <UserId>
               		<UserIdentifierType ncip:Scheme="http://worldcat.org/ncip/schemes/v2/extensions/useridentifiertype.scm">EIDM</UserIdentifierType>
                   <UserIdentifierValue>foo</UserIdentifierValue>
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
		        </Ext>               
           </LookupUser>
       </NCIPMessage>        
        XML;    
        try {
            $response = $client->request('POST', $url, ['headers' => $headers, 'body' => $ncipMessage]);
            $xml = $response->getBody();
            print($xml);
        } catch (RequestException $error) {
            print_r($error);
        }
        
    } catch (\League\OAuth2\Client\Provider\Exception\IdentityProviderException $e) {
        
        // Failed to get the access token or user details.
        print($e->getMessage());
        
    }
    
}