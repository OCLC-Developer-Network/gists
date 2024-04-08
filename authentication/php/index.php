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
    'scopes'            => 'WorldCatMetadataAPI refresh_token'
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
        
        // Try to get an access token using the authorization code grant.
        $accessToken = $provider->getAccessToken('authorization_code', [
            'code' => $_GET['code']
        ]);
        
        $url = $config['metadata_service_url'] . "/manage/bibs/1";
        $client = new Client();
        $headers = array();
        $headers['Authorization'] = "Bearer " . $accessToken->getToken();
        try {
            $response = $client->request('GET', $url, ['headers' => $headers]);
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