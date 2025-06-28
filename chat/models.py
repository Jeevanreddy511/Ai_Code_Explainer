from django.db import models # type: ignore


class Chat(models.Model):
    code = models.TextField()
    tree = models.TextField()
    name = models.CharField(max_length=20)
    time = models.DateTimeField(auto_now=True) 

    def add_message(self, query, reply):
        Message.objects.create(query=query, reply=reply, chat=self)
        self.save()
    
    def update(self, code, tree):
        self.code = code
        self.tree = tree
        # print(self.code)
        self.save()
    
    def get_messages(self):
        return (self.code, self.tree ,self.messages.all())
    
    def __str__(self):
        return f"Chat {self.id}"


class Message(models.Model):
    query = models.TextField()
    reply = models.TextField()

    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="messages")

    def get_qanda(self):
        return {
            'query': self.query,
            'reply': self.reply
        }

    def __str__(self):
        return f"Query: {self.query} | Bot: {self.reply}"

class NameGenerator(models.Model):
    generator = models.PositiveIntegerField()

    def generate(self):
        self.generator += 1
        self.save()
        return "Chat " + str(self.generator)