# Generated by Django 4.2.8 on 2023-12-16 18:57

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('study', '0003_usertestresponse'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserTestScore',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_answers_chosen', models.IntegerField(default=0)),
                ('correct_answers_count', models.IntegerField(default=0)),
                ('incorrect_answers_count', models.IntegerField(default=0)),
                ('test_date', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
