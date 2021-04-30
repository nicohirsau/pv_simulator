import amqpstorm
import threading
import time

class Receiver(object):
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
        except amqpstorm.exception.AMQPConnectionError as exception:
            print("Could not connect to rabbitMQ!")
            self.connected = False
    
    def _on_message_received_callback(self, message_body):
        print("callback received:")
        print(message_body)

    def start_consuming_async(self):
        if not self.connected:
            print("Can't start consuming if not connected!")
            return
        
        if not self._consumer_thread:
            self._consumer_thread = threading.Thread(
                target = self._consume
            )
        self._consuming = True
        self._consumer_thread.start()
    
    def start_consuming_blocking(self):
        if not self.connected:
            print("Can't start consuming if not connected!")
            return
        
        self._consuming = True
        self._consume()

    def stop_consuming(self):
        if not self._consuming:
            return
        
        self._consuming = False
        self._consumer_thread.join()
    
    def _consume(self):
        while self._consuming:
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
