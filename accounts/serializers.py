from django.contrib.auth import get_user_model
from rest_framework import  serializers
from dj_rest_auth.registration.serializers import RegisterSerializer
from .models import Student,Instructor

User = get_user_model()


class StudentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Student
        fields = ['birth_date', 'education', 'phone_number']
        

class InstructorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instructor
        fields = ["bio", "education"]


class StudentRegisterSerializer(RegisterSerializer):
    first_name = serializers.CharField(max_length=10)
    last_name = serializers.CharField(max_length=10)
    student = StudentSerializer()

    def save(self, request):
        user = super().save(request)
        student_data = self.validated_data["student"]
        Student.objects.create(user=user, **student_data)
        return user


class StudentProfileSerializer(serializers.ModelSerializer):
    student = StudentSerializer()

    class Meta:
        model = User
        fields = ["first_name", "last_name", "student"]

    def update(self, instance, validated_data):
        student_data = validated_data.pop("student")
        if hasattr(instance, "student"):
            student = instance.student
        else:
            return serializers.ValidationError("the instance doesn't have student attribute")
        for attr in validated_data:
            setattr(instance,attr,validated_data[attr])

        for attr in student_data:
            setattr(student, attr, student_data[attr])

        return instance


class InstructorProfileSerializer(serializers.ModelSerializer):
    instructor = InstructorSerializer()

    class Meta:
        model = User
        fields = ["first_name", "last_name", "instructor"]

    def update(self, instance, validated_data):
        student_data = validated_data.pop("instructor")
        if hasattr(instance, "instructor"):
            student = instance.student
        else:
            return serializers.ValidationError("the instance doesn't have instructor attribute")
        for attr in validated_data:
            setattr(instance,attr,validated_data[attr])

        for attr in student_data:
            setattr(student, attr, student_data[attr])

        return instance
