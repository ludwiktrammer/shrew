import os

from django.db import models
from django.utils.safestring import mark_safe
from django.urls import reverse


class PageCategory(models.Model):
    name = models.CharField(
        max_length=100,
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
        help_text="Used in page's URL",
    )
    text = models.TextField(
        help_text=mark_safe("You can use <a href='http://commonmark.org/help/'>MarkDown</a> here"),
        blank=True,
    )

    class Meta:
        ordering = ('name',)
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('pages:category-detail', kwargs={
            'slug': self.slug,
        })


class Page(models.Model):
    name = models.CharField(
        max_length=100,
    )
    slug = models.SlugField(
        max_length=100,
        help_text="Used in page's URL",
    )
    text = models.TextField(
        help_text=mark_safe("You can use <a href='http://commonmark.org/help/'>MarkDown</a> here"),
    )
    visible = models.BooleanField(
        default=True,
        help_text="Visible on list",
    )
    category = models.ForeignKey(
        PageCategory,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    order = models.PositiveIntegerField(
        default=0,
    )

    class Meta:
        ordering = ('order', 'id')
        unique_together = ('slug', 'category')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        kwargs = {'slug': self.slug}
        if self.category:
            kwargs['category_slug'] = self.category.slug
        return reverse('pages:page-detail', kwargs=kwargs)


class Attachment(models.Model):
    def upload_folder(self, filename):
        return os.path.join('pages', self.page.slug, filename)

    file = models.FileField(
        upload_to=upload_folder,
    )
    page = models.ForeignKey(
        Page,
        related_name='attachments',
        on_delete=models.CASCADE,
    )

    class Meta:
        ordering = ('file',)

    def __str__(self):
        return self.file.url

