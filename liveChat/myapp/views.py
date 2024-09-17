from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseBadRequest, HttpResponseForbidden
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import ChatRoom, Message

@login_required
def chat_room_list(request):
    """채팅방 목록을 보여주는 뷰"""
    chat_rooms = ChatRoom.objects.all()
    if request.method == 'POST':
        room_name = request.POST.get('room_name', '').strip()
        if room_name:
            chat_room = ChatRoom.objects.create(name=room_name, created_by=request.user)
            Message.objects.create(user=request.user, chat_room=chat_room, content=f'{request.user.username} created the room.')
            return redirect('chat_room_list')
    return render(request, 'chat_room_list.html', {'chat_rooms': chat_rooms})

@login_required
def chat_room_detail(request, chat_room_id):
    """채팅방 상세 정보를 보여주는 뷰"""
    chat_room = get_object_or_404(ChatRoom, id=chat_room_id)
    messages = Message.objects.filter(chat_room=chat_room).order_by('created_at')
    # 사용자가 입장했을 때 알림 메시지 생성
    if not Message.objects.filter(chat_room=chat_room, content__contains=f'{request.user.username} joined the room.').exists():
        Message.objects.create(user=request.user, chat_room=chat_room, content=f'{request.user.username} joined the room.')
    return render(request, 'chat_room_detail.html', {'chat_room': chat_room, 'messages': messages})

@login_required
def create_message(request, chat_room_id):
    """메시지를 생성하는 뷰"""
    chat_room = get_object_or_404(ChatRoom, id=chat_room_id)
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if not content:
            return HttpResponseBadRequest('Content cannot be empty')
        Message.objects.create(user=request.user, chat_room=chat_room, content=content)
        return redirect(reverse('chat_room_detail', args=[chat_room.id]))
    return render(request, 'create_message.html', {'chat_room': chat_room})

@login_required
def leave_chat_room(request, chat_room_id):
    """채팅방 나가기 뷰"""
    chat_room = get_object_or_404(ChatRoom, id=chat_room_id)
    Message.objects.create(user=request.user, chat_room=chat_room, content=f'{request.user.username} left the room.')
    return redirect('chat_room_list')

@login_required
def delete_chat_room(request, chat_room_id):
    """채팅방 삭제 뷰"""
    chat_room = get_object_or_404(ChatRoom, id=chat_room_id)
    if chat_room.created_by != request.user:
        return HttpResponseForbidden('You are not allowed to delete this room.')
    chat_room.delete()
    return redirect('chat_room_list')

def index(request):
    """인덱스 페이지를 보여주는 뷰"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('chat_room_list')
        else:
            return render(request, 'index.html', {'error': 'Invalid username or password'})
    return render(request, 'index.html')

def register(request):
    """회원가입 페이지를 보여주는 뷰"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        
        if password != password_confirm:
            return render(request, 'register.html', {'error': 'Passwords do not match'})
        
        if User.objects.filter(username=username).exists():
            return render(request, 'register.html', {'error': 'Username already exists'})
        
        user = User.objects.create_user(username=username, password=password)
        login(request, user)
        return redirect('chat_room_list')
    
    return render(request, 'register.html')

@login_required
def user_logout(request):
    """로그아웃 뷰"""
    logout(request)
    return redirect('index')