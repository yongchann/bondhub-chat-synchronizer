class Chat:
    def __init__(self, sender, chat_date_time, content, sender_address):
        self.sender = sender
        self.chat_date_time = chat_date_time
        self.content = content
        self.sender_address = sender_address

    def __str__(self):
        return f"{self.sender} ({self.chat_date_time}) : {self.content} {self.sender_address}"