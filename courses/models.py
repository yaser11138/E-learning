from django.db import models
from django.contrib.auth import get_user_model
from .fields import OrderField
from polymorphic.models import PolymorphicModel

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
    title = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE, related_name="courses"
    )
    required_time = models.IntegerField()
    summary = models.TextField()
    thumbnail = models.ImageField()
    owner = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    slug = models.SlugField(null=False, unique=True)

    class Meta:
        ordering = ["-created"]
        verbose_name_plural = "courses"

    def __str__(self):
        return f"{self.title} by {self.owner.fullname}"

    @property
    def is_free(self):
        if self.price == 0:
            return True
        else:
            return False


class Module(CreateUpdateDate):
    course = models.ForeignKey(Course, related_name="modules", on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = OrderField(blank=True, for_fields="course")

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.title


class Content(PolymorphicModel):
    module = models.ForeignKey(
        Module, related_name="contents", on_delete=models.CASCADE
    )
    order = OrderField(blank=True, for_fields=["module"])
    owner = models.ForeignKey(
        UserModel, related_name="content_related", on_delete=models.CASCADE
    )
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
