from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.generics import ListAPIView, RetrieveAPIView
from courses.models import Subject, Course
from courses import serializers


class SubjectList(ListAPIView):
    queryset = Subject.objects.all()
    serializer_class = serializers.SubjectListSerializer


class SubjectDetail(RetrieveAPIView):
    queryset = Subject.objects.all()
    serializer_class = serializers.SubjectSerializer


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            serializer_class = serializers.CourseListSerializer
        else:
            serializer_class = serializers.CourseSerializer






