from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),  # 인덱스 페이지 URL 패턴
    path('register/', views.register, name='register'),  # 회원가입 페이지 URL 패턴
    path('chat_rooms/', views.chat_room_list, name='chat_room_list'),
    path('chat_rooms/<int:chat_room_id>/', views.chat_room_detail, name='chat_room_detail'),
    path('chat_rooms/<int:chat_room_id>/create_message/', views.create_message, name='create_message'),
    path('chat_rooms/<int:chat_room_id>/leave/', views.leave_chat_room, name='leave_chat_room'),  # 채팅방 나가기 URL 패턴
    path('chat_rooms/<int:chat_room_id>/delete/', views.delete_chat_room, name='delete_chat_room'),  # 채팅방 삭제 URL 패턴
    path('logout/', views.user_logout, name='logout'),  # 로그아웃 URL 패턴
]