# Generated by Django 4.2.8 on 2023-12-24 15:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_rename_userknownword_userunknownword_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='dictionary',
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
    ]