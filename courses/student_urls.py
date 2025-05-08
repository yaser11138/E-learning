from django.urls import path
from rest_framework import routers
from .views import StudentCourseView,StudentContentView
router = routers.DefaultRouter()
router.register("course", StudentCourseView, basename="course_list")
urlpatterns = router.urls

urlpatterns += [
    path("content/<slug:slug>", StudentContentView.as_view(), name="content_retrieve")
]