from django.urls import path
from rest_framework import routers
from .views import (
    StudentCourseView,
    StudentContentView,
    CourseProgressView,
    ContentProgressView,
)

router = routers.DefaultRouter()
router.register("courses", StudentCourseView, basename="course_list")

urlpatterns = router.urls

urlpatterns += [
    path("content/<slug:slug>", StudentContentView.as_view(), name="content_retrieve"),
    path(
        "course/<slug:slug>/progress",
        CourseProgressView.as_view(),
        name="course_progress",
    ),
    path(
        "content/<slug:slug>/progress",
        ContentProgressView.as_view(),
        name="content_progress",
    ),
]
