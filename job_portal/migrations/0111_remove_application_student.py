# Generated by Django 4.2.15 on 2024-10-24 12:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('job_portal', '0110_remove_jobseekerstatus_rejected_job_seeker_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='application',
            name='student',
        ),
    ]
