from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from dj_rest_auth.registration.views import RegisterView
from .serializers import StudentRegisterSerializer, StudentProfileSerializer, InstructorProfileSerializer
from drf_spectacular.utils import extend_schema, OpenApiExample


User = get_user_model()


class studentRegistrationView(RegisterView):
    serializer_class = StudentRegisterSerializer


class ProfileViewUpdate(APIView):
    permission_classes = [IsAuthenticated]

    def _get_user_serializer(self, user):
        """Helper method to determine correct serializer"""
        if hasattr(user, "student"):
            return StudentProfileSerializer
        elif hasattr(user, "instructor"):
            return InstructorProfileSerializer
        return None

    @extend_schema(
        summary="Retrieve profile",
        description="Returns the current user's profile information",
        responses={
            200: StudentProfileSerializer,
        },
        tags=["Profile"]
    )
    def get(self, request):
        user = request.user
        serializer_class = self._get_user_serializer(user)
        if serializer_class is None:
            return Response(
                {"error": "User is neither a student nor an instructor"},
                status=status.HTTP_400_BAD_REQUEST
            )
        user_serializer = serializer_class(instance=user)
        return Response(data=user_serializer.data,status=status.HTTP_200_OK)

    @extend_schema(
        summary="Update profile",
        description="Updates the current user's profile information",
        examples=[
            OpenApiExample(
                "Student update",
                value={
                    "first_name": "John",
                    "last_name": "Smith",
                    "student": {"phone_number": 1234567890}
                },
            ),
            OpenApiExample(
                "Instructor update",
                value={
                    "first_name": "Dr. John",
                    "last_name": "Smith",
                    "instructor": {"bio": "some text"}
                },
            ),
        ],
        tags=["Profile"]
    )
    def put(self, request):
        user = request.user
        serializer_class = self._get_user_serializer(user)

        if serializer_class is None:
            return Response(
                {"error": "User is neither a student nor an instructor"},
                status=status.HTTP_400_BAD_REQUEST
            )
        user_serializer = serializer_class(instance=user, data=request.data, partial=True)
        if user_serializer.is_valid():
            user_serializer.save()
            return Response(user_serializer.data)
        return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

