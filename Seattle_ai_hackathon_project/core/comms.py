"""
Communication system for the Smart Traffic Management System
Implements a simple in-memory message bus with publish-subscribe pattern
"""
from collections import defaultdict, deque


class MessageBus:
    def __init__(self, max_history=100):
        """
        Initialize a simple message bus
        
        Args:
            max_history: Maximum number of messages to keep per topic
        """
        self.subscribers = defaultdict(list)
        self.messages = defaultdict(lambda: deque(maxlen=max_history))
    
    def publish(self, topic, message):
        """
        Publish a message to a topic
        
        Args:
            topic: Topic to publish to
            message: Message payload (any serializable object)
        """
        # Store the message
        self.messages[topic].append(message)
        
        # Notify subscribers
        for callback in self.subscribers[topic]:
            callback(message)
    
    def subscribe(self, topic, callback):
        """
        Subscribe to a topic with a callback
        
        Args:
            topic: Topic to subscribe to
            callback: Function to call when a message is published to the topic
        
        Returns:
            Subscription ID
        """
        self.subscribers[topic].append(callback)
        return len(self.subscribers[topic]) - 1
    
    def unsubscribe(self, topic, subscription_id):
        """
        Unsubscribe from a topic
        
        Args:
            topic: Topic to unsubscribe from
            subscription_id: Subscription ID
        """
        if topic in self.subscribers and subscription_id < len(self.subscribers[topic]):
            self.subscribers[topic].pop(subscription_id)
    
    def get_messages(self, topic, count=None):
        """
        Get recent messages from a topic
        
        Args:
            topic: Topic to get messages from
            count: Number of messages to retrieve (None for all)
        
        Returns:
            List of messages
        """
        if topic not in self.messages:
            return []
        
        messages = list(self.messages[topic])
        if count is not None:
            messages = messages[-count:]
        
        return messages
    
    def clear(self):
        """Clear all message queues"""
        for topic in self.messages:
            self.messages[topic].clear()
    
    def get_topic_list(self):
        """Get a list of all topics with messages"""
        return list(self.messages.keys())