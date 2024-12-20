from django.shortcuts import render
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from . import serializers
from django.contrib.auth.models import User
from .models import Guitars, Video, ChatHistory, ChatHistoryData, ReportData
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import api_view
from rest_framework.views import APIView
import sys
import onnxruntime as ort
sys.path.append("../")
import numpy as np
import cv2
from PIL import Image
from .constants import classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import AccessToken




class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer


class UserDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer

class GuitarList(generics.ListAPIView):
    queryset = Guitars.objects.all()
    serializer_class = serializers.GuitarSerializer



from .models import Video
from rest_framework_simplejwt.authentication import JWTAuthentication
JWT_authenticator = JWTAuthentication()
class VideoUploadView(generics.CreateAPIView):
    #permission_classes = [IsAuthenticated]
    queryset = Video.objects.all()
    serializer_class = serializers.VideoSerializer
    def create(self, request, *args, **kwargs):
        res = JWT_authenticator.authenticate(request)
        if res:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            video = serializer.save()
            file_url = request.build_absolute_uri(video.file.url)
            file_id = Video.objects.get(file=video.file)
            return Response({'file_url': file_url, 'file_id':file_id.id}, status=status.HTTP_201_CREATED)
    

from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, renderer_classes


# Тестовый запрос
@api_view(['GET'])
def get_test(request):
    print('Данные', request.data)
    report_data = ReportData.objects.all()
    print(report_data)
    serializer = serializers.ReportData(report_data, many=True)
    return Response({'chat_history': serializer.data}, status=status.HTTP_200_OK)

@api_view(['POST'])
def post_test(request):
    try:
        data = request.data  # Получаем JSON-данные как словарь Python
        # name = data.get("Имя")
        # age = data.get("Возраст")
        print(data)
        print(data[0].get("id"))
        report_data_update = ReportData.objects.get(id=data[0].get("id"))
        report_data_update.status = data[0].get("Статус")
        report_data_update.comment = data[0].get("Комментарий")
        report_data_update.save()
    except:
        print('Не сработало')
        return Response({'message': 'Не сработало'}, status=status.HTTP_306_RESERVED)
    return Response({'message': 'Сработало'}, status=status.HTTP_200_OK)


@api_view(['POST'])
def get_report_data(request):
    response = JWT_authenticator.authenticate(request)
    print(response)
    if response:
        try:
            token = response[1]['user_id']
            user = User.objects.get(id = token)
            data = request.data  # Получаем JSON-данные как словарь Python
            print(data.get('answerId'), data.get('message'))
            chat_report_data_model = ReportData(message=data.get('message'), answer=ChatHistoryData.objects.get(id=data.get('answerId')), owner_name=user.username, owner=user, status=False, answer_text=ChatHistoryData.objects.get(id=data.get('answerId')).anser)
            chat_report_data_model.save()
        except:
            print('Не сработало')
            return Response({'message': 'Ошибка отправки'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': 'Репорт отправлен'}, status=status.HTTP_200_OK)



@api_view(['GET'])
def get_chat_history(request):
    print(request)
    response = JWT_authenticator.authenticate(request)
    print(response)
    if response:
        token = response[1]['user_id']
        user = User.objects.get(id = token)
        chat_history = ChatHistory.objects.filter(owner=user)
        serializer = serializers.ChatSerializer(chat_history, many=True)
        return Response({'chat_history': serializer.data}, status=status.HTTP_200_OK)
    
@api_view(['GET'])
def get_chat_report(request):
    print(request)
    response = JWT_authenticator.authenticate(request)
    print(response)
    if response:
        token = response[1]['user_id']
        user = User.objects.get(id = token)
        chat_report = ReportData.objects.filter(owner=user)
        serializer = serializers.ReportData(chat_report, many=True)
        return Response({'chat_report': serializer.data}, status=status.HTTP_200_OK)

@api_view(['POST'])
def get_chat_data(request):
    response = JWT_authenticator.authenticate(request)
    print(response)
    if response:
        token = response[1]['user_id']
        user = User.objects.get(id = token)
        chat_data = ChatHistoryData.objects.filter(chat=ChatHistory.objects.get(id=request.data.get('id'), owner=user))
        data_list = []
        for item in chat_data:
            file_name_item = item.request.file
            element = {
                "id": f'{item.id}',
                "request": f'http://localhost:8000/media/{file_name_item}',
                "anser": f'{item.anser}',
                "date": f'{item.save_date}',
            }
            data_list.append(element)
        print(data_list)
        if chat_data:
            print(chat_data)
            return Response({'chat_data': data_list}, status=status.HTTP_200_OK)
        else:
            print('Записи не найдены!')
            return Response({'chat_data': False}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def create_chat(request):
    response = JWT_authenticator.authenticate(request)
    print(response)
    if response:
        chat_name = request.data.get('data')
        print('Сработало-', chat_name)
        token = response[1]['user_id']
        user = User.objects.get(id = token)
        chat_history = ChatHistory(name=chat_name, owner=user)
        chat_history.save()
        return Response({'message': f'Чат с названием - {chat_name} создан!'}, status=status.HTTP_200_OK)



@api_view(['POST'])
def delete_chat(request):
    response = JWT_authenticator.authenticate(request)
    print(response)
    if response:
        token = response[1]['user_id']
        user = User.objects.get(id = token)
        chat_id = request.data.get('id')
        chat_history = ChatHistory.objects.get(id = chat_id, owner=user)
        chat_history.delete()
        print('Сработало-', chat_id)
        return Response({'message': f'Чат с id - {chat_id} удален!'}, status=status.HTTP_200_OK)


from django.conf import settings
@api_view(['POST'])
def video_process(request):
    response = JWT_authenticator.authenticate(request)
    print(response)
    if response:
        token = response[1]['user_id']
        user = User.objects.get(id = token)
        number = request.data.get('id')
        print(number, request.data.get('chatId'))
        video_path = Video.objects.get(id=number)
        if isinstance(number, (int, float)):
            path_to_model = "../mvit32-2.onnx"
            path_to_input_video = f'{settings.MEDIA_ROOT}\{video_path.file}'
            #path_to_input_video = r'R:\Projects\Rest-Django\guitar_shop\media\videos\f17a6060-6ced-4bd1-9886-8578cfbb864f_1_FTA6zUZ.mp4'
            path_to_output_video = "output_onnx.mp4"
            session = ort.InferenceSession(path_to_model)
            input_name = session.get_inputs()[0].name
            input_shape = session.get_inputs()[0].shape
            window_size = input_shape[3]
            output_names = [output.name for output in session.get_outputs()]

            threshold = 0.1
            frame_interval = 2
            mean = [123.675, 116.28, 103.53]
            std = [58.395, 57.12, 57.375]
            def resize(im, new_shape=(224, 224)):
                shape = im.shape[:2]  # current shape [height, width]
                if isinstance(new_shape, int):
                    new_shape = (new_shape, new_shape)

                # Scale ratio (new / old)
                r = min(new_shape[0] / shape[0], new_shape[1] / shape[1])

                # Compute padding
                new_unpad = int(round(shape[1] * r)), int(round(shape[0] * r))
                dw, dh = new_shape[1] - new_unpad[0], new_shape[0] - new_unpad[1]  # wh padding

                dw /= 2
                dh /= 2

                if shape[::-1] != new_unpad:  # resize
                    im = cv2.resize(im, new_unpad, interpolation=cv2.INTER_LINEAR)
                top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
                left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
                im = cv2.copyMakeBorder(im, top, bottom, left, right, cv2.BORDER_CONSTANT, value=(114, 114, 114))  # add border
                return im
            
            cap = cv2.VideoCapture(path_to_input_video)
            _,frame = cap.read()
            shape = frame.shape
            fourcc = cv2.VideoWriter_fourcc(*'H264')
            writer = cv2.VideoWriter(path_to_output_video, fourcc, 30, (frame.shape[1], frame.shape[0]+50))

            tensors_list = []
            prediction_list = []
            prediction_list.append("---")

            frame_counter = 0
            while True:
                _, frame = cap.read()
                if frame is None:
                    break
                frame_counter += 1
                if frame_counter == frame_interval:
                    image = cv2.cvtColor(frame.copy(), cv2.COLOR_BGR2RGB)
                    image = resize(image, (224, 224))
                    image = (image - mean) / std
                    image = np.transpose(image, [2, 0, 1])
                    tensors_list.append(image)
                    if len(tensors_list) == window_size:
                        input_tensor = np.stack(tensors_list[: window_size], axis=1)[None][None]
                        outputs = session.run(output_names, {input_name: input_tensor.astype(np.float32)})[0]
                        gloss = str(classes[outputs.argmax()])
                        if outputs.max() > threshold:
                            if gloss != prediction_list[-1] and len(prediction_list):
                                if gloss != "---":
                                    prediction_list.append(gloss)
                        tensors_list.clear()
                    frame_counter = 0

                text = "  ".join(prediction_list)
                text_div = np.zeros((50, frame.shape[1], 3), dtype=np.uint8)
                cv2.putText(text_div, text, (10, 30), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 2)
                print(text)
                frame = np.concatenate((frame, text_div), axis=0)
                writer.write(frame)
            writer.release()
            cap.release()
            print(prediction_list)
            print(f'{settings.MEDIA_ROOT}\{video_path.file}')
            print(number, request.data.get('chatId'))
            chat_history_data_model = ChatHistoryData(anser=" ".join(prediction_list), chat = ChatHistory.objects.get(id=request.data.get('chatId')), request=video_path, owner=user)
            chat_history_data_model.save()




            return Response({'message': prediction_list, 'number': number}, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid input'}, status=status.HTTP_400_BAD_REQUEST)