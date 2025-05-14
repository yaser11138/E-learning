# E-Learning Platform

A modern, feature-rich e-learning platform built with Django and Django REST Framework. This platform enables instructors to create and manage courses while allowing students to learn at their own pace with progress tracking.

## Features

### For Instructors
- Create and manage courses with detailed information
- Organize course content into modules
- Support for multiple content types:
  - Text content
  - Video content
  - Image content
  - File attachments
- Set course pricing (free or paid)
- Track student progress and engagement

### For Students
- Browse available courses
- Access course content with progress tracking
- Track completion status for individual content items
- Video progress tracking (resume from last position)
- Course completion tracking
- Progress percentage calculation

## Technical Stack

- **Backend Framework**: Django & Django REST Framework
- **Database**: PostgreSQL (recommended)
- **Authentication**: Django's built-in authentication system
- **File Storage**: Django's FileSystemStorage (configurable)
- **API Documentation**: DRF Spectacular

## Prerequisites

- Python 3.8+
- pip (Python package manager)
- Virtual environment (recommended)
- PostgreSQL (recommended) or SQLite

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/e-learning.git
cd e-learning
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure your database settings in `settings.py`

5. Run migrations:
```bash
python manage.py migrate
```

6. Create a superuser:
```bash
python manage.py createsuperuser
```

7. Run the development server:
```bash
python manage.py runserver
```

## Project Structure

```
e-learning/
├── courses/                 # Main app for course management
│   ├── models.py           # Database models
│   ├── views.py            # API views
│   ├── serializers.py      # API serializers
│   └── tests/              # Test cases
├── core/                   # Core functionality
├── media/                  # User-uploaded files
├── static/                 # Static files
└── manage.py              # Django management script
```

## API Endpoints

### API Documentation
- `GET /api/docs/swagger/` - Swagger UI Documentation
- `GET /api/docs/redoc/` - ReDoc Documentation
- `GET /api/docs/schema/` - OpenAPI Schema

### Authentication
- `POST /auth/register/` - Register new user
- `POST /auth/login/` - User login
- `POST /auth/logout/` - User logout

### Course Management
- `GET /api/v1/content/courses/` - List all courses
- `POST /api/v1/content/courses/` - Create a new course
- `GET /api/v1/content/courses/{slug}/` - Get course details
- `PUT /api/v1/content/courses/{slug}/` - Update course
- `DELETE /api/v1/content/courses/{slug}/` - Delete course

### Module Management
- `GET /api/v1/content/courses/{slug}/modules/` - List course modules
- `POST /api/v1/content/courses/{slug}/modules/` - Create new module
- `GET /api/v1/content/modules/{slug}/` - Get module details
- `PUT /api/v1/content/modules/{slug}/` - Update module
- `DELETE /api/v1/content/modules/{slug}/` - Delete module

### Content Management
- `GET /api/v1/content/modules/{slug}/contents/` - List module contents
- `POST /api/v1/content/modules/{slug}/contents/` - Create new content
- `GET /api/v1/content/contents/{slug}/` - Get content details
- `PUT /api/v1/content/contents/{slug}/` - Update content
- `DELETE /api/v1/content/contents/{slug}/` - Delete content

### Student Endpoints
- `GET /api/v1/student/courses/` - List available courses
- `GET /api/v1/student/courses/{slug}/` - Get course details
- `GET /api/v1/student/contents/{slug}/` - Get content details

### Progress Tracking
- `GET /api/v1/student/courses/{slug}/progress/` - Get course progress
- `GET /api/v1/student/contents/{slug}/progress/` - Get content progress
- `POST /api/v1/student/contents/{slug}/progress/` - Update content progress

### Enrollment
- `POST /api/v1/enrollment/enroll/{slug}/` - Enroll in a course
- `GET /api/v1/enrollment/enrolled-courses/` - List enrolled courses

## Testing

Run the test suite:
```bash
python manage.py test
```

Run specific test cases:
```bash
python manage.py test courses.tests.test_progress
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.


## Support

For support, please open an issue in the GitHub repository or contact the maintainers. 