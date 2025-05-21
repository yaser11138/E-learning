from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiParameter,
    OpenApiExample,
    OpenApiResponse,
)
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.types import OpenApiTypes
from .serializers import (
    CourseSerializer,
    ModuleSerializer,
    ContentSerializer,
    CourseProgressSerializer,
    ContentProgressSerializer,
    CourseMediaSerializer,
)
from core.permissions import IsInstructor, IsOwner, IsStudent
from .models import (
    Course,
    Module,
    Content,
    CourseProgress,
    ContentProgress,
    CourseMedia,
)
from .utils import validate_file, upload_file_to_cloudinary, delete_file_from_cloudinary


@extend_schema_view(
    list=extend_schema(tags=["courses"]),
    create=extend_schema(tags=["courses"]),
    retrieve=extend_schema(tags=["courses"]),
    update=extend_schema(tags=["courses"]),
    partial_update=extend_schema(tags=["courses"]),
    destroy=extend_schema(tags=["courses"]),
)
class CourseViewSet(ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAuthenticated, IsInstructor, IsOwner]
    lookup_field = "slug"

    @extend_schema(
        summary="Create a new course",
        description="Creates a new course with the provided data, including file uploads",
        request={"multipart/form-data": CourseSerializer},
        responses={201: CourseSerializer, 400: OpenApiTypes.OBJECT},
    )
    def create(self, request, *args, **kwargs):
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
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        summary="Partial Update an existing course",
        description="Updates the course with the given slug",
        request=CourseSerializer,
        responses={200: CourseSerializer, 400: OpenApiTypes.OBJECT},
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(
        summary="Delete a course",
        description="Deletes the course with the given slug",
        responses={200: OpenApiTypes.OBJECT, 404: OpenApiTypes.OBJECT},
    )
    def destroy(self, request, *args, **kwargs):
        course = self.get_object()
        title = course.title
        self.perform_destroy(course)
        return Response(
            {"message": f"{title} successfully deleted"}, status=status.HTTP_200_OK
        )


@extend_schema_view(
    get=extend_schema(tags=["courses"]),
)
class ModuleListView(APIView):
    serializer_class = ModuleSerializer
    permission_classes = [IsAuthenticated, IsInstructor, IsOwner]

    @extend_schema(
        summary="List all modules in a course",
        description="Retrieve a list of modules associated with a given course slug.",
        parameters=[
            OpenApiParameter(
                name="slug",
                location=OpenApiParameter.PATH,
                required=True,
                description="The unique identifier of the course.",
                type=str,
            )
        ],
        responses={
            200: ModuleSerializer(many=True),
            404: {"description": "Course not found"},
        },
    )
    def get(self, request, slug: str = None):
        course = get_object_or_404(Course, slug=slug)
        self.check_object_permissions(request, course)
        course_modules_serializer = ModuleSerializer(instance=course.modules, many=True)
        return Response(data=course_modules_serializer.data, status=status.HTTP_200_OK)


@extend_schema_view(
    post=extend_schema(tags=["courses"]),
)
class ModuleCreateView(APIView):
    serializer_class = ModuleSerializer
    permission_classes = [IsAuthenticated, IsInstructor]

    @extend_schema(
        summary="Create a module",
        description="Create a new module within a specific course.",
        parameters=[
            OpenApiParameter(
                name="slug",
                location=OpenApiParameter.PATH,
                required=True,
                description="The unique identifier of the course.",
                type=str,
            )
        ],
        request=ModuleSerializer,
        responses={
            201: ModuleSerializer,
            400: {"description": "Invalid input data"},
            404: {"description": "Course not found"},
        },
    )
    def post(self, request, slug: str):
        course = get_object_or_404(Course, slug=slug)
        serializer = ModuleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(course=course)
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    retrieve=extend_schema(tags=["courses"]),
    update=extend_schema(tags=["courses"]),
    destroy=extend_schema(tags=["courses"]),
)
class ModuleViewSet(ViewSet):
    serializer_class = ModuleSerializer
    permission_classes = [IsAuthenticated, IsInstructor, IsOwner]
    lookup_field = "slug"

    @extend_schema(
        summary="Retrieve a module",
        description="Fetch details of a specific module using its slug.",
        parameters=[
            OpenApiParameter(
                name="slug",
                location=OpenApiParameter.PATH,
                required=True,
                description="The unique identifier of the module.",
                type=str,
            )
        ],
        responses={200: ModuleSerializer, 404: {"description": "Module not found"}},
    )
    def retrieve(self, request, slug: str = None):
        module = get_object_or_404(Module, slug=slug)
        module_serializer = ModuleSerializer(instance=module)
        return Response(data=module_serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Update a module",
        description="Update an existing module using its slug.",
        parameters=[
            OpenApiParameter(
                name="slug",
                location=OpenApiParameter.PATH,
                required=True,
                description="The unique identifier of the module.",
                type=str,
            )
        ],
        request=ModuleSerializer,
        responses={
            200: ModuleSerializer,
            400: {"description": "Invalid input data"},
            403: {"description": "Permission denied"},
            404: {"description": "Module not found"},
        },
    )
    def update(self, request, slug: str = None):
        module = get_object_or_404(Module, slug=slug)
        self.check_object_permissions(request, module.course)
        module_serializer = ModuleSerializer(
            instance=module, data=request.data, partial=True
        )
        if module_serializer.is_valid():
            module_serializer.save()
            return Response(data=module_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(
                data=module_serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

    @extend_schema(
        summary="Delete a module",
        description="Delete a specific module using its slug.",
        parameters=[
            OpenApiParameter(
                name="slug",
                location=OpenApiParameter.PATH,
                required=True,
                description="The unique identifier of the module.",
                type=str,
            )
        ],
        responses={
            204: {"description": "Module deleted successfully"},
            403: {"description": "Permission denied"},
            404: {"description": "Module not found"},
        },
    )
    def destroy(self, request, slug: str = None):
        module = get_object_or_404(Module, slug=slug)
        self.check_object_permissions(request, module.course)
        module.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# Resource type to file field mapping
RESOURCE_TYPE_MAPPING = {
    "VideoContent": "video_file",
    "ImageContent": "image_file",
    "FileContent": "file",
    "TextContent": None,
}

@extend_schema_view(
    get=extend_schema(tags=["content"]),
    post=extend_schema(tags=["content"]),
)
class ContentViewListCreate(APIView):
    permission_classes = [IsAuthenticated, IsOwner, IsInstructor]
    parser_classes = (MultiPartParser, FormParser)



    @extend_schema(
        summary="List module contents",
        description="Get all contents for a specific module",
        responses={
            200: ContentSerializer(many=True),
            404: {"type": "object", "properties": {"detail": {"type": "string"}}},
        },
        parameters=[
            OpenApiParameter(
                name="module_slug",
                location=OpenApiParameter.PATH,
                description="Unique slug identifier of the module",
                required=True,
                type=str,
            )
        ],
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
            "multipart/form-data": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Title of the content"},
                    "is_free": {
                        "type": "boolean",
                        "description": "Whether the content is free to access",
                    },
                    "resourcetype": {
                        "type": "string",
                        "description": "Type of resource",
                        "enum": [
                            "TextContent",
                            "VideoContent",
                            "ImageContent",
                            "FileContent",
                        ],
                    },
                    "text": {
                        "type": "string",
                        "description": "Text content if resourcetype is text",
                    },
                    "video_file": {
                        "type": "string",
                        "format": "binary",
                        "description": "Video file if resourcetype is video",
                    },
                    "image_file": {
                        "type": "string",
                        "format": "binary",
                        "description": "Image file if resourcetype is image",
                    },
                    "file": {
                        "type": "string",
                        "format": "binary",
                        "description": "Document file if resourcetype is file",
                    },
                },
                "required": ["title", "resourcetype"],
            }
        },
        responses={
            201: ContentSerializer,
            400: {"type": "object", "properties": {"detail": {"type": "string"}}},
            404: {"type": "object", "properties": {"detail": {"type": "string"}}},
        },
        parameters=[
            OpenApiParameter(
                name="module_slug",
                location=OpenApiParameter.PATH,
                description="Unique slug identifier of the module",
                required=True,
                type=str,
            )
        ],
    )
    def post(self, request, module_slug):
        module = get_object_or_404(Module, slug=module_slug)
        resource_type = request.data.get("resourcetype")

        # Check if it's a file-based content
        if resource_type in RESOURCE_TYPE_MAPPING:
            file_field = RESOURCE_TYPE_MAPPING[resource_type]

            if file_field:  # Skip for TextContent
                file = request.FILES.get(file_field)
                if not file:
                    return Response(
                        {"error": f"{file_field} is required"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                # Validate file
                is_valid, error_message = validate_file(file)
                if not is_valid:
                    return Response(
                        {"error": error_message}, status=status.HTTP_400_BAD_REQUEST
                    )

                # Upload to Cloudinary
                upload_result = upload_file_to_cloudinary(file)
                if not upload_result:
                    return Response(
                        {"error": "Failed to upload file"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                # Add Cloudinary data to request data
                request.data[file_field] = upload_result["url"]
                request.data["public_id"] = upload_result["public_id"]

                # Add specific fields based on content type
                if resource_type == "VideoContent":
                    request.data["thumbnail_url"] = upload_result.get("thumbnail_url")
                elif resource_type == "FileContent":
                    request.data["file_size"] = file.size

        serializer = ContentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(module=module)
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    retrieve=extend_schema(tags=["content"]),
    partial_update=extend_schema(tags=["content"]),
    destroy=extend_schema(tags=["content"]),
)
class ContentDetailView(ViewSet):
    parser_classes = [MultiPartParser, FormParser]
    serializer_class = ContentSerializer
    lookup_field = "slug"
    permission_classes = [IsAuthenticated, IsInstructor, IsOwner]

    @extend_schema(
        summary="Retrieve content details",
        description="Get details of a specific content item by slug",
        parameters=[
            OpenApiParameter(
                name="slug",
                location=OpenApiParameter.PATH,
                description="Unique slug identifier of the content",
                required=True,
                type=str,
            )
        ],
        responses={
            200: ContentSerializer,
            404: {"type": "object", "properties": {"detail": {"type": "string"}}},
        },
    )
    def retrieve(self, request, slug=None):
        content = get_object_or_404(Content, slug=slug)
        self.check_object_permissions(request, content.module.course)
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
                type=str,
            )
        ],
        request={
            "multipart/form-data": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Title of the content"},
                    "description": {
                        "type": "string",
                        "description": "Description of the content",
                    },
                    "is_free": {
                        "type": "boolean",
                        "description": "Whether the content is free to access",
                    },
                    "resourcetype": {
                        "type": "string",
                        "description": "Type of resource",
                        "enum": [
                            "TextContent",
                            "VideoContent",
                            "ImageContent",
                            "FileContent",
                        ],
                    },
                    "text": {
                        "type": "string",
                        "description": "Text content if resourcetype is text",
                    },
                    "video_file": {
                        "type": "string",
                        "format": "binary",
                        "description": "Video file if resourcetype is video",
                    },
                    "image": {
                        "type": "string",
                        "format": "binary",
                        "description": "Image file if resourcetype is image",
                    },
                    "file": {
                        "type": "string",
                        "format": "binary",
                        "description": "Document file if resourcetype is file",
                    },
                    "order": {
                        "type": "integer",
                        "description": "Order position of the content",
                    },
                },
            }
        },
        responses={
            200: ContentSerializer,
            400: {"type": "object", "properties": {"detail": {"type": "string"}}},
            403: {"type": "object", "properties": {"detail": {"type": "string"}}},
            404: {"type": "object", "properties": {"detail": {"type": "string"}}},
        },
    )
    def partial_update(self, request, slug=None):
        content = get_object_or_404(Content, slug=slug)
        self.check_object_permissions(request, content.module.course)

        # Handle file updates if a new file is provided
        if content.resourcetype in ("VideoContent" , "ImageContent", "FileContent"):
            file_field = RESOURCE_TYPE_MAPPING[content.resourcetype]
            file = request.FILES.get(file_field)

            if file:
                # Validate file
                is_valid, error_message = validate_file(file)
                if not is_valid:
                    return Response(
                        {"error": error_message}, status=status.HTTP_400_BAD_REQUEST
                    )

                # Delete old file from Cloudinary
                delete_file_from_cloudinary(content.public_id)

                # Upload new file to Cloudinary
                upload_result = upload_file_to_cloudinary(file)
                if not upload_result:
                    return Response(
                        {"error": "Failed to upload file"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                # Add Cloudinary data to request data
                request.data[file_field] = upload_result["url"]
                request.data["public_id"] = upload_result["public_id"]
                if content.resourcetype == "VideoContent":
                    request.data["thumbnail_url"] = upload_result.get("thumbnail_url")
                elif content.resourcetype == "FileContent":
                    request.data["file_size"] = file.size

        serializer = ContentSerializer(
            data=request.data, instance=content, partial=True
        )
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
                type=str,
            )
        ],
        responses={
            204: None,
            403: {"type": "object", "properties": {"detail": {"type": "string"}}},
            404: {"type": "object", "properties": {"detail": {"type": "string"}}},
        },
    )
    def destroy(self, request, slug=None):
        content = get_object_or_404(Content, slug=slug)
        self.check_object_permissions(request, content.module.course)
        content.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema_view(
    retrieve=extend_schema(tags=["courses"]),
    list=extend_schema(tags=["courses"]),
)
class StudentCourseView(ViewSet):
    permission_classes = [IsAuthenticated, IsStudent]
    lookup_field = "slug"

    @extend_schema(
        summary="Retrieve a specific course",
        description="Get detailed information about a course by its slug",
        parameters=[
            OpenApiParameter(
                name="slug",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                description="Unique slug identifier of the course",
            ),
        ],
        responses={
            status.HTTP_200_OK: CourseSerializer,
            status.HTTP_404_NOT_FOUND: OpenApiResponse(description="Course not found"),
            status.HTTP_403_FORBIDDEN: OpenApiResponse(description="Not authorized"),
        },
    )
    def retrieve(self, request, slug):
        course = get_object_or_404(Course, slug=slug)
        course_serializer = CourseSerializer(
            instance=course, context={"request": request}
        )
        return Response(data=course_serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="List all courses",
        description="Get a list of all available courses",
        responses={
            status.HTTP_200_OK: CourseSerializer(many=True),
            status.HTTP_403_FORBIDDEN: OpenApiResponse(description="Not authorized"),
        },
    )
    def list(self, request):
        courses = Course.objects.all()
        course_serializer = CourseSerializer(
            instance=courses, many=True, context={"request": request}
        )
        return Response(data=course_serializer.data, status=status.HTTP_200_OK)


@extend_schema_view(
    get=extend_schema(tags=["content"]),
)
class StudentContentView(APIView):
    permission_classes = [IsAuthenticated, IsStudent]

    @extend_schema(
        summary="Retrieve course content",
        description="Get detailed information about specific content by its slug",
        parameters=[
            OpenApiParameter(
                name="slug",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                description="Unique slug identifier of the content",
            ),
        ],
        responses={
            status.HTTP_200_OK: ContentSerializer,
            status.HTTP_404_NOT_FOUND: OpenApiResponse(description="Content not found"),
            status.HTTP_403_FORBIDDEN: OpenApiResponse(description="Not authorized"),
        },
    )
    def get(self, request, slug=None):
        content = get_object_or_404(Content, slug=slug)
        content_serializer = ContentSerializer(instance=content)
        return Response(data=content_serializer.data, status=status.HTTP_200_OK)


@extend_schema_view(
    get=extend_schema(tags=["progress"]),
)
class CourseProgressView(APIView):
    permission_classes = [IsAuthenticated, IsStudent]

    @extend_schema(
        summary="Get course progress",
        description="Get progress information for a specific course",
        parameters=[
            OpenApiParameter(
                name="slug",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                description="Unique slug identifier of the course",
            ),
        ],
        responses={
            status.HTTP_200_OK: CourseProgressSerializer,
            status.HTTP_404_NOT_FOUND: OpenApiResponse(description="Course not found"),
        },
    )
    def get(self, request, slug):
        course = get_object_or_404(Course, slug=slug)
        progress, created = CourseProgress.objects.get_or_create(
            student=request.user, course=course
        )
        serializer = CourseProgressSerializer(progress)
        return Response(serializer.data)


@extend_schema_view(
    get=extend_schema(tags=["progress"]),
    post=extend_schema(tags=["progress"]),
)
class ContentProgressView(APIView):
    permission_classes = [IsAuthenticated, IsStudent]

    @extend_schema(
        summary="Get content progress",
        description="Get progress information for specific content",
        parameters=[
            OpenApiParameter(
                name="slug",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                description="Unique slug identifier of the content",
            ),
        ],
        responses={
            status.HTTP_200_OK: ContentProgressSerializer,
            status.HTTP_404_NOT_FOUND: OpenApiResponse(description="Content not found"),
        },
    )
    def get(self, request, slug):
        content = get_object_or_404(Content, slug=slug)
        progress, created = ContentProgress.objects.get_or_create(
            student=request.user, content=content
        )
        serializer = ContentProgressSerializer(progress)
        return Response(serializer.data)

    @extend_schema(
        summary="Update content progress",
        description="Update progress for specific content",
        parameters=[
            OpenApiParameter(
                name="slug",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                description="Unique slug identifier of the content",
            ),
        ],
        request=ContentProgressSerializer,
        responses={
            status.HTTP_200_OK: ContentProgressSerializer,
            status.HTTP_404_NOT_FOUND: OpenApiResponse(description="Content not found"),
        },
    )
    def post(self, request, slug):
        content = get_object_or_404(Content, slug=slug)
        progress, created = ContentProgress.objects.get_or_create(
            student=request.user, content=content
        )

        if request.data.get("completed"):
            progress.mark_as_completed()
        elif "last_position" in request.data:
            progress.last_position = request.data["last_position"]
            progress.save()

        serializer = ContentProgressSerializer(progress)
        return Response(serializer.data)


class CourseMediaViewSet(ModelViewSet):
    """ViewSet for handling course media files."""

    serializer_class = CourseMediaSerializer
    permission_classes = [IsAuthenticated, IsInstructor, IsOwner]

    def get_queryset(self):
        return CourseMedia.objects.filter(course_id=self.kwargs["course_pk"])

    def perform_create(self, serializer):
        course = get_object_or_404(Course, id=self.kwargs["course_pk"])
        file = self.request.FILES.get("file")

        # Validate file
        is_valid, error_message = validate_file(file)
        if not is_valid:
            raise self.serializer_class.ValidationError(error_message)

        # Upload to Cloudinary
        upload_result = upload_file_to_cloudinary(file)
        if not upload_result:
            raise self.serializer_class.ValidationError("Failed to upload file")

        # Create media object
        serializer.save(
            course=course,
            file_url=upload_result["url"],
            public_id=upload_result["public_id"],
            size=file.size,
        )

    def perform_destroy(self, instance):
        # The delete method in the model will handle Cloudinary deletion
        instance.delete()
