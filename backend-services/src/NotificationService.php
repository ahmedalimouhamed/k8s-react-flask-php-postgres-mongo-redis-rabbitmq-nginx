<?php
require_once __DIR__ .'/../vendor/autoload.php';

use PhpAmqpLib\Connection\AMQPStreamConnection;
use PhpAmqpLib\Message\AMQPMessage;

class NotificationService{
    private $rabbitmq;

    public function __construct(){
        $this->rabbitmq = new AMQPStreamConnection(
            'localhost', 5672, 'guest', 'guest'
        );
    }

    public function listen(){
        $channel = $this->rabbitmq->channel();
        $channel->queue_declare('order_created', false, true, false, false);

        echo "[*] Waiting for messages. To exit press CTRL+C\n";

        $callback = function($msg){
            echo " [X] Received ", $msg->bdy, "\n";
            $data = json_decode($msg->body, true);
            $this->processOrderNotification($data);
        };

        $channel->basic_consume('order_created', '', false, true, false, false, $callback);

        while($channel->is_consuming()){
            $channel->wait();
        }
    }

    private function processOrderNotification($data){
        $orderId = $data['order_id'];
        $userId = $data['user_id'];

        error_log("processing notification for order: $orderId, user: $userId");
        mail('admin@example.com', "New Order #$orderId", "User $userId placed a new order");
    }
}

$service = new NotificationService();
$service->listen();