from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

class ChatRoom(models.Model):
    """채팅방 모델"""
    name = models.CharField(max_length=100, unique=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    
    def __str__(self):
        return self.name

class Message(models.Model):
    """메시지 모델"""
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.content[:20]}"
    
    def clean(self):
        if not self.content:
            raise ValidationError('Content cannot be empty')
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
