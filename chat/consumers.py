import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import ChatMessage, ChatRoom
from courses.models import Course

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs'].get('room_name') or 'general'
        self.room_group_name = f'chat_{self.room_name}'

        if not self.scope['user'].is_authenticated:
            await self.close()
            return
        
        try:
            self.course = await database_sync_to_async(Course.objects.get)(slug=self.room_name)
        except Course.DoesNotExist:
            await self.send(text_data='{"error": "Course not found."}')
            await self.close()
            return


        # Join room group
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        print(f"User {self.scope['user']} connected to room {self.room_group_name}")


        await self.add_user_to_room_participants(self.scope['user'], self.room_name)


    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'): 
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
            print(f"User {self.scope['user']} disconnected from room {self.room_group_name}")

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_content = text_data_json.get('message')
        user = self.scope['user']

        if not message_content or not user.is_authenticated:
            print("Discarding empty message or message from unauthenticated user.")
            return

        chat_message = await self.save_message(user, self.room_name, message_content)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat.message', 
                'message': message_content,
                'sender_id': user.id,
                'sender_username': user.username,
                'timestamp': str(chat_message.timestamp)
            }
        )
        print(f"Message '{message_content}' from {user.username} sent to group {self.room_group_name}")


    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        sender_id = event['sender_id']
        sender_username = event['sender_username']
        timestamp = event['timestamp']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'sender_id': sender_id,
            'sender_username': sender_username,
            'timestamp': timestamp,
            'is_self': self.scope['user'].id == sender_id 
        }))
        print(f"Message '{message}' from {sender_username} delivered to user {self.scope['user'].username} in room {self.room_group_name}")

    @database_sync_to_async
    def save_message(self, sender, room_name, content):
        room = ChatRoom.objects.get(name=room_name)

        message = ChatMessage.objects.create(
            room=room,
            sender=sender,
            content=content
        )
        return message

    @database_sync_to_async
    def add_user_to_room_participants(self, user, room_name):
         room, created = ChatRoom.objects.get_or_create(name=room_name)
         if created:
             room.course = Course.objects.get(slug=self.room_name)
             room.save()
         room.participants.add(user)

