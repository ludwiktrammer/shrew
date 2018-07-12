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
    base = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    history = HistoricalRecords()

    class Meta:
        ordering = ('-pk', )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('creations:editor-creation', kwargs={
            'slug': self.slug,
        })
