from dj_rest_auth.registration.serializers import RegisterSerializer

from rest_framework import  serializers
from .models import Student


class StudentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Student
        fields = ['birth_date', 'education', 'phone_number']
        

class StudentRegisterSerializer(RegisterSerializer):
    first_name = serializers.CharField(max_length=10)
    last_name = serializers.CharField(max_length=10)
    student = StudentSerializer()

    def save(self, request):
        user = super().save(request)
        student_data = self.validated_data["student"]
        Student.objects.create(user=user,**student_data)
        return user
