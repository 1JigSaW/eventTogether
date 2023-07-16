# Generated by Django 4.2.1 on 2023-07-15 22:08

import cloudinary.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0010_remove_message_recipient'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='image',
            field=cloudinary.models.CloudinaryField(blank=True, max_length=255, null=True, verbose_name='events'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='image',
            field=cloudinary.models.CloudinaryField(blank=True, max_length=255, null=True, verbose_name='users'),
        ),
    ]
