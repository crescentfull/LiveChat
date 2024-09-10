from django.shortcuts import render, get_object_or_404, redirect
from .models import ChatRoom, Message
from django.views.generic import ListView, DetailView
from django.urls import reverse


def index(request):
    """
    채팅 페이지를 렌더링하는 뷰 함수입니다.
    """
    return render(request, 'myapp/index.html')


class ChatRoomListView(ListView):
    """채팅방 목록을 보여주는 뷰"""
    model = ChatRoom
    template_name = 'chat_room_list.html'
    context_object_name = 'chat_rooms'

class ChatRoomDetailView(DetailView):
    """채팅방 세부 정보를 보여주는 뷰"""
    model = ChatRoom
    template_name = 'chat_room_detail.html'
    context_object_name = 'chat_room'

def create_message(request, pk):
    """새 메시지를 생성하는 뷰"""
    chat_room = get_object_or_404(ChatRoom, pk=pk)
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Message.objects.create(user=request.user, chat_room=chat_room, content=content)
            return redirect(reverse('chat_room_detail', args=[chat_room.id]))
        else:
            return render(request, 'chat_room_detail.html', {
                'chat_room': chat_room,
                'error': '메시지 내용이 필요합니다.'
            })
    return redirect(reverse('chat_room_detail', args=[chat_room.id]))