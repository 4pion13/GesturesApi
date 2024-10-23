from django.db import models
from django.contrib.auth.models import User

class Guitars(models.Model):
    product_id = models.CharField(max_length=1000, blank=True)
    name = models.CharField(max_length=1000, blank=True)
    img = models.CharField(max_length=1000, blank=True)
    price = models.CharField(max_length=100, blank=True)


class Video(models.Model):
    file = models.FileField(upload_to='videos/')


class ChatHistory(models.Model):
    name = models.CharField(max_length=1000, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)


class ChatHistoryData(models.Model):
    chat = models.ForeignKey(ChatHistory, on_delete=models.CASCADE)
    request = models.ForeignKey(Video, on_delete=models.CASCADE)
    anser = models.CharField(max_length=1000, blank=True)
    save_date = models.DateField(auto_now_add=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
