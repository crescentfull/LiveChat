from django.test import TestCase
from django.urls import reverse
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from .models import ChatRoom, Message

class ChatRoomTestCase(TestCase):
    """채팅방 모델에 대한 테스트 케이스"""
    
    @classmethod
    def setUpTestData(cls):
        """테스트를 위한 초기 설정 (모든 테스트에 공유)"""
        cls.user = User.objects.create_user(username='testuser', password='12345')
        cls.chat_room = ChatRoom.objects.create(name='테스트 채팅방')

    def test_chat_room_creation(self):
        """채팅방이 올바르게 생성되는지 테스트"""
        self.assertEqual(self.chat_room.name, '테스트 채팅방')
        self.assertTrue(isinstance(self.chat_room, ChatRoom))

    def test_chat_room_creation_with_duplicate_name(self):
        """중복된 이름의 채팅방 생성 테스트"""
        with self.assertRaises(IntegrityError):
            ChatRoom.objects.create(name='테스트 채팅방')

class MessageTestCase(TestCase):
    """메시지 모델에 대한 테스트 케이스"""
    
    @classmethod
    def setUpTestData(cls):
        """테스트를 위한 초기 설정 (모든 테스트에 공유)"""
        cls.user = User.objects.create_user(username='testuser', password='12345')
        cls.chat_room = ChatRoom.objects.create(name='테스트 채팅방')
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
        with self.assertRaises(ValueError):
            Message.objects.create(
                user=self.user,
                chat_room=self.chat_room,
                content=''
            )

class ViewTestCase(TestCase):
    """뷰에 대한 테스트 케이스"""
    
    @classmethod
    def setUpTestData(cls):
        """테스트를 위한 초기 설정 (모든 테스트에 공유)"""
        cls.user = User.objects.create_user(username='testuser', password='12345')
        cls.chat_room = ChatRoom.objects.create(name='테스트 채팅방')

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
        self.assertTrue(Message.objects.filter(content='새 메시지입니다.').exists())

    def test_create_message_with_empty_content(self):
        """빈 메시지 내용으로 메시지 생성 시도"""
        response = self.client.post(reverse('create_message', args=[self.chat_room.id]), {
            'content': ''
        })
        self.assertEqual(response.status_code, 400)  # 잘못된 요청 상태 코드
        self.assertFalse(Message.objects.filter(content='').exists())
