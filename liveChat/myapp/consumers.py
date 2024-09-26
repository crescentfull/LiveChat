import json
from channels.generic.websocket import AsyncWebsocketConsumer
from datetime import datetime

class ChatConsumer(AsyncWebsocketConsumer):
    # WebSocket 연결 시 실행되는 함수
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        # 방 그룹에 참여
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # 입장 메시지 전송
        username = self.scope["user"].username if self.scope["user"].is_authenticated else "Anonymous"
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': f'{username} joined the room.',
                'username': username  # 추가
            }
        )

    # WebSocket 연결 종료 시 실행되는 함수
    async def disconnect(self, close_code):
        # 방 그룹에서 나가기
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # 클라이언트로부터 메시지를 수신할 때 실행되는 함수
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # 방 그룹에 메시지 전송
        username = self.scope["user"].username if self.scope["user"].is_authenticated else "Anonymous"
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': f'{username}: {message}',
                'username': username  # 추가
            }
        )

    # 방 그룹에서 메시지를 수신할 때 실행되는 함수
    async def chat_message(self, event):
        message = event['message']
        username = event.get('username', 'Anonymous')  # 추가

        # WebSocket으로 메시지 전송
        await self.send(text_data=json.dumps({
            'content': message,
            'username': username  # 추가
        }))