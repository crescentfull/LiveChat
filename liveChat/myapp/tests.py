import asyncio
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.exceptions import ValidationError
from .models import ChatRoom, Message
from channels.testing import WebsocketCommunicator
from liveChat.asgi import application

class ChatRoomTests(TestCase):
    def setUp(self):
        # 테스트 사용자 생성
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client = Client()
        self.client.login(username='testuser', password='testpassword')

        # 테스트 채팅방 생성
        self.chat_room = ChatRoom.objects.create(name='Test Room', created_by=self.user)

    def test_chat_room_creation(self):
        # 채팅방이 올바르게 생성되었는지 테스트
        self.assertEqual(ChatRoom.objects.count(), 1)
        self.assertEqual(self.chat_room.name, 'Test Room')
        self.assertEqual(self.chat_room.created_by, self.user)

    def test_join_chat_room(self):
        # 채팅방에 입장할 때 메시지가 생성되는지 테스트
        response = self.client.get(reverse('chat_room_detail', args=[self.chat_room.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'joined the room.')

    def test_send_message(self):
        # 메시지를 전송할 때 메시지가 올바르게 저장되는지 테스트
        response = self.client.post(reverse('create_message', args=[self.chat_room.id]), {'content': 'Hello, world!'})
        self.assertEqual(response.status_code, 302)  # 리다이렉트 확인
        self.assertEqual(Message.objects.count(), 1)
        message = Message.objects.first()
        self.assertEqual(message.content, 'testuser: Hello, world!')
        self.assertEqual(message.user, self.user)
        self.assertEqual(message.chat_room, self.chat_room)

    def test_receive_message_authenticated_user(self):
        # WebSocket을 통해 인증된 사용자가 메시지를 수신하는지 테스트
        async def async_test():
            communicator = WebsocketCommunicator(application, f'/ws/chat/{self.chat_room.id}/')
            # WebSocket 연결 시 인증된 사용자 설정
            communicator.scope['user'] = self.user
            connected, subprotocol = await communicator.connect()
            self.assertTrue(connected)

            # 채팅방 입장 메시지 수신
            response = await communicator.receive_json_from()
            self.assertEqual(response['content'], 'testuser joined the room.')

            # 메시지 전송
            await communicator.send_json_to({'message': 'Hello, world!'})

            # 전송된 메시지 수신
            response = await communicator.receive_json_from()
            self.assertEqual(response['content'], 'testuser: Hello, world!')

            await communicator.disconnect()

        asyncio.run(async_test())

    def test_receive_message_anonymous_user(self):
        # WebSocket을 통해 익명 사용자가 메시지를 수신하는지 테스트
        async def async_test():
            communicator = WebsocketCommunicator(application, f'/ws/chat/{self.chat_room.id}/')
            connected, subprotocol = await communicator.connect()
            self.assertTrue(connected)

            # 채팅방 입장 메시지 수신
            response = await communicator.receive_json_from()
            self.assertEqual(response['content'], 'Anonymous joined the room.')

            # 메시지 전송
            await communicator.send_json_to({'message': 'Hello, world!'})

            # 전송된 메시지 수신
            response = await communicator.receive_json_from()
            self.assertEqual(response['content'], 'Anonymous: Hello, world!')

            await communicator.disconnect()

        asyncio.run(async_test())

class MessageTestCase(TestCase):
    """메시지 모델에 대한 테스트 케이스"""
    
    @classmethod
    def setUpTestData(cls):
        """테스트를 위한 초기 설정 (모든 테스트에 공유)"""
        cls.user = User.objects.create_user(username='testuser', password='12345')
        cls.chat_room = ChatRoom.objects.create(name='테스트 채팅방', created_by=cls.user)
        cls.message = Message.objects.create(
            user=cls.user,
            chat_room=cls.chat_room,
            content='안녕하세요!'
        )

    def test_message_creation_with_valid_data(self):
        """유효한 데이터로 메시지가 올바르게 생성되는지 테스트"""
        self.assertEqual(self.message.content, '안녕하세요!')
        self.assertEqual(self.message.user, self.user)
        self.assertEqual(self.message.chat_room, self.chat_room)
        self.assertTrue(isinstance(self.message, Message))

    def test_message_creation_with_invalid_data(self):
        """잘못된 데이터로 메시지 생성 시 예외가 발생하는지 테스트"""
        with self.assertRaises(ValidationError):
            message = Message(
                user=self.user,
                chat_room=self.chat_room,
                content=''
            )
            message.full_clean()  # ValidationError를 발생시키기 위해 full_clean() 호출

class ViewTestCase(TestCase):
    """뷰에 대한 테스트 케이스"""
    
    @classmethod
    def setUpTestData(cls):
        """테스트를 위한 초기 설정 (모든 테스트에 공유)"""
        cls.user = User.objects.create_user(username='testuser', password='12345')
        cls.chat_room = ChatRoom.objects.create(name='테스트 채팅방', created_by=cls.user)

    def setUp(self):
        """각 테스트마다 클라이언트를 로그인 상태로 만듭니다."""
        self.client.login(username='testuser', password='12345')

    def test_chat_room_list_view(self):
        """채팅방 목록 뷰가 올바르게 작동하는지 테스트"""
        response = self.client.get(reverse('chat_room_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '테스트 채팅방')

    def test_chat_room_detail_view(self):
        """채팅방 상세 뷰가 올바르게 작동하는지 테스트"""
        response = self.client.get(reverse('chat_room_detail', args=[self.chat_room.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '테스트 채팅방')

    def test_create_message(self):
        """메시지 생성 기능이 올바르게 작동하는지 테스트"""
        response = self.client.post(reverse('create_message', args=[self.chat_room.id]), {
            'content': '새 메시지입니다.'
        })
        self.assertEqual(response.status_code, 302)  # 리다이렉트 상태 코드
        self.assertTrue(Message.objects.filter(content='testuser: 새 메시지입니다.').exists())

    def test_create_message_with_empty_content(self):
        """빈 메시지 내용으로 메시지 생성 시도"""
        response = self.client.post(reverse('create_message', args=[self.chat_room.id]), {
            'content': ''
        })
        self.assertEqual(response.status_code, 400)  # 잘못된 요청 상태 코드
        self.assertFalse(Message.objects.filter(content='').exists())