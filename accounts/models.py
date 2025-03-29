from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    pass


EDUCATION_CHOICES = [
    ("HIGH_SCHOOL", "High School"),
    ("BACHELORS", "Bachelors"),
    ("MASTERS", "Masters"),
    ("PHD", "PhD"),
]


class Student(models.Model):

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    birth_date = models.DateField()
    education = models.CharField(max_length=255, choices=EDUCATION_CHOICES)
    phone_number = models.CharField(max_length=255)
    profile_picture = models.ImageField(
        upload_to="profile_pictures/", null=True, blank=True
    )


class Instructor(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    bio = models.TextField()
    education = models.CharField(max_length=255, choices=EDUCATION_CHOICES)
    profile_picture = models.ImageField(
        upload_to="profile_pictures/", null=True, blank=True
    )
