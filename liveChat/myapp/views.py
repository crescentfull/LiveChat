from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, HttpResponseServerError
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import ChatRoom, Message
from .utils.logging_helpers import *  # 로깅 헬퍼 임포트

def get_anonymous_user_id(request):
    # 세션에 익명 사용자 ID가 없으면 새로운 ID 생성
    if 'anonymous_user_id' not in request.session:
        existing_ids = [int(id.split('익명')[1]) for id in request.session.keys() if id.startswith('익명')]
        new_id_number = max(existing_ids, default=0) + 1
        request.session['anonymous_user_id'] = f'익명{new_id_number}'
    return request.session['anonymous_user_id']

def chat_room_list(request):
    """채팅방 목록을 보여주는 뷰"""
    try:
        # 모든 채팅방을 가져옵니다.
        chat_rooms = ChatRoom.objects.all()
        if request.method == 'POST' and request.user.is_authenticated:
            # 새로운 채팅방을 생성합니다.
            room_name = request.POST.get('room_name', '').strip()
            if room_name:
                chat_room = ChatRoom.objects.create(name=room_name, created_by=request.user)
                Message.objects.create(user=request.user, chat_room=chat_room, content=f'{request.user.username} created the room.')
                return redirect('chat_room_list')
        return render(request, 'chat_room_list.html', {'chat_rooms': chat_rooms})
    except Exception as e:
        # 예외 발생 시 로그를 기록하고 서버 오류 응답을 반환합니다.
        log_error(f"Error in chat_room_list: {str(e)}")
        return HttpResponseServerError("An unexpected error occurred.")

def chat_room_detail(request, chat_room_id):
    """채팅방 상세 정보를 보여주는 뷰"""
    try:
        # 특정 채팅방과 그 메시지를 가져옵니다.
        chat_room = get_object_or_404(ChatRoom, id=chat_room_id)
        messages = Message.objects.filter(chat_room=chat_room).order_by('created_at')
        log_debug(f"Context data: chat_room={chat_room}, messages={messages}")
        # 사용자 이름을 설정합니다.
        if request.user.is_authenticated:
            username = request.user.username
        else:
            username = get_anonymous_user_id(request)
        
        # 사용자가 입장했을 때 알림 메시지를 생성합니다.
        if not Message.objects.filter(chat_room=chat_room, content__contains=f'{username} joined the room.').exists():
            Message.objects.create(user=request.user if request.user.is_authenticated else None, chat_room=chat_room, content=f'{username} joined the room.')
        
        return render(request, 'chat_room_detail.html', {'chat_room': chat_room, 'messages': messages, 'username': username})
    except ChatRoom.DoesNotExist:
        # 채팅방이 존재하지 않을 때 로그를 기록하고 404 응답을 반환합니다.
        log_error(f"ChatRoom with id {chat_room_id} does not exist.")
        return HttpResponse("Chat room not found.", status=404)
    except Exception as e:
        # 예외 발생 시 로그를 기록하고 서버 오류 응답을 반환합니다.
        log_error(f"Error in chat_room_detail: {str(e)}")
        return HttpResponseServerError("An unexpected error occurred.")

def create_message(request, chat_room_id):
    """메시지를 생성하는 뷰"""
    try:
        # 특정 채팅방을 가져옵니다.
        chat_room = get_object_or_404(ChatRoom, id=chat_room_id)
        if request.method == 'POST':
            # 메시지 내용을 가져와서 저장합니다.
            content = request.POST.get('content', '').strip()
            if not content:
                return HttpResponseBadRequest('Content cannot be empty')
            if request.user.is_authenticated:
                user = request.user
                username = user.username
            else:
                user = None
                username = f'Anonymous-{get_anonymous_user_id(request)}'
            Message.objects.create(user=user, chat_room=chat_room, content=f'{username}: {content}')
            return redirect(reverse('chat_room_detail', args=[chat_room.id]))
        return render(request, 'create_message.html', {'chat_room': chat_room})
    except Exception as e:
        # 예외 발생 시 로그를 기록하고 서버 오류 응답을 반환합니다.
        log_error(f"Error in create_message: {str(e)}")
        return HttpResponseServerError("An unexpected error occurred.")

def leave_chat_room(request, chat_room_id):
    """채팅방 나가기 뷰"""
    try:
        # 특정 채팅방을 가져옵니다.
        chat_room = get_object_or_404(ChatRoom, id=chat_room_id)
        # 사용자가 채팅방을 나갈 때 알림 메시지를 생성합니다.
        username = request.user.username if request.user.is_authenticated else f'Anonymous-{get_anonymous_user_id(request)}'
        Message.objects.create(user=request.user if request.user.is_authenticated else None, chat_room=chat_room, content=f'{username} left the room.')
        return redirect('chat_room_list')
    except Exception as e:
        # 예외 발생 시 로그를 기록하고 서버 오류 응답을 반환합니다.
        log_error(f"Error in leave_chat_room: {str(e)}")
        return HttpResponseServerError("An unexpected error occurred.")

@login_required
def delete_chat_room(request, chat_room_id):
    """채팅방 삭제 뷰"""
    try:
        # 특정 채팅방을 가져옵니다.
        chat_room = get_object_or_404(ChatRoom, id=chat_room_id)
        # 사용자가 채팅방을 삭제할 권한이 있는지 확인합니다.
        if chat_room.created_by != request.user:
            return HttpResponseForbidden('You are not allowed to delete this room.')
        chat_room.delete()
        return redirect('chat_room_list')
    except Exception as e:
        # 예외 발생 시 로그를 기록하고 서버 오류 응답을 반환합니다.
        log_error(f"Error in delete_chat_room: {str(e)}")
        return HttpResponseServerError("An unexpected error occurred.")

def index(request):
    """인덱스 페이지를 보여주는 뷰"""
    try:
        if request.method == 'POST':
            # 사용자 인증을 처리합니다.
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('chat_room_list')
            else:
                return render(request, 'index.html', {'error': 'Invalid username or password'})
        return render(request, 'index.html')
    except Exception as e:
        # 예외 발생 시 로그를 기록하고 서버 오류 응답을 반환합니다.
        log_error(f"Error in index: {str(e)}")
        return HttpResponseServerError("An unexpected error occurred.")

def register(request):
    """회원가입 페이지를 보여주는 뷰"""
    try:
        if request.method == 'POST':
            # 회원가입 정보를 처리합니다.
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
    except Exception as e:
        # 예외 발생 시 로그를 기록하고 서버 오류 응답을 반환합니다.
        log_error(f"Error in register: {str(e)}")
        return HttpResponseServerError("An unexpected error occurred.")

@login_required
def user_logout(request):
    """로그아웃 뷰"""
    try:
        # 사용자를 로그아웃 처리합니다.
        logout(request)
        return redirect('index')
    except Exception as e:
        # 예외 발생 시 로그를 기록하고 서버 오류 응답을 반환합니다.
        log_error(f"Error in user_logout: {str(e)}")
        return HttpResponseServerError("An unexpected error occurred.")