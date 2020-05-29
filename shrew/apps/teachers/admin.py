from django.contrib import admin

from .models import Student


@admin.register(Student)
class CreationAdmin(admin.ModelAdmin):
    list_display = ('user', 'teacher')
    list_filter = (
        ('teacher', admin.RelatedOnlyFieldListFilter),
    )
