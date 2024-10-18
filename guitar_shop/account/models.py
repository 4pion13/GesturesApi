from django.db import models




class UserCustom(models.Model):
    login = models.CharField(max_length=1000, blank=True)
    password = models.CharField(max_length=1000, blank=True)