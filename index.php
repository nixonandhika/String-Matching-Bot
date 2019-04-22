<?php
require __DIR__ . '/vendor/autoload.php';

// load config
$dotenv = new Dotenv\Dotenv(__DIR__);
$dotenv->load();

// Slim app Initialization
$configs =  [
	'settings' => ['displayErrorDetails' => true],
];
$app = new Slim\App($configs);

//GET METHOD
$app->get('/', function ($request, $response) {
	return "Success";
});

//POST METHOD
$app->post('/', function ($request, $response)
{
	// get request body and LINE signature
	$body 	   = file_get_contents('php://input');

	// log body and signature
	file_put_contents('php://stderr', 'Body: '.$body);


	// Create bot client instance
	$httpClient = new \LINE\LINEBot\HTTPClient\CurlHTTPClient($_ENV['CHANNEL_ACCESS_TOKEN']);
	$bot = new \LINE\LINEBot($httpClient, ['channelSecret' => $_ENV['CHANNEL_SECRET']]);
	$data = json_decode($body, true);
	$reply = "";
	foreach ($data['events'] as $event)
	{
		$usermsg = $event['message']['text'];
		$usermsg = strtolower($usermsg);
		if($usermsg == "halo" || $usermsg == "hi" || $usermsg == "hello"){
			$reply = "Halo juga, aku Slothy!";
		} else{
			$exec_command = "cd engine && python string_matcher.py " . "\"" . $usermsg . "\"";
			$reply = exec($exec_command);
			$reply = str_replace('"', "", $reply);
		}
		$reply = str_replace("<BR>", "\n", $reply);
        $msgbuilder = new \LINE\LINEBot\MessageBuilder\TextMessageBuilder($reply);
		$res = $bot->replyMessage($event['replyToken'], $msgbuilder); //Call API
		return $res->getHTTPStatus() . ' ' . $res->getRawBody();
	}
});

$app->run();
