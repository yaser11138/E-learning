from rest_framework import serializers
from courses.models import (
    Subject,
    Content,
    Module,
    Course,
    VideoContent,
    TextContent,
    FileContent,
    ImageContent,
    ContentProgress,
    CourseProgress,
    CourseMedia,
)
from rest_polymorphic.serializers import PolymorphicSerializer


class VideoContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoContent
        fields = "__all__"
        extra_kwargs = {"module": {"read_only": True}}


class ImageContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageContent
        fields = "__all__"
        extra_kwargs = {"module": {"read_only": True}}


class FileContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileContent
        fields = "__all__"
        extra_kwargs = {"module": {"read_only": True}}


class TextContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TextContent
        fields = "__all__"
        extra_kwargs = {"module": {"read_only": True}}


class ContentSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        VideoContent: VideoContentSerializer,
        ImageContent: ImageContentSerializer,
        TextContent: TextContentSerializer,
        FileContent: FileContentSerializer,
    }


class ModuleSerializer(serializers.ModelSerializer):
    contents = serializers.HyperlinkedRelatedField(
        many=True, read_only=True, view_name="content-detail", lookup_field="slug"
    )

    class Meta:
        model = Module
        fields = ["order", "slug", "title", "description", "contents"]
        extra_kwargs = {"order": {"read_only": True}, "slug": {"read_only": True}}


class CourseSerializer(serializers.ModelSerializer):
    modules = ModuleSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        exclude = ["slug", "owner"]


class CourseListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = "__all__"


class SubjectListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ["id", "title", "slug"]


class SubjectSerializer(serializers.ModelSerializer):
    courses = CourseSerializer(many=True, read_only=True)

    class Meta:
        model = Subject
        fields = "__all__"


class ContentProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentProgress
        fields = ["id", "content", "completed", "completed_at", "last_position"]
        read_only_fields = ["completed_at"]


class CourseProgressSerializer(serializers.ModelSerializer):
    progress_percentage = serializers.FloatField(read_only=True)

    class Meta:
        model = CourseProgress
        fields = [
            "id",
            "course",
            "started_at",
            "last_accessed",
            "completed",
            "completed_at",
            "progress_percentage",
        ]
        read_only_fields = [
            "started_at",
            "last_accessed",
            "completed_at",
            "progress_percentage",
        ]


class CourseMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseMedia
        fields = [
            "id",
            "title",
            "description",
            "media_type",
            "file_url",
            "thumbnail_url",
            "duration",
            "size",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "file_url",
            "thumbnail_url",
            "duration",
            "size",
            "created_at",
            "updated_at",
        ]


class CourseMediaUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    title = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False, allow_blank=True)
    media_type = serializers.ChoiceField(choices=CourseMedia.MEDIA_TYPES)
