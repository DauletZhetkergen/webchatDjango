from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import User
from django.db import models


# Create your models here.


from django.db import models
from django.contrib.auth.models import User

class Chat(models.Model):
    name = models.CharField(max_length=255)  # Название чата (например, идентификатор или название)
    participants = models.ManyToManyField(User, related_name='chats')  # Пользователи, участвующие в чате

    def __str__(self):
        return self.name

class ChatMessage(models.Model):
    chat = models.ForeignKey(Chat, related_name='messages', on_delete=models.CASCADE)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username}: {self.message[:10]}...'

    class Meta:
        ordering = ['created_at']
