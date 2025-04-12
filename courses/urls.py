from django.urls import path
from rest_framework import routers
from .views import CourseViewSet, ModuleViewSet, ModuleCreateView, ModuleListView
router = routers.DefaultRouter()
router.register(r'course', CourseViewSet, basename='course')
router.register('modules', ModuleViewSet, basename="module")
urlpatterns = router.urls
urlpatterns += [
    path("course/<slug:slug>/create_module/", ModuleCreateView.as_view(), name="module_create"),
    path("course/<slug:slug>/moudels", ModuleListView.as_view(), name="module_list"),
]