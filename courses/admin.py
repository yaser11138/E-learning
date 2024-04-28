from django.contrib import admin
from courses.models import Course,Content,Subject,Module


class ModuleInline(admin.StackedInline):
    model = Module


# Register your models here.
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'subject', 'price']
    list_filter = ['created', 'subject', 'price']
    search_fields = ['title', 'summary']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ModuleInline]