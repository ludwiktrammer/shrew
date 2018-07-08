from adminsortable2.admin import SortableAdminMixin

from django.contrib import admin
from django import forms
from django.db import models

from .models import Page, PageCategory, Attachment


@admin.register(PageCategory)
class PageCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name', )
    prepopulated_fields = {'slug': ('name',)}


class AttachmentInline(admin.TabularInline):
    model = Attachment


@admin.register(Page)
class PageAdmin(SortableAdminMixin, admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('name', 'category', 'text')
        }),
        ('Advanced', {
            'classes': ('collapse',),
            'fields': ('slug', 'visible'),
        }),
    )
    list_display = ('name', 'category', 'visible')
    list_editable = ('visible', )
    list_filter = ('category', 'visible')
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
    inlines = [
        AttachmentInline,
    ]
