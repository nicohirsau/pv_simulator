import amqpstorm
import threading
import time

class QueueClient(object):
    def __init__(
            self, 
            host = 'localhost', 
            username = 'guest', 
            password = 'guest', 
            queue_name = 'queue'
        ):
        self._host = host
        self._queue_name = queue_name
        self._username = username
        self._password = password
        self.connected = False


        self._consuming = False
        self._should_consume = False
        self._consumer_thread = None
        
    def connect(self):
        try:
            self._connection = amqpstorm.Connection(
                self._host,
                self._username,
                self._password
            )
            self._channel = self._connection.channel()
            self._channel.queue.declare(
                self._queue_name
            )
            self.connected = True
            return True
        except amqpstorm.exception.AMQPConnectionError as exception:
            print("Could not connect to rabbitMQ!")
            self.connected = False
            return False
        except amqpstorm.exception.AMQPInvalidArgument:
            print("Could setup the channel!")
            self.connected = False
            return False
        
    def send_message(self, message_body):
        if not self.connected:
            print("Cannot send message! Sender is not connected!")
            return False
        
        message = amqpstorm.Message.create(
            self._channel,
            message_body,
            properties = {
                'content_type': 'text/plain'
            }
        )
        try:
            message.publish(self._queue_name)
            return True
        except amqpstorm.exception.AMQPInvalidArgument:
            print("Could not send message: '", message_body, "'!")
            return False

    def purge_queue(self):
        if not self.connected:
            print("Not connected to a queue! Cannot purge it!")
            return False
        
        self._channel.queue.purge(self._queue_name)
        return True
    
    def start_consuming_blocking(self):
        if not self.connected:
            print("Can't start consuming if not connected!")
            return False
        
        self._should_consume = True
        self._consume()
        return True

    def start_consuming_async(self):
        if not self.connected:
            print("Can't start consuming if not connected!")
            return False
        
        if not self._consumer_thread:
            self._consumer_thread = threading.Thread(
                target = self._consume
            )

        if self._consumer_thread.is_alive():
            print("Client is already consuming!")
            return False
        
        self._should_consume = True
        self._consumer_thread.start()
        return True

    def stop_consuming_async(self):
        if not self._consuming:
            print("Client is not consuming!")
            return False
        
        self._should_consume = False
        self._consumer_thread.join()
        return True
    
    def _consume(self):
        self._consuming = True
        while self._should_consume:
            result = self._channel.basic.get(
                queue = self._queue_name, 
                no_ack = False
            )
            if result:
                self._on_message_received_callback(
                    result.body
                )
                self._channel.basic.ack(
                    result.method['delivery_tag']
                )
                time.sleep(0.25)
        self._consuming = False

    def _on_message_received_callback(self, message_body):
        raise NotImplementedError(
            "_on_message_received_callback not implemented!"
        )
