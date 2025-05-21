from celery import shared_task
from django.core.cache import cache
from django.core.mail import send_mail
from django.conf import settings
from .models import Course, CourseEnrollment


@shared_task
def update_course_statistics(course_id):
    """Update course statistics and cache them."""
    try:
        course = Course.objects.get(id=course_id)
        stats = {
            "total_enrollments": CourseEnrollment.objects.filter(course=course).count(),
            "active_students": CourseEnrollment.objects.filter(
                course=course, is_active=True
            ).count(),
            "completion_rate": course.calculate_completion_rate(),
        }

        # Cache the statistics for 1 hour
        cache_key = f"course_stats_{course_id}"
        cache.set(cache_key, stats, timeout=3600)

        return stats
    except Course.DoesNotExist:
        return None


@shared_task
def send_course_update_notification(course_id):
    """Send email notifications to enrolled students about course updates."""
    try:
        course = Course.objects.get(id=course_id)
        enrolled_students = CourseEnrollment.objects.filter(
            course=course, is_active=True
        ).select_related("student")

        for enrollment in enrolled_students:
            send_mail(
                subject=f"Course Update: {course.title}",
                message=f"Hello {enrollment.student.username},\n\n"
                f'The course "{course.title}" has been updated. '
                f"Please check the course page for new content.\n\n"
                f"Best regards,\nE-Learning Team",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[enrollment.student.email],
                fail_silently=True,
            )
    except Course.DoesNotExist:
        return None


@shared_task
def process_course_enrollment(enrollment_id):
    """Process course enrollment asynchronously."""
    try:
        enrollment = CourseEnrollment.objects.get(id=enrollment_id)

        # Perform enrollment processing
        enrollment.process_enrollment()

        # Send welcome email
        send_mail(
            subject=f"Welcome to {enrollment.course.title}",
            message=f"Hello {enrollment.student.username},\n\n"
            f'Welcome to the course "{enrollment.course.title}"! '
            f"We are excited to have you join us.\n\n"
            f"Best regards,\nE-Learning Team",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[enrollment.student.email],
            fail_silently=True,
        )

        return True
    except CourseEnrollment.DoesNotExist:
        return False
