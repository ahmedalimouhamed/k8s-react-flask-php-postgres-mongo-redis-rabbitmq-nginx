<?php
require_once __DIR__ . '/../vendor/autoload.php';

use PhpAmqpLib\Connection\AMQPStreamConnection;

echo "Waiting for RabbitMQ to be ready...\n";
sleep(15);

class NotificationService {
    private $rabbitmq;

    public function __construct() {
        $this->rabbitmq = new AMQPStreamConnection(
            'rabbitmq', 5672, 'guest', 'guest'
        );
    }

    public function listen() {
        $channel = $this->rabbitmq->channel();
        $channel->queue_declare('order_created', false, true, false, false);

        echo "[*] Waiting for messages. To exit press CTRL+C\n";

        $callback = function($msg) {
            echo " [X] Received " . $msg->body . "\n";
            $data = json_decode($msg->body, true);
            $this->processOrderNotification($data);
        };

        $channel->basic_consume('order_created', '', false, true, false, false, $callback);

        while($channel->is_consuming()) {
            $channel->wait();
        }
    }

    private function processOrderNotification($data) {
        $orderId = $data['order_id'];
        $userId = $data['user_id'];

        error_log("Processing notification for order: $orderId, user: $userId");
        
        file_put_contents(
            '/app/logs/notifications.log', 
            date('Y-m-d H:i:s') . " - Order #$orderId by user $userId\n",
            FILE_APPEND
        );
        
        echo "✅ Processed order #$orderId from user $userId\n";
    }
}

$service = new NotificationService();
$service->listen();