from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import video_process, get_chat_history, create_chat, get_chat_data, delete_chat, get_test, post_test, get_report_data, get_chat_report

urlpatterns = [
    path('users/', views.UserList.as_view()),
    path('users/<int:pk>/', views.UserDetail.as_view()),
    path('guitar/', views.GuitarList.as_view()),
    path('upload/', views.VideoUploadView.as_view()),
    path('process/', video_process, name="video_process"),
    path('chat-history/', get_chat_history, name="chat_history"),
    path('new-chat/', create_chat, name="create_chat"),
    path('chat-data/', get_chat_data, name="chat_data"),
    path('delete-chat/', delete_chat, name="delete_chat"),
    path('test/', get_test, name="get_test"),
    path('data/', post_test, name="post_test"),
    path('report-data/', get_report_data, name="get_report_data"),
    path('chat-report/', get_chat_report, name="get_chat_report_data"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
#+= static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
#urlpatterns = format_suffix_patterns(urlpatterns)