# Create Message Queue Package Class
class QueuePackage:
    def __init__(self, sentTo: str, sentFrom: str, content: any):
        self.sentTo = sentTo
        self.sentFrom = sentFrom
        self.content = content

    def json(self):
        return {
            "sentFrom": self.sentFrom,
            "sentTo": self.sentTo,
            "content": self.content
        }