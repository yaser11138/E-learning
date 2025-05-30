from django.contrib.auth import urls
from django.urls import path, include
from .views import studentRegistrationView, ProfileViewUpdate


urlpatterns = [
    path("dj-rest-auth/", include("dj_rest_auth.urls")),
    path("register/student/", studentRegistrationView.as_view(), name="student_register"),
    path("profile/", ProfileViewUpdate.as_view(), name="profile")
]
