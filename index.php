<?php
require __DIR__ . '/vendor/autoload.php';

use \LINE\LINEBot\SignatureValidator as SignatureValidator;

// load config
$dotenv = new Dotenv\Dotenv(__DIR__);
$dotenv->load();

// initiate app
$configs =  [
	'settings' => ['displayErrorDetails' => true],
];
$app = new Slim\App($configs);

/* ROUTES */
$app->get('/', function ($request, $response) {
	return "Success";
});

$app->post('/', function ($request, $response)
{
	// get request body and line signature header
	$body 	   = file_get_contents('php://input');
	$signature = $_SERVER['HTTP_X_LINE_SIGNATURE'];

	// log body and signature
	file_put_contents('php://stderr', 'Body: '.$body);

	// is LINE_SIGNATURE exists in request header?
	if (empty($signature)){
		return $response->withStatus(400, 'Signature not set');
	}

	// is this request comes from LINE?
	if($_ENV['PASS_SIGNATURE'] == false && ! SignatureValidator::validateSignature($body, $_ENV['CHANNEL_SECRET'], $signature)){
		return $response->withStatus(400, 'Invalid signature');
	}

	// init bot
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
		$res = $bot->replyMessage($event['replyToken'], $msgbuilder);
		return $res->getHTTPStatus() . ' ' . $res->getRawBody();
	}
});

$app->run();
