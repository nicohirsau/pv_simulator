from pvsimulator.queueclient import QueueClient
from pvsimulator.simulations import configuration
import time

def test_connection():
    configuration.read_config_file("tests/test.conf")
    qc = QueueClient(
        host = configuration.CONFIGURATION['host'],
        username = configuration.CONFIGURATION['username'],
        password = configuration.CONFIGURATION['password'],
        queue_name = configuration.CONFIGURATION['queue_name']
    )
    qc.connect()
    assert qc.connected

def test_publishing():
    configuration.read_config_file("tests/test.conf")
    qc = QueueClient(
        host = configuration.CONFIGURATION['host'],
        username = configuration.CONFIGURATION['username'],
        password = configuration.CONFIGURATION['password'],
        queue_name = configuration.CONFIGURATION['queue_name']
    )
    qc.connect()
    # This raises an error if something goes wrong
    qc.publish_message("TEST")
    qc.purge_queue()

# The name cannot be TestConsumer because pytest
# would try to do stuff with it if it's name starts with Test
class ConsumerTest(QueueClient):
    message_received = False

    def _on_message_received_callback(self, message_body):
        self.message_received = (message_body == "TEST")

def test_consumption():
    configuration.read_config_file("tests/test.conf")
    qc = QueueClient(
        host = configuration.CONFIGURATION['host'],
        username = configuration.CONFIGURATION['username'],
        password = configuration.CONFIGURATION['password'],
        queue_name = configuration.CONFIGURATION['queue_name']
    )
    qc.connect()

    test_consumer = ConsumerTest(
        host = configuration.CONFIGURATION['host'],
        username = configuration.CONFIGURATION['username'],
        password = configuration.CONFIGURATION['password'],
        queue_name = configuration.CONFIGURATION['queue_name']
    )
    test_consumer.connect()

    # Purge the queue to have a clean state
    qc.purge_queue()
    qc.publish_message("TEST")

    test_consumer.start_consuming_async()
    time.sleep(1)
    test_consumer.stop_consuming()
    
    assert test_consumer.message_received
