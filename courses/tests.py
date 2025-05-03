from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
import io
from PIL import Image
import tempfile
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Course, Module, Content, Subject, TextContent
from accounts.models import Instructor, Student
import json

User = get_user_model()


class CourseViewSetTest(APITestCase):
    def setUp(self):
        # Create users
        self.user1 = User.objects.create_user(
            username='instructor',
            email='instructor@example.com',
            password='testpassword123',
        )
        self.user2 = User.objects.create_user(
            username='other_instructor',
            email='other@example.com',
            password='testpassword123',
        )
        self.user3 = User.objects.create_user(
            username='student',
            email='student@example.com',
            password='testpassword123'
        )
        self.subject = Subject.objects.create(title="test",slug="test")
        self.instructor = Instructor.objects.create(user=self.user1, education="BACHELORS")
        self.other_instructor = Instructor.objects.create(user=self.user2, education="BACHELORS")
        self.student = Student.objects.create(user=self.user3, education="BACHELORS", phone_number="09991113333",
                                              birth_date="2002-10-2")


        # Create test course
        self.course = Course.objects.create(
            title='Test Course',
            price=12333,
            subject=self.subject,
            required_time=122,
            owner=self.instructor.user
        )

        # Set up client
        self.client = APIClient()

    def _generate_test_image(self):
        """Generate a test image for testing file uploads"""
        file = io.BytesIO()
        image = Image.new('RGB', (100, 100), color='red')
        image.save(file, 'png')
        file.name = 'test.png'
        file.seek(0)
        return file

    def test_list_courses(self):
        """Test listing all courses"""
        url = reverse('course-list')
        self.client.force_authenticate(user=self.instructor.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_course(self):
        """Test creating a new course"""
        url = reverse('course-list')
        self.client.force_authenticate(user=self.instructor.user)

        # Create a test image file
        image = self._generate_test_image()

        data = {
            'title': 'New Course',
            'subject': self.subject.pk,
            "required_time": 12,
            "price": 133,
            "summary": "This is for test",
            'thumbnail': SimpleUploadedFile("thumbnail.png", image.getvalue(), content_type="image/png")
        }

        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Course.objects.count(), 2)
        self.assertEqual(response.data['title'], 'New Course')

    def test_retrieve_course(self):
        """Test retrieving a specific course"""
        url = reverse('course-detail', kwargs={'slug': self.course.slug})
        self.client.force_authenticate(user=self.instructor.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Course')

    def test_update_course(self):
        """Test updating an existing course"""
        url = reverse('course-detail', kwargs={'slug': self.course.slug})
        self.client.force_authenticate(user=self.instructor.user)

        data = {
            'summary': 'Updated Course',
        }

        response = self.client.patch(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.course.refresh_from_db()
        self.assertEqual(self.course.summary, 'Updated Course')

    def test_update_course_not_owner(self):
        """Test that non-owner cannot update course"""
        url = reverse('course-detail', kwargs={'slug': self.course.slug})
        self.client.force_authenticate(user=self.other_instructor.user)

        data = {
            'title': 'Unauthorized Update',
        }

        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.course.refresh_from_db()
        self.assertEqual(self.course.title, 'Test Course')  # Title should remain unchanged

    def test_delete_course(self):
        """Test deleting a course"""
        url = reverse('course-detail', kwargs={'slug': self.course.slug})
        self.client.force_authenticate(user=self.instructor.user)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Course.objects.count(), 0)

    def test_student_cannot_create_course(self):
        """Test that students cannot create courses"""
        url = reverse('course-list')
        self.client.force_authenticate(user=self.student.user)

        image = self._generate_test_image()

        data = {
            'title': 'Student Course',
            'price': 123,
            'required_time':12,
            'subject': self.subject,
            'thumbnail': SimpleUploadedFile("thumbnail.png", image.getvalue(), content_type="image/png")

        }

        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Course.objects.count(), 1)  # Count should remain unchanged


class ModuleViewsTest(APITestCase):
    def setUp(self):
        # Create users
        self.user1 = User.objects.create_user(
            username='instructor',
            email='instructor@example.com',
            password='testpassword123',
        )
        self.user2 = User.objects.create_user(
            username='other_instructor',
            email='other@example.com',
            password='testpassword123',
        )
        self.user3 = User.objects.create_user(
            username='student',
            email='student@example.com',
            password='testpassword123'
        )
        self.subject = Subject.objects.create(title="test", slug="test")
        self.instructor = Instructor.objects.create(user=self.user1, education="BACHELORS")
        self.other_instructor = Instructor.objects.create(user=self.user2, education="BACHELORS")
        self.student = Student.objects.create(user=self.user3, education="BACHELORS", phone_number="09991113333",
                                              birth_date="2002-10-2")

        # Create test course
        self.course = Course.objects.create(
            title='Test Course',
            price=12333,
            subject=self.subject,
            required_time=122,
            owner=self.instructor.user
        )

        # Create test module
        self.module = Module.objects.create(
            title='Test Module',
            description='Test description',
            course=self.course
        )

        # Set up client
        self.client = APIClient()

    def test_list_modules(self):
        """Test listing all modules for a course"""
        url = reverse('module_list', kwargs={'slug': self.course.slug})
        self.client.force_authenticate(user=self.instructor.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Test Module')

    def test_create_module(self):
        """Test creating a new module"""
        url = reverse('module_create', kwargs={'slug': self.course.slug})
        self.client.force_authenticate(user=self.instructor.user)

        data = {
            'title': 'New Module',
            'description': 'New module description'
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Module.objects.count(), 2)
        self.assertEqual(response.data['title'], 'New Module')

    def test_retrieve_module(self):
        """Test retrieving a specific module"""
        url = reverse('module-detail', kwargs={'slug': self.module.slug})
        self.client.force_authenticate(user=self.instructor.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Module')

    def test_update_module(self):
        """Test updating an existing module"""
        url = reverse('module-detail', kwargs={'slug': self.module.slug})
        self.client.force_authenticate(user=self.instructor.user)

        data = {
            'title': 'Updated Module',
            'description': 'Updated description'
        }

        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.module.refresh_from_db()
        self.assertEqual(self.module.title, 'Updated Module')

    def test_update_module_not_owner(self):
        """Test that non-owner cannot update module"""
        url = reverse('module-detail', kwargs={'slug': self.module.slug})
        self.client.force_authenticate(user=self.other_instructor.user)

        data = {
            'title': 'Unauthorized Update',
            'description': 'Should not work'
        }

        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.module.refresh_from_db()
        self.assertEqual(self.module.title, 'Test Module')  # Title should remain unchanged

    def test_delete_module(self):
        """Test deleting a module"""
        url = reverse('module-detail', kwargs={'slug': self.module.slug})
        self.client.force_authenticate(user=self.instructor.user)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Module.objects.count(), 0)


class ContentViewsTest(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='instructor',
            email='instructor@example.com',
            password='testpassword123',
        )
        self.user2 = User.objects.create_user(
            username='other_instructor',
            email='other@example.com',
            password='testpassword123',
        )
        self.user3 = User.objects.create_user(
            username='student',
            email='student@example.com',
            password='testpassword123'
        )
        self.subject = Subject.objects.create(title="test", slug="test")
        self.instructor = Instructor.objects.create(user=self.user1, education="BACHELORS")
        self.other_instructor = Instructor.objects.create(user=self.user2, education="BACHELORS")
        self.student = Student.objects.create(user=self.user3, education="BACHELORS", phone_number="09991113333",
                                              birth_date="2002-10-2")

        # Create test course
        self.course = Course.objects.create(
            title='Test Course',
            price=12333,
            subject=self.subject,
            required_time=122,
            owner=self.instructor.user
        )

        # Create test module
        self.module = Module.objects.create(
            title='Test Module',
            description='Test description',
            course=self.course
        )

        # Create test content
        self.content = TextContent.objects.create(
            title='Test Content',
            module=self.module,
            text='Test text content'
        )

        # Set up client
        self.client = APIClient()

    def _create_temp_file(self, content=b'test content'):
        temp_file = tempfile.NamedTemporaryFile(suffix='.pdf')
        temp_file.write(content)
        temp_file.seek(0)
        return temp_file

    def test_list_contents(self):
        """Test listing all contents for a module"""
        url = reverse('module-contents', kwargs={'module_slug': self.module.slug})
        self.client.force_authenticate(user=self.instructor.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Test Content')

    def test_create_text_content(self):
        """Test creating a new text content"""
        url = reverse('module-contents', kwargs={'module_slug': self.module.slug})
        self.client.force_authenticate(user=self.instructor.user)

        data = {
            'title': 'New Text Content',
            'resourcetype': 'TextContent',
            'text': 'This is a test text content',
            'is_free': True
        }

        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Content.objects.count(), 2)
        self.assertEqual(response.data['title'], 'New Text Content')
        self.assertEqual(response.data['resourcetype'], 'TextContent')

    def test_create_file_content(self):
        """Test creating a new file content"""
        url = reverse('module-contents', kwargs={'module_slug': self.module.slug})
        self.client.force_authenticate(user=self.instructor.user)

        temp_file = self._create_temp_file()

        data = {
            'title': 'File Content',
            'resourcetype': 'FileContent',
            'file': SimpleUploadedFile(temp_file.name, temp_file.read(), content_type='application/pdf')
        }

        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Content.objects.count(), 2)
        self.assertEqual(response.data['resourcetype'], 'FileContent')

    def test_retrieve_content(self):
        """Test retrieving a specific content"""
        url = reverse('content-detail', kwargs={'slug': self.content.slug})
        self.client.force_authenticate(user=self.instructor.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Content')

    def test_update_content(self):
        """Test updating an existing content"""
        url = reverse('content-detail', kwargs={'slug': self.content.slug})
        self.client.force_authenticate(user=self.instructor.user)

        data = {
            'title': 'Updated Content',
            'text': 'Updated text content'
        }

        response = self.client.patch(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.content.refresh_from_db()
        self.assertEqual(self.content.title, 'Updated Content')
        self.assertEqual(self.content.text, 'Updated text content')



    def test_delete_content(self):
        """Test deleting a content"""
        url = reverse('content-detail', kwargs={'slug': self.content.slug})
        self.client.force_authenticate(user=self.instructor.user)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Content.objects.count(), 0)

    def test_student_cannot_create_content(self):
        """Test that students cannot create content"""
        url = reverse('module-contents', kwargs={'module_slug': self.module.slug})
        self.client.force_authenticate(user=self.student.user)

        data = {
            'title': 'Student Content',
            'resourcetype': 'text',
            'text': 'This should not work'
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Content.objects.count(), 1)  # Count should remain unchanged


