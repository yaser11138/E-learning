from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.types import OpenApiTypes
from .serializers import CourseSerializer
from .permissions import IsInstructor, IsOwner
from .models import Course


class CourseViewSet(ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAuthenticated, IsInstructor, IsOwner]
    lookup_field = "slug"

    @extend_schema(
        summary="Create a new course",
        description="Creates a new course with the provided data, including file uploads",
        request={'multipart/form-data': CourseSerializer},
        responses={201: CourseSerializer, 400: OpenApiTypes.OBJECT},
        tags=["course"]
    )
    def create(self, request, *args, **kwargs):  # Handles POST
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Update an existing course",
        description="Updates the course with the given slug",
        request=CourseSerializer,
        responses={200: CourseSerializer, 400: OpenApiTypes.OBJECT},
        tags=["course"]
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        summary="Delete a course",
        description="Deletes the course with the given slug",
        responses={200: OpenApiTypes.OBJECT, 404: OpenApiTypes.OBJECT},
        tags=["course"]
    )
    def destroy(self, request, *args, **kwargs):  # Handles DELETE
        course = self.get_object()
        title = course.title
        self.perform_destroy(course)
        return Response({"message": f"{title} successfully deleted"}, status=status.HTTP_200_OK)








