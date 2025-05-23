"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from courses import instructor_urls, student_urls
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

# API Documentation URLs
api_docs_urlpatterns = [
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "swagger/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"
    ),
    path("redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]

# API URLs
api_urlpatterns = [
    path("content/", include(instructor_urls)),
    path("student/", include(student_urls)),
    path("enrollment/", include("enrollment.urls")),
    path("dashboard/", include("dashboard.urls")),
]

# Main URL patterns
urlpatterns = [
    # Admin interface
    path("admin/", admin.site.urls),
    # Authentication
    path("auth/", include("accounts.urls")),
    # API Documentation
    path("api/docs/", include(api_docs_urlpatterns)),
    # API Endpoints
    path("api/v1/", include(api_urlpatterns)),
    # Redirect root to Swagger UI
    path(
        "", RedirectView.as_view(url="/api/docs/swagger/", permanent=False), name="home"
    ),
]

# Serve media and static files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS)
