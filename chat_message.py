class ChatMessage:
    def __init__(self, sender, timestamp, content, sender_address):
        self.sender = sender
        self.timestamp = timestamp
        self.content = content
        self.sender_address = sender_address

    def __str__(self):
        return f"{self.sender} ({self.timestamp}) : {self.content} {self.sender_address}"