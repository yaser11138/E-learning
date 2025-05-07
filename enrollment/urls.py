from django.urls import path
from .views import (
    EnrollmentCreateView,
    InstructorEnrollmentListView,
    StudentEnrollmentListView,
)

urlpatterns = [
    path('courses/<slug:course_slug>/enroll/', EnrollmentCreateView.as_view(), name='enrollment-create'),
    path('enrollments/', StudentEnrollmentListView.as_view(), name='student-enrollment-list'),
    path('instructor/enrollments/', InstructorEnrollmentListView.as_view(), name='instructor-enrollment-list'),
    path('instructor/courses/<slug:course_slug>/enrollments/', InstructorEnrollmentListView.as_view(),
         name='instructor-course-enrollment-list'),
]