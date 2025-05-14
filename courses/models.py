import uuid
from django.db import models
from django.contrib.auth import get_user_model
from .fields import OrderField, AutoSlugField
from polymorphic.models import PolymorphicModel
from django.utils import timezone

UserModel = get_user_model()


class CreateUpdateDate(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Subject(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title


class Course(CreateUpdateDate):
    title = models.CharField(max_length=50, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE, related_name="courses"
    )
    required_time = models.IntegerField()
    summary = models.TextField()
    thumbnail = models.ImageField()
    owner = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    slug = AutoSlugField(null=False, populate_from="title")

    class Meta:
        ordering = ["-created"]
        verbose_name_plural = "courses"

    def __str__(self):
        return f"{self.title} by {self.owner.get_full_name()}"

    @property
    def is_free(self):
        if self.price == 0:
            return True
        else:
            return False


class Module(CreateUpdateDate):
    course = models.ForeignKey(Course, related_name="modules", on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    slug = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    description = models.TextField(blank=True)
    order = OrderField(blank=True, for_fields=["course"])

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.title


class Content(PolymorphicModel):
    module = models.ForeignKey(
        Module, related_name="contents", on_delete=models.CASCADE
    )
    order = OrderField(blank=True, for_fields=["module"])
    slug = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField(max_length=250)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    is_free = models.BooleanField(default=False)


class VideoContent(Content):
    video_file = models.FileField(upload_to="videos/")


class ImageContent(Content):
    image_file = models.ImageField(upload_to="images/")


class TextContent(Content):
    text = models.TextField()


class FileContent(Content):
    file = models.FileField(upload_to="files/")


class CourseProgress(models.Model):
    student = models.ForeignKey(
        UserModel, on_delete=models.CASCADE, related_name="course_progress"
    )
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="progress"
    )
    started_at = models.DateTimeField(auto_now_add=True)
    last_accessed = models.DateTimeField(auto_now=True)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ["student", "course"]

    def __str__(self):
        return f"{self.student.get_full_name()} - {self.course.title}"

    @property
    def progress_percentage(self):
        total_contents = sum(
            module.contents.count() for module in self.course.modules.all()
        )
        if total_contents == 0:
            return 0
        completed_contents = ContentProgress.objects.filter(
            student=self.student, content__module__course=self.course, completed=True
        ).count()
        return (completed_contents / total_contents) * 100


class ContentProgress(models.Model):
    student = models.ForeignKey(
        UserModel, on_delete=models.CASCADE, related_name="content_progress"
    )
    content = models.ForeignKey(
        Content, on_delete=models.CASCADE, related_name="progress"
    )
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    last_position = models.FloatField(default=0)  # For video progress tracking

    class Meta:
        unique_together = ["student", "content"]

    def __str__(self):
        return f"{self.student.get_full_name()} - {self.content.title}"

    def mark_as_completed(self):
        self.completed = True
        self.completed_at = timezone.now()
        self.save()

        # Check if all contents in the module are completed
        module = self.content.module
        all_contents = module.contents.all()
        all_completed = all(
            ContentProgress.objects.filter(
                student=self.student, content=content, completed=True
            ).exists()
            for content in all_contents
        )

        if all_completed:
            # Mark course as completed if all modules are completed
            course = module.course
            all_modules = course.modules.all()
            all_modules_completed = all(
                all(
                    ContentProgress.objects.filter(
                        student=self.student, content=content, completed=True
                    ).exists()
                    for content in module.contents.all()
                )
                for module in all_modules
            )

            if all_modules_completed:
                course_progress = CourseProgress.objects.get(
                    student=self.student, course=course
                )
                course_progress.completed = True
                course_progress.completed_at = timezone.now()
                course_progress.save()
