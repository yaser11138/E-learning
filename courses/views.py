from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.types import OpenApiTypes
from .serializers import CourseSerializer, ModuleSerializer, ContentSerializer
from .permissions import IsInstructor, IsOwner
from .models import Course, Module, Content


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
        summary="Partial Update an existing course",
        description="Updates the course with the given slug",
        request=CourseSerializer,
        responses={200: CourseSerializer, 400: OpenApiTypes.OBJECT},
        tags=["course"]
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

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
        self.check_object_permissions(request, course)
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
        self.check_object_permissions(request, module.course)
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
        self.check_object_permissions(request, module.course)
        module.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ContentViewListCreate(APIView):
    permission_classes = [IsAuthenticated, IsOwner, IsInstructor]
    parser_classes = (MultiPartParser, FormParser)

    @extend_schema(
        summary="List module contents",
        description="Get all contents for a specific module",
        responses={
            200: ContentSerializer(many=True),
            404: {"type": "object", "properties": {"detail": {"type": "string"}}}
        },
        parameters=[
            OpenApiParameter(
                name="module_slug",
                location=OpenApiParameter.PATH,
                description="Unique slug identifier of the module",
                required=True,
                type=str
            )
        ],
        tags=["contents"]
    )
    def get(self, request, module_slug):
        module = get_object_or_404(Module, slug=module_slug)
        contents = module.contents.all()
        serializer = ContentSerializer(instance=contents, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Create module content",
        description="Create a new content item for a specific module. Use multipart/form-data for file uploads.",
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'title': {
                        'type': 'string',
                        'description': 'Title of the content'
                    },
                    'is_free': {
                        'type': 'boolean',
                        'description': 'Whether the content is free to access'
                    },
                    'resource_type': {
                        'type': 'string',
                        'description': 'Type of resource',
                        'enum': ['text', 'video', 'image', 'file']
                    },
                    'text': {
                        'type': 'string',
                        'description': 'Text content if resource_type is text'
                    },
                    'video_file': {
                        'type': 'string',
                        'format': 'binary',
                        'description': 'Video file if resource_type is video'
                    },
                    'image': {
                        'type': 'string',
                        'format': 'binary',
                        'description': 'Image file if resource_type is image'
                    },
                    'file': {
                        'type': 'string',
                        'format': 'binary',
                        'description': 'Document file if resource_type is file'
                    }
                },
                'required': ['title', 'resource_type']
            }
        },
        responses={
            201: ContentSerializer,
            400: {"type": "object", "properties": {"detail": {"type": "string"}}},
            404: {"type": "object", "properties": {"detail": {"type": "string"}}}
        },
        parameters=[
            OpenApiParameter(
                name="module_slug",
                location=OpenApiParameter.PATH,
                description="Unique slug identifier of the module",
                required=True,
                type=str
            )
        ],
        examples=[
            OpenApiExample(
                "Text Content Example",
                summary="Example request for text content",
                value={
                    "title": "Introduction to Python",
                    "description": "Basic Python concepts",
                    "content_type": "text",
                    "text_content": "Python is a high-level programming language...",
                    "order": 1
                },
                request_only=True,
            ),
            OpenApiExample(
                "File Upload Example",
                summary="Example request for file upload",
                value={
                    "title": "Python Tutorial PDF",
                    "description": "Comprehensive Python guide",
                    "content_type": "file",
                    "order": 2
                    # file field would be submitted as actual file
                },
                request_only=True,
            ),
        ],
        tags=["contents"]
    )
    def post(self, request, module_slug):
        module = get_object_or_404(Module, slug=module_slug)
        serializer = ContentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(module=module)
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ContentDetailView(ViewSet):
    """ViewSet for content details operations"""

    parser_classes = [MultiPartParser, FormParser]
    serializer_class = ContentSerializer
    lookup_field = "slug"

    def get_permissions(self):
        if self.action == "retrieve":
            return [IsAuthenticated()]
        elif self.action in ["partial_update", "destroy"]:
            return [IsAuthenticated(), IsInstructor(), IsOwner()]
        return [IsAuthenticated()]

    @extend_schema(
        summary="Retrieve content details",
        description="Get details of a specific content item by slug",
        parameters=[
            OpenApiParameter(
                name="slug",
                location=OpenApiParameter.PATH,
                description="Unique slug identifier of the content",
                required=True,
                type=str
            )
        ],
        responses={
            200: ContentSerializer,
            404: {"type": "object", "properties": {"detail": {"type": "string"}}}
        },
        tags=["contents"]
    )
    def retrieve(self, request, slug=None):
        content = get_object_or_404(Content, slug=slug)
        serializer = ContentSerializer(instance=content)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Update content",
        description="Update a specific content item. Use multipart/form-data for file uploads.",
        parameters=[
            OpenApiParameter(
                name="slug",
                location=OpenApiParameter.PATH,
                description="Unique slug identifier of the content",
                required=True,
                type=str
            )
        ],
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'title': {
                        'type': 'string',
                        'description': 'Title of the content'
                    },
                    'description': {
                        'type': 'string',
                        'description': 'Description of the content'
                    },
                    'is_free': {
                        'type': 'boolean',
                        'description': 'Whether the content is free to access'
                    },
                    'resourcetype': {
                        'type': 'string',
                        'description': 'Type of resource',
                        'enum': ['TextContent', 'VideoContent', 'ImageContent', 'FileContent']
                    },
                    'text': {
                        'type': 'string',
                        'description': 'Text content if resourcetype is text'
                    },
                    'video_file': {
                        'type': 'string',
                        'format': 'binary',
                        'description': 'Video file if resourcetype is video'
                    },
                    'image': {
                        'type': 'string',
                        'format': 'binary',
                        'description': 'Image file if resourcetype is image'
                    },
                    'file': {
                        'type': 'string',
                        'format': 'binary',
                        'description': 'Document file if resourcetype is file'
                    },
                    'order': {
                        'type': 'integer',
                        'description': 'Order position of the content'
                    }
                }
            }
        },
        responses={
            200: ContentSerializer,
            400: {"type": "object", "properties": {"detail": {"type": "string"}}},
            403: {"type": "object", "properties": {"detail": {"type": "string"}}},
            404: {"type": "object", "properties": {"detail": {"type": "string"}}}
        },
        tags=["contents"]
    )
    def partial_update(self, request, slug=None):
        content = get_object_or_404(Content, slug=slug)
        self.check_object_permissions(request, content.module.course)
        serializer = ContentSerializer(data=request.data, instance=content, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Delete content",
        description="Delete a specific content item",
        parameters=[
            OpenApiParameter(
                name="slug",
                location=OpenApiParameter.PATH,
                description="Unique slug identifier of the content",
                required=True,
                type=str
            )
        ],
        responses={
            204: None,
            403: {"type": "object", "properties": {"detail": {"type": "string"}}},
            404: {"type": "object", "properties": {"detail": {"type": "string"}}}
        },
        tags=["contents"]
    )
    def destroy(self, request, slug=None):
        content = get_object_or_404(Content, slug=slug)
        self.check_object_permissions(request, content.module.course)
        content.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)





