from django.db import models

from metamiejskie.users.models import User


# Create your models here.


class Chat(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name="chats")
    context = models.JSONField(default=list)
