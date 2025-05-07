from rest_framework.serializers import ModelSerializer, SlugRelatedField
from .models import Enrollment


class EnrollmentSerializer(ModelSerializer):
    course = SlugRelatedField(read_only=True, slug_field="title")

    class Meta:
        model = Enrollment
        exclude = ('id',)