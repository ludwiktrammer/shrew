from adminsortable2.admin import SortableAdminMixin

from django.contrib import admin
from django import forms
from django.db import models

from .models import Sample


@admin.register(Sample)
class SampleAdmin(SortableAdminMixin, admin.ModelAdmin):
    fields = ['name', 'kind', 'code', 'svg', 'slug']
    list_display = ('name', 'kind')
    list_filter = ('kind', )
    search_fields = ('name', )
    prepopulated_fields = {'slug': ('name',)}
    formfield_overrides = {
        models.CharField: {
            'widget': forms.TextInput(attrs={'style': 'min-width: 50%'}),
        },
        models.TextField: {
            'widget': forms.Textarea(attrs={'style': 'min-width: 80%', 'rows': 20}),
        },
    }
