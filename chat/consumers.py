import json
from random import randint
from time import sleep
from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.middleware import BaseMiddleware
from chat.models import ChatMessage, Chat
from django.contrib.auth.models import User, AnonymousUser
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import UntypedToken

from .openrouter import OpenRouterClient


class JWTAuthMiddleware(BaseMiddleware):
    """
    Middleware для обработки аутентификации JWT токена в WebSocket.
    """

    async def __call__(self, scope, receive, send):
        # Извлекаем query string
        query_params = parse_qs(scope['query_string'].decode())
        token = query_params.get('token', [None])[0]  # Получаем токен из строки запроса

        if token:
            try:
                class FakeRequest:
                    def __init__(self, token):
                        self.META = {'HTTP_AUTHORIZATION': f'Bearer {token}'}

                fake_request = FakeRequest(token)
                user, _ = await database_sync_to_async(JWTAuthentication().authenticate)(fake_request)
                scope['user'] = user  # Устанавливаем пользователя в scope
            except Exception as e:
                print(f"Ошибка JWT аутентификации: {e}")
                scope['user'] = None  # Если ошибка, устанавливаем None
        else:
            scope['user'] = None  # Если токен отсутствует, пользователь None

        # Передача управления следующему middleware
        return await super().__call__(scope, receive, send)


class ChatConsumer(AsyncWebsocketConsumer):

    @database_sync_to_async
    def get_messages(self, chat):
        return list(chat.messages.all())

    @database_sync_to_async
    def get_user_from_message(self, message):
        return message.user

    async def connect(self):
        print(self.scope)
        self.room_name = self.scope['user'].username
        self.room_group_name = f'chat_{self.room_name}'
        print(self.room_group_name)
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        self.chat = await database_sync_to_async(Chat.objects.get)(name=self.room_name)

        messages = await self.get_messages(self.chat)
        messages_data = []
        for message in messages:

            user = await self.get_user_from_message(message)

            messages_data.append({
                'message': message.message,
                'user': user.username,
                'created_at': message.created_at.isoformat(),
            })
        await self.accept()
        await self.send(text_data=json.dumps({
            'type': 'init_messages',
            'messages': messages_data}))



    async def disconnect(self, close_code):
        # Отключение от группы
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def chat_message(self, event):
        # Обработчик для типа chat_message
        message = event['message']
        user = event['user']

        # Отправляем сообщение на WebSocket
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': message,
            'user': user,
        }))

    async def receive(self, text_data):
        user = self.scope['user']
        text_data_json = json.loads(text_data)
        print(user)
        user_message = text_data_json['message']

        chat_message = await database_sync_to_async(ChatMessage.objects.create)(chat=self.chat, user=user,
                                                                                message=user_message)


        ############
        llm_api = OpenRouterClient()
        status_code, ai_response = await llm_api.send_request(prompt=user_message)

        if status_code != 200:
            await self.send(text_data=json.dumps({
                'message': "LLM not working"
            }))
        llm_user = await database_sync_to_async(User.objects.get)(username="llm_api")
        print(llm_user.username)
        chat_message = await database_sync_to_async(ChatMessage.objects.create)(chat=self.chat, user=llm_user,
                                                                                message=ai_response)
        await self.send(text_data=json.dumps({
            'type':'llm_answer',
            'message': ai_response
        }))
