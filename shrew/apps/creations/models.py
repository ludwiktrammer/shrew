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
        unique_with='author',
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
        related_name='creations',
        on_delete=models.CASCADE,
    )
    featured = models.BooleanField(
        default=False,
    )
    advanced = models.BooleanField(
        default=False,
    )
    base = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        related_name='children',
        blank=True,
        null=True,
    )
    history = HistoricalRecords()
    loving = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='loved',
    )

    class Meta:
        ordering = ('-pk', )
        unique_together = ('slug', 'author')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('creations:creation-detail', kwargs={
            'slug': self.slug,
            'user': self.author.username,
        })
