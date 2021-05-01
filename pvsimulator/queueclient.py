import amqpstorm
import threading
import time

from pvsimulator.exceptions import *

class QueueClient(object):
    """
    The QueueClient represents a Client, which connects to a single RabbitMQ queue.
    It can be used to publish and/or consume messages on this queue.
    """
    def __init__(
            self, 
            host = 'localhost', 
            username = 'guest', 
            password = 'guest', 
            queue_name = 'queue',
            consuming_timeout = 0.25
        ):
        """
        Params:
            host: The hostname of the RabbitMQ instance.
            username: The username, which will be used to login to the RabbitMQ instance.
            password: The password for the user.
            queue_name: The name of the queue, this Client will be connected to.
        """
        self._host = host
        self._queue_name = queue_name
        self._username = username
        self._password = password
        self.connected = False

        self._consuming = False
        self._should_consume = False
        self._consumer_thread = None
        self._consuming_timeout = consuming_timeout
        
    def connect(self):
        """
        Try to connect the client to its queue.

        Raises:
            PVConnectionError if the connection to the RabbitMQ instance failed.
            PVQueueConnectionError if the connection to the designated queue failed.
        """
        try:
            self._connection = amqpstorm.Connection(
                self._host,
                self._username,
                self._password
            )
        except amqpstorm.AMQPConnectionError as e:
            print(e)
            raise PVConnectionError(
                "Could not connect to RabbitMQ Service"
            )

        try:
            self._channel = self._connection.channel()
            self._channel.queue.declare(
                self._queue_name
            )
        except amqpstorm.AMQPConnectionError as e:
            print(e)
            raise PVQueueConnectionError(
                "Could not connect to Queue: ", self._queue_name
            )
        
        self.connected = True

        
    def publish_message(self, message_body):
        """
        Publish a message to the queue.

        Param:
            message_body: The message, that should be published as plain text.

        Raises:
            PVNotConnectedError if the Client is not connected properly.
            PVMessagePublishingError if the message could not be published.
        """
        if not self.connected:
            raise PVNotConnectedError(
                "Cannot publish message! Client is not connected!"
            )
        
        message = amqpstorm.Message.create(
            self._channel,
            message_body,
            properties = {
                'content_type': 'text/plain'
            }
        )
        try:
            message.publish(self._queue_name)
        except amqpstorm.exception.AMQPInvalidArgument as e:
            print(e)
            raise PVMessagePublishingError(
                "Could not publish message: '", message_body, "'!"
            )

    def purge_queue(self):
        """
        Delete all published messages in the queue.

        Raises:
            PVNotConnectedError if the Client is not connected properly.
        """
        if not self.connected:
            raise PVNotConnectedError(
                "The client is not properly connected to the RabbitMQ service!"
            )
        
        self._channel.queue.purge(self._queue_name)
    
    def start_consuming_blocking(self):
        """
        Start to consume messages while blocking the thread doing it.

        Raises:
            PVNotConnectedError if the Client is not connected properly.
        """
        if not self.connected:
            raise PVNotConnectedError(
                "The client is not properly connected to the RabbitMQ service!"
            )
        
        self._should_consume = True
        self._consume()

    def start_consuming_async(self):
        """
        Start to consume messages using a seperate worker thread.

        Raises:
            PVNotConnectedError if the Client is not connected properly.
            PVQueueClientAlreadyConsumingError if the Client is already consuming.
        """
        if not self.connected:
            raise PVNotConnectedError(
                "The client is not properly connected to the RabbitMQ service!"
            )

        if self._consuming:
            raise PVQueueClientAlreadyConsumingError(
                "Client is already consuming!"
            )
        
        if not self._consumer_thread:
            self._consumer_thread = threading.Thread(
                target = self._consume
            )
        
        self._should_consume = True
        self._consumer_thread.start()

    def stop_consuming_async(self):
        """
        Stops the consuming thread.

        Raises:
            PVQueueClientNotConsumingError if the Client is not consuming.
        """
        if not self._consuming:
            raise PVQueueClientNotConsumingError(
                "Client is not consuming!"
            )
            return False
        
        self._should_consume = False
        self._consumer_thread.join()
        return True
    
    def _consume(self):
        """
        Internal consuming implementation.
        Runs, while the value of self._should_consume is true.
        """
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
                time.sleep(self._consuming_timeout)
        self._consuming = False

    def _on_message_received_callback(self, message_body):
        """
        This method should be implemented by child-classes,
        that intend to consume messages.
        It gets called when a message was received.

        Param:
            message_body: The message, that was received. In plain text.
        """
        raise NotImplementedError(
            "_on_message_received_callback not implemented!"
        )
