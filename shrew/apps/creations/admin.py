from adminsortable2.admin import SortableAdminMixin
from simple_history.admin import SimpleHistoryAdmin
from django.contrib import admin
from django import forms
from django.db import models

from .models import Creation


@admin.register(Creation)
class CreationAdmin(SimpleHistoryAdmin):
    list_display = ('name', 'author', 'featured', 'is_animated')
    list_filter = ('featured', 'is_animated')
    search_fields = ('name', )
    date_hierarchy = 'created'
    formfield_overrides = {
        models.CharField: {
            'widget': forms.TextInput(attrs={'style': 'min-width: 50%'}),
        },
        models.TextField: {
            'widget': forms.Textarea(attrs={'style': 'min-width: 80%', 'rows': 20}),
        },
    }
