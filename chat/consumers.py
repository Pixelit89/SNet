from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.db.models.query import QuerySet
from .models import ChatMessages, ChatGroups
from datetime import datetime
import json


class ChatConsumer(AsyncWebsocketConsumer):
    connected_users = []
    group = 0

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['group']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        if not self.scope['user'].username in self.connected_users:
            self.connected_users.append(self.scope['user'].username)

        if self.group == 0:
            self.group = await  database_sync_to_async(self.get_group)()

        # history = await database_sync_to_async(self.message_management)(param='connect', room=self.group)
        # history = reversed(history)
        # for item in history:
        #     message = item.message
        #     username = item.username.username
        #     pub_date = item.pub_date
        #     # Send message to WebSocket
        #     await self.send(text_data=json.dumps({
        #         'message': message,
        #         'username': username,
        #         'pub_date': pub_date.strftime("%d-%b-%Y %H:%M:%S")
        #     }))


    async def disconnect(self, close_code):
        # Leave room group
        if self.scope['user'].username in self.connected_users:
            self.connected_users.remove(self.scope['user'].username)
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from page (WebSocket)
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        user_id = self.scope['user'].id
        await database_sync_to_async(self.message_management)(param='store', message=message)
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'user_id': user_id
            }
        )

    # Send message to page (Receive from room group)
    async def chat_message(self, event):
        message = event['message']
        user_id = event['user_id']
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'user_id': user_id,
            'pub_date': datetime.now().strftime("%d-%b-%Y %H:%M:%S")
        }))

    def get_group(self):
        group = ChatGroups.objects.get(name=self.scope['url_route']['kwargs']['group'])
        return group

    def message_management(self, param, message=None, room=None):
        if param == 'store':
            message = ChatMessages.objects.create(
                user_id=self.scope['user'].id,
                message=message,
                chat_room=self.group
            )
            message.save()
        if param == 'connect':
            history = ChatMessages.objects.filter(chat_room=room).order_by('-pub_date')[:10]
            return history
