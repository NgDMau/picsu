# Generated by Django 4.2.8 on 2023-12-24 16:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('study', '0007_usertest_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='usertestscore',
            name='type',
            field=models.CharField(max_length=32, null=True),
        ),
    ]
