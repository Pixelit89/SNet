from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.db.models.query import QuerySet
from .models import ChatMessages, ChatGroups, LastSeen
from datetime import datetime
import json


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['group']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        if not self.room_name == 'listener':
            self.group = await  database_sync_to_async(self.get_group)()

    async def disconnect(self, close_code):
        # Leave room group
        await  database_sync_to_async(self.message_management)(param='disconnect')
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
                'user_id': user_id,
                'group': self.group.name,
                'pub_date': datetime.now().strftime("%H:%M %d-%b-%y"),
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
        if param == 'disconnect':
            last_seen = LastSeen.objects.get(user_id=self.scope['user'].id, group=self.group)
            last_seen.last_seen = datetime.now()
            last_seen.save()


class ListenerConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        await self.accept()
        try:
            self.groups, self.last_seen = await database_sync_to_async(self.get_groups)()
            last_seen = self.last_seen.last().last_seen
            last_messages = []

            for group in self.groups:

                self.room_name = group.name
                self.room_group_name = 'chat_%s' % self.room_name
                # Join room group
                await self.channel_layer.group_add(
                    self.room_group_name,
                    self.channel_name
                )
                last = group.chatmessages_set.last().pub_date
                last_messages.append((group.name, last))
                if last > last_seen:
                    await self.send(text_data="text")
                    break
        except AttributeError:
            pass

    async def disconnect(self, close_code):
        for group in self.groups:
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    # Receive message from page (WebSocket)
    async def receive(self, text_data):
        pass

    # Send message to page (Receive from room group)
    async def chat_message(self, event):
        print(event)
        await self.send(text_data=json.dumps(event))

    def get_groups(self):
        groups = ChatGroups.objects.filter(users=self.scope['user'].id)
        last_seen = LastSeen.objects.filter(user_id=self.scope['user'].id)
        return groups, last_seen
