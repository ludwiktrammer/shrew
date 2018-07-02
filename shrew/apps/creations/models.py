from django.db import models
from django.urls import reverse


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
