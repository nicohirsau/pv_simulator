import pika

class Sender(object):
    def __init__(self, host, channel_name, clear_queue = True):
        self.host = host
        self.channel_name = channel_name
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                self.host
            )
        )
        self.channel = self.connection.channel()
        if clear_queue:
            self.channel.queue_delete(self.channel_name)
        self.channel.queue_declare(self.channel_name)
    
    def send_message(self, message):
        self.channel.basic_publish(
            exchange = '',
            routing_key = self.channel_name,
            body = message
        )
