import pika
import threading

class Receiver(object):
    def __init__(self, host, channel_name):
        self.host = host
        self.channel_name = channel_name
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                self.host
            )
        )
        self.channel = self.connection.channel()
        self.channel.queue_declare(self.channel_name)
        self.channel.basic_consume(
            queue = self.channel_name,
            auto_ack = True,
            on_message_callback = self.on_message_received_callback
        )
        self.consuming = False
        self.consumer_thread = threading.Thread(
            target = self.channel.start_consuming
        )
    
    def on_message_received_callback(self, ch, method, properties, body):
        print("callback received:")
        print("ch: ", ch)
        print("method: ", method)
        print("properties: ", properties)
        print("body: ", body)

    def start_consuming(self):
        self.consuming = True
        self.consumer_thread.start()
