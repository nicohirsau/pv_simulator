import amqpstorm

class Sender(object):
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
        
    def send_message(self, message_body):
        if not self.connected:
            print("Cannot send message! Sender is not connected!")
            return
        
        message = amqpstorm.Message.create(
            self._channel,
            message_body,
            properties = {
                'content_type': 'text/plain'
            }
        )
        message.publish(self._queue_name)
