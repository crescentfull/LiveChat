from channels.generic.websocket import AsyncWebsocketConsumer
import json

class ChatConsumer(AsyncWebsocketConsumer):
    # 사용자 수를 저장할 클래스 변수
    user_count = 0

    async def connect(self):
        # 사용자 접속 시마다 사용자 수 증가
        ChatConsumer.user_count += 1
        self.user_name = f'손님{ChatConsumer.user_count}'  # 사용자 이름 할당
        self.room_name = 'chat_room'
        self.room_group_name = 'chat_%s' % self.room_name

        # 그룹에 가입
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # WebSocket 연결 허용
        await self.accept()

        # 모든 사용자에게 접속 메시지 브로드캐스트
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': f'{self.user_name}가 접속되었습니다.'
            }
        )

    async def disconnect(self, close_code):
        # 그룹에서 탈퇴
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        # 사용자 접속 해제 시, 사용자 수 감소
        ChatConsumer.user_count -= 1

        # 모든 사용자에게 접속 해제 메시지 브로드캐스트
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': f'{self.user_name}가 접속을 종료했습니다.'
            }
        )

    async def receive(self, text_data):
        # 수신된 메시지 파싱
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # 메시지에 사용자 이름 추가
        full_message = f"{self.user_name}: {message}"

        # 그룹에 메시지 브로드캐스트
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': full_message
            }
        )

    async def chat_message(self, event):
        # 이벤트로부터 메시지 가져오기
        message = event['message']

        # WebSocket을 통해 메시지 전송
        await self.send(text_data=json.dumps({
            'message': message
        }))
