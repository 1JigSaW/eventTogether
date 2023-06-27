# Generated by Django 4.2.1 on 2023-06-27 20:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('app', '0002_event_place'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserFavourite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('favourite_event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.event')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'favourite_event')},
            },
        ),
    ]