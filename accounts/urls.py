from django.contrib.auth import urls
from django.urls import path, include
from .views import studentRegistrationView, StudentProfileViewUpdate


urlpatterns = [
    path("dj-rest-auth/", include("dj_rest_auth.urls")),
    path("register/student/", studentRegistrationView.as_view(), name="student_register"),
    path("", StudentProfileViewUpdate.as_view() ,name="student_profile")
]
