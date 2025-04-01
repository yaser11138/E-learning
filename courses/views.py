from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.types import OpenApiTypes
from .serializers import CourseSerializer
from .permissions import IsInstructor


class CreateCourseView(APIView):
    serializer_class = CourseSerializer
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAuthenticated, IsInstructor]

    @extend_schema(
        summary="Create a new course",
        description="Creates a new course with the provided data, including file uploads",
        request={
            'multipart/form-data': CourseSerializer,
        },
        responses={
            201: CourseSerializer,
            400: OpenApiTypes.OBJECT,
        },
        tags=["Courses"]
    )
    def post(self, request):
        course_serializer = CourseSerializer(data=request.data)
        if course_serializer.is_valid():
            course_serializer.save(owner=request.user)
            return Response(data=course_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(data=course_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


