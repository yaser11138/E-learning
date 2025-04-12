from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.serializers import ValidationError
from rest_framework.test import APIRequestFactory
from ..models import Student, Instructor
from ..serializers import (
    StudentSerializer,
    InstructorSerializer,
    StudentRegisterSerializer,
    StudentProfileSerializer,
    InstructorProfileSerializer
)

User = get_user_model()


class StudentSerializerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="password123",
            first_name="Test",
            last_name="User"
        )
        self.student_data = {
            "birth_date": "1995-05-15",
            "education": "PHD",
            "phone_number": "+123456789"
        }
        self.student = Student.objects.create(user=self.user, **self.student_data)

    def test_contains_expected_fields(self):
        serializer = StudentSerializer(instance=self.student)
        data = serializer.data

        self.assertCountEqual(
            data.keys(),
            ['birth_date', 'education', 'phone_number']
        )

    def test_field_content(self):
        serializer = StudentSerializer(instance=self.student)
        data = serializer.data

        self.assertEqual(data['birth_date'], self.student_data['birth_date'])
        self.assertEqual(data['education'], self.student_data['education'])
        self.assertEqual(data['phone_number'], self.student_data['phone_number'])

    def test_validation(self):
        invalid_data = {
            "birth_date": "invalid-date",
            "education": "Something Odd",
            "phone_number": "+123456789"
        }
        serializer = StudentSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('birth_date', serializer.errors)
        self.assertIn('education', serializer.errors)

class InstructorSerializerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="instructor",
            email="instructor@example.com",
            password="password123",
            first_name="John",
            last_name="Doe"
        )
        self.instructor_data = {
            "bio": "Experienced instructor with 10 years of teaching",
            "education": "PHD"
        }
        self.instructor = Instructor.objects.create(user=self.user, **self.instructor_data)

    def test_contains_expected_fields(self):
        serializer = InstructorSerializer(instance=self.instructor)
        data = serializer.data

        self.assertCountEqual(
            data.keys(),
            ['bio', 'education']
        )

    def test_field_content(self):
        serializer = InstructorSerializer(instance=self.instructor)
        data = serializer.data

        self.assertEqual(data['bio'], self.instructor_data['bio'])
        self.assertEqual(data['education'], self.instructor_data['education'])


# noinspection PyUnresolvedReferences
class StudentRegisterSerializerTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.request = self.factory.post('accounts/register/student/')
        self.request.session = dict()
        self.valid_data = {
            'username': 'newstudent',
            'email': 'student@example.com',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!',
            'first_name': 'New',
            'last_name': 'Student',
            'student': {
                'birth_date': '2000-01-01',
                'education': 'PHD',
                'phone_number': '+987654321'
            }
        }

    def test_validation(self):
        serializer = StudentRegisterSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())

    def test_first_name_max_length(self):
        invalid_data = self.valid_data.copy()
        invalid_data['first_name'] = 'VeryLongFirstName'  # More than 10 chars

        serializer = StudentRegisterSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('first_name', serializer.errors)

    def test_save_creates_user_and_student(self):
        serializer = StudentRegisterSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())

        # Set context with request cause the save method need reqeust object
        serializer.context['request'] = self.request
        user = serializer.save(self.request)
        user = User.objects.get(username="newstudent")
        print(user.first_name, self.valid_data['first_name'])
        # Verify user was created with correct data
        self.assertEqual(user.username, self.valid_data['username'])
        self.assertEqual(user.first_name, self.valid_data['first_name'])
        self.assertEqual(user.last_name, self.valid_data['last_name'])

        # Verify student was created with correct data
        student = Student.objects.get(user=user)
        self.assertEqual(student.birth_date.strftime('%Y-%m-%d'), self.valid_data['student']['birth_date'])
        self.assertEqual(student.education, self.valid_data['student']['education'])
        self.assertEqual(student.phone_number, self.valid_data['student']['phone_number'])


# noinspection PyUnresolvedReferences
class StudentProfileSerializerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="studentprofile",
            email="studentprofile@example.com",
            password="password123",
            first_name="Student",
            last_name="Profile"
        )
        self.student_data = {
            "birth_date": "1998-07-20",
            "education": "PHD",
            "phone_number": "+1122334455"
        }
        self.student = Student.objects.create(user=self.user, **self.student_data)

        self.user_without_student = User.objects.create_user(
            username="notstudent",
            email="notstudent@example.com",
            password="password123"
        )

    def test_serialization(self):
        serializer = StudentProfileSerializer(instance=self.user)
        data = serializer.data

        self.assertEqual(data['first_name'], self.user.first_name)
        self.assertEqual(data['last_name'], self.user.last_name)
        self.assertEqual(data['student']['education'], self.student_data['education'])
        self.assertEqual(data['student']['phone_number'], self.student_data['phone_number'])

    def test_update(self):
        update_data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'student': {
                'education': 'MASTERS',
                'phone_number': '+9988776655',
                'birth_date': '1998-07-20'  # Keep the same
            }
        }

        serializer = StudentProfileSerializer(instance=self.user, data=update_data)
        self.assertTrue(serializer.is_valid())

        updated_user = serializer.save()

        # Check user fields were updated
        self.assertEqual(updated_user.first_name, update_data['first_name'])
        self.assertEqual(updated_user.last_name, update_data['last_name'])

        # Check student fields were updated
        student = Student.objects.get(user=updated_user)
        self.assertEqual(student.education, update_data['student']['education'])
        self.assertEqual(student.phone_number, update_data['student']['phone_number'])

    def test_update_user_without_student(self):
        update_data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'student': {
                'education': 'MASTERS',
                'phone_number': '+1122334455',
                'birth_date': '1998-07-20'
            }
        }

        serializer = StudentProfileSerializer(instance=self.user_without_student, data=update_data)
        self.assertTrue(serializer.is_valid())

        with self.assertRaises(ValidationError):
            serializer.save()


class InstructorProfileSerializerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="instructorprofile",
            email="instructorprofile@example.com",
            password="password123",
            first_name="Instructor",
            last_name="Profile"
        )
        self.instructor_data = {
            "bio": "Experienced teacher",
            "education": "PHD"
        }
        self.instructor = Instructor.objects.create(user=self.user, **self.instructor_data)

        self.user_without_instructor = User.objects.create_user(
            username="notinstructor",
            email="notinstructor@example.com",
            password="password123"
        )

    def test_serialization(self):
        serializer = InstructorProfileSerializer(instance=self.user)
        data = serializer.data

        self.assertEqual(data['first_name'], self.user.first_name)
        self.assertEqual(data['last_name'], self.user.last_name)
        self.assertEqual(data['instructor']['bio'], self.instructor_data['bio'])
        self.assertEqual(data['instructor']['education'], self.instructor_data['education'])

    def test_update(self):
        update_data = {
            'first_name': 'Updated',
            'last_name': 'Instructor',
            'instructor': {
                'bio': 'Updated bio information',
                'education': 'PHD'
            }
        }

        serializer = InstructorProfileSerializer(instance=self.user, data=update_data, partial=True)
        self.assertTrue(serializer.is_valid())

        updated_user = serializer.save()

        # Check user fields were updated
        self.assertEqual(updated_user.first_name, update_data['first_name'])
        self.assertEqual(updated_user.last_name, update_data['last_name'])

        # Check instructor fields were updated
        instructor = Instructor.objects.get(user=updated_user)
        self.assertEqual(instructor.bio, update_data['instructor']['bio'])
        self.assertEqual(instructor.education, update_data['instructor']['education'])

    def test_update_user_without_instructor(self):
        update_data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'instructor': {
                'bio': 'Some bio',
                'education': 'PHD'
            }
        }

        serializer = InstructorProfileSerializer(instance=self.user_without_instructor, data=update_data)
        self.assertTrue(serializer.is_valid())

        with self.assertRaises(ValidationError):
            serializer.save()
