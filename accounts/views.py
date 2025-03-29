from django.shortcuts import render
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from dj_rest_auth.registration.views import RegisterView
from .serializers import StudentRegisterSerializer, StudentProfileSerializer

User = get_user_model()


class studentRegistrationView(RegisterView):
    serializer_class = StudentRegisterSerializer


class StudentProfileViewUpdate(APIView):

    def get(self, request):
        user = request.user
        user_serializer = StudentProfileSerializer(instance=user)
        return Response(data=user_serializer.data)

