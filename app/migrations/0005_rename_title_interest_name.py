# Generated by Django 4.2.1 on 2023-06-29 21:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_language_remove_userprofile_language_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='interest',
            old_name='title',
            new_name='name',
        ),
    ]
