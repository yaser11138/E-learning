from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from courses.models import Course


User = get_user_model()


class Enrollment(models.Model):
    class StatusChoices(models.TextChoices):
        Completed = "COMPLETED", "Completed"
        In_progress = "IN PROGRESS", "In progress"
        reached_deadline = "REACHED DEADLINE", "reached deadline"

    user = models.ForeignKey(User, related_name="enrollments", on_delete=models.CASCADE)
    course = models.ForeignKey(Course, related_name="enrollments", on_delete=models.CASCADE)
    started = models.DateField(auto_now_add=True)
    deadline = models.DateField()
    status = models.CharField(choices=StatusChoices.choices, default=StatusChoices.In_progress)

    @property
    def deadline_reached(self):
        if self.deadline == timezone.now().date():
            return True
        else:
            return False