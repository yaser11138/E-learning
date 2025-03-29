from django.shortcuts import render
from dj_rest_auth.registration.views import RegisterView
from .serializers import StudentRegisterSerializer


class studentRegistrationView(RegisterView):
    serializer_class = StudentRegisterSerializer
