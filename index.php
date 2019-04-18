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
	$count = 0;
	$reply = "";
	foreach ($data['events'] as $event)
	{
		$userMessage = $event['message']['text'];
		$userMessage = "\"" . strtolower($userMessage) . "\"";
		$temp = "\"" . "halo" . "\"";
		if($userMessage == temp){
			$reply = "Halo hi";
		} else{
			if($count > 1){
				if($userMessage == "1"){
					echo $reply_split[0];
					$reply = exec("cd engine && python string_matcher.py " . "\"" . $reply_split[0]) . "\"";
				} else if($userMessage == "2"){
					echo $reply_split[1];
					$reply = exec("cd engine && python string_matcher.py " . "\"" . $reply_split[1]) . "\"";
				} else if($userMessage == "3"){
					echo $reply_split[2];
					$reply = exec("cd engine && python string_matcher.py " . "\"" . $reply_split[2]) . "\"";
				} else{
					$reply = exec("cd engine && python string_matcher.py ?");
				}
				$reply_split = explode("<BR>", $reply);
				$count = 0;
			} else{
				$exec_command = "cd engine && python string_matcher.py " . $userMessage;
				$reply = exec($exec_command);
				$reply_split = explode("<BR>", $reply);
				foreach($reply_split as $piece){
					$count++;
				}
				if($count == 1){
					$count = 0;
				}
			}
		}
    $textMessageBuilder = new \LINE\LINEBot\MessageBuilder\TextMessageBuilder($reply);
		$result = $bot->replyMessage($event['replyToken'], $textMessageBuilder);
		return $result->getHTTPStatus() . ' ' . $result->getRawBody();
	}
});

$app->run();
