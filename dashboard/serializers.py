from rest_framework import serializers
from courses.models import Course, CourseProgress
from courses.serializers import CourseProgressSerializer as BaseCourseProgressSerializer

class StudentDashboardSerializer(serializers.Serializer):
    role = serializers.CharField(default='student')
    statistics = serializers.DictField()
    recent_courses = serializers.ListField()
    enrolled_courses = serializers.ListField()

class TeacherDashboardSerializer(serializers.Serializer):
    role = serializers.CharField(default='teacher')
    statistics = serializers.DictField()
    top_courses = serializers.ListField()
    courses = serializers.ListField()