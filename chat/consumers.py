import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import ChatMessage, ChatRoom

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs'].get('room_name') or 'general'
        # For simplicity, using room_name directly. For course-specific rooms, you might derive this from a course ID.
        self.room_group_name = f'chat_{self.room_name}'

        # Check if user is authenticated
        if not self.scope['user'].is_authenticated:
            await self.close()
            return

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        print(f"User {self.scope['user']} connected to room {self.room_group_name}")

        # Add user to ChatRoom participants (optional, depending on your logic)
        # You might want to create/get the ChatRoom instance here
        # await self.add_user_to_room_participants(self.scope['user'], self.room_name)


    async def disconnect(self, close_code):
        # Leave room group
        if hasattr(self, 'room_group_name'): # Ensure room_group_name was set
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
            print(f"User {self.scope['user']} disconnected from room {self.room_group_name}")
        # Optional: Remove user from ChatRoom participants if you added them
        # await self.remove_user_from_room_participants(self.scope['user'], self.room_name)


    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_content = text_data_json.get('message')
        user = self.scope['user']

        if not message_content or not user.is_authenticated:
            print("Discarding empty message or message from unauthenticated user.")
            return

        # Save message to database
        chat_message = await self.save_message(user, self.room_name, message_content)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat.message', # This will call the chat_message method
                'message': message_content,
                'sender_id': user.id,
                'sender_username': user.username, # Or any other user identifier
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
            'is_self': self.scope['user'].id == sender_id # Flag if the message is from the current user
        }))
        print(f"Message '{message}' from {sender_username} delivered to user {self.scope['user'].username} in room {self.room_group_name}")

    @database_sync_to_async
    def save_message(self, sender, room_name, content):
        # Get or create the chat room.
        # For simplicity, we're using the room_name directly.
        # In a more complex setup, you might fetch a Course object and then its associated ChatRoom.
        room, created = ChatRoom.objects.get_or_create(name=room_name)

        # If the room is newly created and you want to link it to a course,
        # you'd need the course information here. For now, we'll keep it simple.
        # Example: if room_name was a course slug:
        # try:
        #     course = Course.objects.get(slug=room_name)
        #     room.course = course
        #     room.save()
        # except Course.DoesNotExist:
        #     pass # Or handle error

        message = ChatMessage.objects.create(
            room=room,
            sender=sender,
            content=content
        )
        return message

    # Optional helper methods for managing ChatRoom participants
    # @database_sync_to_async
    # def add_user_to_room_participants(self, user, room_name):
    #     room, created = ChatRoom.objects.get_or_create(name=room_name)
    #     room.participants.add(user)

    # @database_sync_to_async
    # def remove_user_from_room_participants(self, user, room_name):
    #     try:
    #         room = ChatRoom.objects.get(name=room_name)
    #         room.participants.remove(user)
    #     except ChatRoom.DoesNotExist:
    #         pass # Or log error

    # Note: The above participant management is basic. You might want more robust logic,
    # e.g., ensuring a ChatRoom is linked to a Course and only enrolled students can join.
    # This would involve fetching the Course model and checking enrollment status.
    # For now, this consumer focuses on the core messaging functionality.
    # Authentication is handled by `self.scope['user'].is_authenticated`.
    # Authorization (who can join which room) would typically be handled by checking
    # course enrollment or other criteria when a user tries to connect to a specific room.
    # The `room_name` parameter in the URL will be key for this.

    # A placeholder for fetching course-specific room, if needed.
    # @database_sync_to_async
    # def get_course_chat_room(self, course_id):
    #     try:
    #         course = Course.objects.get(id=course_id)
    #         room, created = ChatRoom.objects.get_or_create(course=course, defaults={'name': f"Course {course.title} Chat"})
    #         return room
    #     except Course.DoesNotExist:
    #         return None

# Example of how you might structure a course-specific consumer:
# class CourseChatConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.course_id = self.scope['url_route']['kwargs']['course_id']
#         self.user = self.scope['user']

#         if not self.user.is_authenticated:
#             await self.close()
#             return

#         # Check if user is enrolled in the course (example authorization)
#         # is_enrolled = await self.check_enrollment(self.user, self.course_id)
#         # if not is_enrolled:
#         #     await self.close()
#         #     return

#         self.room = await self.get_course_chat_room(self.course_id)
#         if not self.room:
#             await self.close() # Course or room not found
#             return

#         self.room_group_name = f'chat_course_{self.course_id}'

#         await self.channel_layer.group_add(self.room_group_name, self.channel_name)
#         await self.accept()
#         await self.add_user_to_room_participants(self.user, self.room.id) # Use room.id if using PK

#     # ... other methods similar to ChatConsumer, but using self.room and self.course_id
#     # You'd also need to implement check_enrollment and get_course_chat_room
#     # using @database_sync_to_async
#     pass
