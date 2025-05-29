from django.urls import path
from rest_framework import routers
from .views import CourseViewSet, ModuleViewSet, ModuleCreateView, ModuleListView, ContentViewListCreate, ContentDetailView
router = routers.DefaultRouter()
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'modules', ModuleViewSet, basename="module")
router.register(r'contents', ContentDetailView, basename="content")
urlpatterns = router.urls
urlpatterns += [
    path("course/<slug:slug>/create_module/", ModuleCreateView.as_view(), name="module_create"),
    path("course/<slug:slug>/moudels", ModuleListView.as_view(), name="module_list"),
    path("module/<slug:module_slug>/content/", ContentViewListCreate.as_view(), name="module-contents")
]