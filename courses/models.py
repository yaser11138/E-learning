from django.db import models
from .fields import OrderField
from django.contrib.auth import get_user_model

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
        ordering = ['title']

    def __str__(self):
        return self.title


class Course(CreateUpdateDate):
    title = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='courses')
    required_time = models.IntegerField()
    summary = models.TextField()
    thumbnail = models.ImageField()
    owner = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    slug = models.SlugField(null=False, unique=True)

    class Meta:
        ordering = ['-created']
        verbose_name_plural = 'courses'

    def __str__(self):
        return f"{self.title} by {self.owner.fullname}"

    @property
    def is_free(self):
        if self.price == 0:
            return True
        else:
            return False


class Module(CreateUpdateDate):
    course = models.ForeignKey(Course, related_name='modules',
                               on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = OrderField(blank=True, for_fields="course")

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title


class Content(CreateUpdateDate):
    module = models.ForeignKey(Module, related_name="contents",
                               on_delete=models.CASCADE)
    slug = models.SlugField(null=False, unique=True)
    is_free = models.BooleanField(default=False)
    video_content = models.URLField()
    text_content = models.TextField()
    file_content = models.FileField(upload_to="images")
    image_content = models.ImageField(upload_to="images")
    order = OrderField(blank=True, for_fields="module")

    class Meta:
        ordering = ['order']
