<?php
/* Using oauth2-client (https://github.com/thephpleague/oauth2-client) 
 * and making a request to WorldCat Metadata API to get a Bibliographic record */
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
    'urlAuthorize'            => 'https://oauth.oclc.org/auth',
    'urlAccessToken'          => 'https://oauth.oclc.org/token',
    'urlResourceOwnerDetails' => ''
];

$basicAuth_provider = new HttpBasicAuthOptionProvider();
$provider = new GenericProvider($setup_options, ['optionProvider' => $basicAuth_provider]);

try {
    
    // Try to get an access token using the client credentials grant.
    $accessToken = $provider->getAccessToken('client_credentials', ['scope' => 'wcapi']);
    
    $url = $config['discovery_service_url'] . "/bibs/1";
    $client = new Client();
    $headers = array();
    $headers['Authorization'] = "Bearer " . $accessToken->getToken();
    try {
        $response = $client->request('GET', $url, ['headers' => $headers]);
        $xml = $response->getBody();
        //print($xml);
        try {
            $jsonO = json_decode($xml);
            print($jsonO->identifier->oclcNumber);
        } catch (Exception $decodeError){
            print($decodeError);
        }
        
    } catch (RequestException $error) {
        print($error->getResponse()->getBody(true));
    }
} catch (\League\OAuth2\Client\Provider\Exception\IdentityProviderException $e) {
    echo "Failed to get access token";
}
