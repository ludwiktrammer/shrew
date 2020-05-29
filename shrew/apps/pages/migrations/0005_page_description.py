# Generated by Django 2.1.13 on 2020-05-29 16:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0004_auto_20180708_1134'),
    ]

    operations = [
        migrations.AddField(
            model_name='page',
            name='description',
            field=models.CharField(blank=True, help_text="short description of the page's contents", max_length=255),
        ),
    ]
