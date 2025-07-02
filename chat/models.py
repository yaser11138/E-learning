from django.db import models
from django.conf import settings
from courses.models import Course # Assuming you want to link chat rooms to courses

class ChatRoom(models.Model):
    """
    Represents a chat room, potentially linked to a course.
    """
    name = models.CharField(max_length=255, help_text="Name of the chat room")
    course = models.ForeignKey(
        Course,
        related_name='chat_rooms',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Course this chat room belongs to (optional)"
    )
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='chat_rooms',
        blank=True,
        help_text="Users participating in this chat room"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.course:
            return f"Chat for {self.course.title}"
        return self.name

class ChatMessage(models.Model):
    """
    Represents a single message within a chat room.
    """
    room = models.ForeignKey(
        ChatRoom,
        related_name='messages',
        on_delete=models.CASCADE,
        help_text="The chat room this message belongs to"
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='sent_messages',
        on_delete=models.CASCADE,
        help_text="The user who sent this message"
    )
    content = models.TextField(help_text="The content of the message")
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender} in {self.room.name} at {self.timestamp}"

    class Meta:
        ordering = ['timestamp']
