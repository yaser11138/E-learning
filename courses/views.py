from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.types import OpenApiTypes
from .serializers import CourseSerializer, ModuleSerializer
from .permissions import IsInstructor, IsOwner
from .models import Course, Module


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


class ModuleListView(APIView):
    serializer_class = ModuleSerializer
    permission_classes = [IsAuthenticated, IsInstructor, IsOwner]

    @extend_schema(
        summary="List all modules in a course",
        description="Retrieve a list of modules associated with a given course slug.",
        parameters=[
            OpenApiParameter(name="slug", location=OpenApiParameter.PATH,
                             required=True, description="The unique identifier of the course.", type=str)
        ],
        responses={200: ModuleSerializer(many=True), 404: {"description": "Course not found"}},
        tags=["module"]
    )
    def get(self, request, slug: str = None):
        course = get_object_or_404(Course, slug=slug)
        self.check_object_permissions(request, course.owner)
        course_modules_serializer = ModuleSerializer(instance=course.modules, many=True)
        return Response(data=course_modules_serializer.data, status=status.HTTP_200_OK)


class ModuleCreateView(APIView):
    serializer_class = ModuleSerializer
    permission_classes = [IsAuthenticated, IsInstructor]
    @extend_schema(
        summary="Create a module",
        description="Create a new module within a specific course.",
        parameters=[
            OpenApiParameter(name="slug", location=OpenApiParameter.PATH,
                             required=True, description="The unique identifier of the course.", type=str)
        ],
        request=ModuleSerializer,
        responses={201: ModuleSerializer, 400: {"description": "Invalid input data"},
                   404: {"description": "Course not found"}},
        tags=["module"]
    )
    def post(self, request, slug: str):
        course = get_object_or_404(Course, slug=slug)
        serializer = ModuleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(course=course)
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ModuleViewSet(ViewSet):
    serializer_class = ModuleSerializer
    permission_classes = [IsAuthenticated, IsInstructor, IsOwner]
    lookup_field = "slug"

    @extend_schema(
        summary="Retrieve a module",
        description="Fetch details of a specific module using its slug.",
        parameters=[
            OpenApiParameter(name="slug", location=OpenApiParameter.PATH,
                             required=True, description="The unique identifier of the module.", type=str)
        ],
        responses={200: ModuleSerializer, 404: {"description": "Module not found"}},
        tags=["module"]
    )
    def retrieve(self, request, slug: str = None):
        module = get_object_or_404(Module, slug=slug)
        module_serializer = ModuleSerializer(instance=module)
        return Response(data=module_serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Update a module",
        description="Update an existing module using its slug.",
        parameters=[
            OpenApiParameter(name="slug", location=OpenApiParameter.PATH,
                             required=True, description= "The unique identifier of the module.", type=str)
        ],
        request=ModuleSerializer,
        responses={200: ModuleSerializer, 400: {"description": "Invalid input data"},
                   403: {"description": "Permission denied"}, 404: {"description": "Module not found"}},
        tags=["module"]
    )
    def update(self, request, slug: str = None):
        module = get_object_or_404(Module, slug=slug)
        self.check_object_permissions(request, module.course.owner)
        module_serializer = ModuleSerializer(instance=module, data=request.data, partial=True)
        if module_serializer.is_valid():
            module_serializer.save()
            return Response(data=module_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(data=module_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Delete a module",
        description="Delete a specific module using its slug.",
        parameters=[
            OpenApiParameter(name="slug", location=OpenApiParameter.PATH, required=True,
                             description="The unique identifier of the module.", type=str)
        ],
        responses={204: {"description": "Module deleted successfully"}, 403: {"description": "Permission denied"},
                   404: {"description": "Module not found"}},
        tags=["module"]
    )
    def destroy(self, request, slug: str = None):
        module = get_object_or_404(Module, slug=slug)
        self.check_object_permissions(request, module.course.owner)
        module.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
