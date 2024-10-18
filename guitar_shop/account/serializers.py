
from rest_framework import serializers
from .models import UserCustom
from django.contrib.auth.models import User



class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'password','username']