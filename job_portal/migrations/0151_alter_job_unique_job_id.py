# Generated by Django 4.2.15 on 2024-10-28 11:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('job_portal', '0150_alter_job_unique_job_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='job',
            name='unique_job_id',
            field=models.UUIDField(default=135418209524497477602705290777117193521, editable=False, unique=True),
        ),
    ]
