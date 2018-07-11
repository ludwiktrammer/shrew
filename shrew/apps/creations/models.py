from django.db import models
from django.urls import reverse
from django.conf import settings

from autoslug import AutoSlugField
from simple_history.models import HistoricalRecords


class Creation(models.Model):
    name = models.CharField(
        max_length=100,
    )
    slug = AutoSlugField(
        populate_from='name',
        unique=True,
    )
    code = models.TextField()
    svg = models.TextField()
    is_animated = models.BooleanField()
    created = models.DateTimeField(
        auto_now_add=True,
    )
    last_modified = models.DateTimeField(
        auto_now=True,
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    featured = models.BooleanField(
        default=False,
    )
    history = HistoricalRecords()

    class Meta:
        ordering = ('-created', )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('creations:editor-creation', kwargs={
            'slug': self.slug,
        })


class Sample(models.Model):
    name = models.CharField(
        max_length=100,
    )
    slug = models.SlugField(
        max_length=100,
        help_text="Used in the URL",
    )
    code = models.TextField()
    svg = models.TextField()
    kind = models.CharField(
        max_length=15,
        choices=[
            ('drawing', "drawing"),
            ('animation', "animation"),
            ('unlisted', "unlisted"),
        ],
    )
    order = models.PositiveIntegerField(
        default=0,
    )

    class Meta:
        ordering = ('order', 'id')
        unique_together = ('slug', 'name')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('editor-sample', kwargs={
            'slug': self.slug,
        })
