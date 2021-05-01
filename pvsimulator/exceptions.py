class PVConnectionError(Exception):
    """
    Is used to indicate, that the Connection to the
    designated RabbitMQ instance failed.
    """
    pass

class PVQueueConnectionError(Exception):
    """
    Is used to indicate, that the Connection to the
    designated RabbitMQ queue failed.
    """
    pass

class PVNotConnectedError(Exception):
    """
    Is used to indicate, that a QueueClient is not
    properly connected to the RabbitMQ instance.
    """
    pass

class PVMessagePublishingError(Exception):
    """
    Is raised, when a message could not be published.
    """
    pass

class PVQueueClientNotConsumingError(Exception):
    """
    Is raised, when a QueueClient, that is currently
    not consuming messages is tasked to stop consuming.
    """
    pass

class PVQueueClientAlreadyConsumingError(Exception):
    """
    Is raised, when a QueueClient, that is currently
    consuming messages is tasked to start consuming.
    """
    pass
