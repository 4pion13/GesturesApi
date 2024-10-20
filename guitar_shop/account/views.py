from django.shortcuts import render
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from . import serializers
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

class RegistrationAPIView(APIView):

    def post(self, request):
        data = request.data
        email = data.get('email', None)
        password = data.get('password', None)
        username = data.get('username', None)
        print(email, username)
        email_existing_one = User.objects.filter(email = email)
        if email_existing_one:
            return Response({'error': 'Пользователь с таким email уже зарегестрирован'},
                            status=status.HTTP_401_UNAUTHORIZED)
        
        username_existing_one = User.objects.filter(username = username)
        if username_existing_one:
            return Response({'error': 'Пользователь с таким логином уже зарегестрирован'},
                            status=status.HTTP_401_UNAUTHORIZED)
        
        serializer = serializers.CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.set_password(password)  # Шифруем пароль
            user.save()         
            refresh = RefreshToken.for_user(user) # Создание Refesh и Access
            refresh.payload.update({    # Полезная информация в самом токене
                'user_id': user.id,
                'username': user.username
            })
            send_mail(
                'Test Subject',
                f'Ваши данные от аккаунта:\nПароль: {password}\nЛогин:{username}',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token), # Отправка на клиент
            }, status=status.HTTP_201_CREATED)





class LoginAPIView(APIView):
    def post(self, request):
        data = request.data
        email = data.get('email', None)
        password = data.get('password', None)
        print(data)
        if email is None or password is None:
            return Response({'error': 'Нужен и логин, и пароль'},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            user_id = User.objects.get(email=email)
            print('USERID- ',user_id)
        except:
            return Response({'error': 'Пользователя с таким Email не существует'},
                            status=status.HTTP_401_UNAUTHORIZED)
        
        user = authenticate(username=user_id.username, password=password)
        print(user)
        if user is None:
            return Response({'error': 'Неверный пароль'},
                            status=status.HTTP_401_UNAUTHORIZED)

        refresh = RefreshToken.for_user(user)

        refresh.payload.update({
            'user_id': user.id,
            'username': user.username
        })

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),

        }, status=status.HTTP_200_OK)






class LogoutAPIView(APIView):
    def post(self, request):
        refresh_token = request.data.get('refresh_token') # С клиента нужно отправить refresh token
        if not refresh_token:
            return Response({'error': 'Необходим Refresh token'},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            token = RefreshToken(refresh_token)
            token.blacklist() # Добавить его в чёрный список
        except Exception as e:
            return Response({'error': 'Неверный Refresh token'},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response({'success': 'Выход успешен'}, status=status.HTTP_200_OK)