from datetime import datetime, timedelta
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from drf_spectacular.types import OpenApiTypes
from courses.models import Course
from .models import Enrollment
from .serializers import EnrollmentSerializer
from core.permissions import IsInstructor, IsStudent


class EnrollmentCreateView(APIView):
    permission_classes = [IsAuthenticated, IsStudent]

    @extend_schema(
        description="Create a new enrollment for the authenticated student in the specified course",
        summary="Create course enrollment",
        responses={
            201: EnrollmentSerializer,
            404: OpenApiResponse(description="Course not found"),
            403: OpenApiResponse(description="User is not a student or not authenticated")
        },
        tags=['Enrollments']
    )
    def post(self, request, course_slug):
        course = get_object_or_404(Course, slug=course_slug)
        deadline = datetime.today().date() + timedelta(days=course.required_time)
        enrollment = Enrollment.objects.create(user=request.user, course=course, deadline=deadline)
        enrollment_serializer = EnrollmentSerializer(instance=enrollment)
        return Response(data=enrollment_serializer.data, status=status.HTTP_201_CREATED)


class InstructorEnrollmentListView(APIView):
    permission_classes = [IsAuthenticated, IsInstructor]

    @extend_schema(
        description="Retrieve enrollments for courses taught by the authenticated instructor",
        summary="List instructor course enrollments",
        parameters=[
            OpenApiParameter(
                name='course_slug',
                location=OpenApiParameter.PATH,
                description="Filter enrollments by course slug (optional)",
                type=OpenApiTypes.STR,
                required=False
            )
        ],
        responses={
            200: EnrollmentSerializer(many=True),
            404: OpenApiResponse(description="Course not found"),
            403: OpenApiResponse(description="User is not an instructor or not authenticated")
        },
        tags=['Enrollments']
    )
    def get(self, request, course_slug=None):
        if course_slug:
            course = get_object_or_404(Course, slug=course_slug)
            enrollments = course.enrollments.all()
            enrollment_serializer = EnrollmentSerializer(instance=enrollments, many=True)
        else:
            enrollments = Enrollment.objects.filter(course__owner=request.user)
            enrollment_serializer = EnrollmentSerializer(instance=enrollments, many=True)
        return Response(data=enrollment_serializer.data, status=status.HTTP_200_OK)


class StudentEnrollmentListView(APIView):
    permission_classes = [IsAuthenticated, IsStudent]

    @extend_schema(
        description="Retrieve all enrollments for the authenticated student",
        summary="List student enrollments",
        responses={
            200: EnrollmentSerializer(many=True),
            403: OpenApiResponse(description="User is not a student or not authenticated")
        },
        tags=['Enrollments']
    )
    def get(self, request):
        enrollments = request.user.enrollments.all()
        enrollment_serializer = EnrollmentSerializer(instance=enrollments, many=True)
        return Response(data=enrollment_serializer.data, status=status.HTTP_200_OK)
