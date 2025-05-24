from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from courses.models import Course, CourseProgress
from courses.serializers import CourseProgressSerializer, CourseSerializer
from .serializers import StudentDashboardSerializer, TeacherDashboardSerializer

class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        
        if hasattr(user, "student"):
            # Get enrolled courses with progress using CourseProgress model
            course_progresses = CourseProgress.objects.filter(student=user)
            
            # Calculate statistics
            total_courses = course_progresses.count()
            completed_courses = course_progresses.filter(completed=True).count()
            in_progress_courses = total_courses - completed_courses
            
            # Calculate average progress manually
            total_progress = sum(cp.progress_percentage for cp in course_progresses)
            avg_progress = total_progress / total_courses if total_courses > 0 else 0
            
            # Get recently accessed courses (last 7 days)
            recent_courses = course_progresses.filter(
                last_accessed__gte=timezone.now() - timedelta(days=7)
            ).order_by('-last_accessed')[:5]
            
            # Prepare data for serialization
            data = {
                'role': 'student',
                'statistics': {
                    'totalCourses': total_courses,
                    'completedCourses': completed_courses,
                    'inProgressCourses': in_progress_courses,
                    'averageProgress': round(avg_progress, 2)
                },
                'recent_courses': CourseProgressSerializer(recent_courses, many=True, context={'request': request}).data,
                'enrolled_courses': CourseProgressSerializer(course_progresses, many=True, context={'request': request}).data
            }
            
            serializer = StudentDashboardSerializer(data)
            return Response(serializer.data)
        
        elif hasattr(user, "instructor"):
            # Get courses created by the teacher
            courses = user.courses.all()
            
            # Calculate statistics
            active_courses = courses.count()
            total_students = sum(course.enrollments.count() for course in courses)
            total_revenue = sum(
                course.price * course.enrollments.count() 
                for course in courses
            )
            
            # Get top performing courses (by enrollment)
            top_courses = sorted(
                courses,
                key=lambda x: x.enrollments.count(),
                reverse=True
            )[:5]
            
            # Prepare data for serialization
            data = {
                'role': 'teacher',
                'statistics': {
                    'activeCourses': active_courses,
                    'totalStudents': total_students,
                    'totalRevenue': round(total_revenue, 2),
                    'averageStudentsPerCourse': round(total_students / active_courses, 2) if active_courses > 0 else 0
                },
                'top_courses': CourseSerializer(top_courses, many=True, context={'request': request}).data,
                'courses': CourseSerializer(courses, many=True, context={'request': request}).data
            }
            
            serializer = TeacherDashboardSerializer(data)
            return Response(serializer.data)
        
        return Response({'error': 'Invalid user role'}, status=400)