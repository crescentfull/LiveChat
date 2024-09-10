from django.urls import path
from . import views

urlpatterns = [
    path('chat/', views.ChatRoomListView.as_view(), name='chat_room_list'),
    path('chat/<int:pk>/', views.ChatRoomDetailView.as_view(), name='chat_room_detail'),
    path('chat/<int:pk>/create_message/', views.create_message, name='create_message'),
]
