# Generated by Django 4.2.15 on 2024-10-24 09:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('job_portal', '0107_remove_candidatestatus_not_eligible_job_seeker_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='student',
            name='job_seeker',
        ),
    ]