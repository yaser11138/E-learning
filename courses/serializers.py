from rest_framework import serializers
from courses.models import Subject, Content, Module, Course


class ContentSerializer(serializers.ModelSerializer):
    contents = serializers.SerializerMethodField()

    class Meta:
        model = Content
        fields = ["order", "is_free", "contents"]

    def get_contents(self, obj):
        contents = {}
        if obj.text_content is not None:
            contents["text"] = obj.text_content
        if obj.image_content is not None:
            contents["image"] = obj.image_content
        if obj.video_content is not None:
            contents["video"] = obj.video_content
        if obj.file_content is not None:
            contents["file"] = obj.file_content
        return contents


class ContentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Content
        fields = ["order", "is_free", "slug"]


class ModuleSerializer(serializers.ModelSerializer):
    contents = ContentListSerializer(many=True, read_only=True)

    class Meta:
        model = Module
        fields = ["order", "title", "description", "contents"]


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
