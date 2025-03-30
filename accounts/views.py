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

    def _get_user_serializer(self, user, data=None, partial=False):
        """Helper method to determine correct serializer"""
        if hasattr(user, "student"):
            return StudentProfileSerializer(instance=user, data=data, partial=partial)
        elif hasattr(user, "instructor"):
            return InstructorProfileSerializer(instance=user, data=data, partial=partial)
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
        serializer = self._get_user_serializer(user)

        if serializer is None:
            return Response(
                {"error": "User is neither a student nor an instructor"},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(serializer.data)

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
        serializer = self._get_user_serializer(user, data=request.data, partial=True)

        if serializer is None:
            return Response(
                {"error": "User is neither a student nor an instructor"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

