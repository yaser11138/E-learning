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
        user.first_name = self.validated_data["first_name"]
        user.last_name = self.validated_data["last_name"]
        user.save()
        student_data = self.validated_data["student"]
        Student.objects.create(user=user, **student_data)
        return user


class StudentProfileSerializer(serializers.ModelSerializer):
    student = StudentSerializer()
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["first_name", "last_name", "student", "role"]

    def get_role(self, obj):
        return 'student'

    def update(self, instance, validated_data):
        student_data = validated_data.pop("student")
        if hasattr(instance, "student"):
            student = instance.student
        else:
            raise serializers.ValidationError("the instance doesn't have student attribute")
        for attr in validated_data:
            setattr(instance, attr, validated_data[attr])
        instance.save()
        for attr in student_data:
            setattr(student, attr, student_data[attr])
        student.save()
        return instance


class InstructorProfileSerializer(serializers.ModelSerializer):
    instructor = InstructorSerializer()
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["first_name", "last_name", "instructor", "role"]

    def get_role(self, obj):
        return 'Instructor'

    def update(self, instance, validated_data):
        instructor_data = validated_data.pop("instructor")
        if hasattr(instance, "instructor"):
            instructor = instance.instructor
        else:
            raise serializers.ValidationError("the instance doesn't have instructor attribute")
        for attr in validated_data:
            setattr(instance, attr, validated_data[attr])
        instance.save()

        for attr in instructor_data:
            setattr(instructor, attr, instructor_data[attr])
        instructor.save()
        return instance
