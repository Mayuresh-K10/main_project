# Generated by Django 4.2.15 on 2024-10-26 18:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('job_portal', '0131_remove_interview_applicants_remove_interview_jobs_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='collegeenquiry',
            name='status',
            field=models.CharField(choices=[('replied', 'Replied'), ('not-replied', 'Not-Replied')], default='pending', max_length=20),
        ),
        migrations.AlterField(
            model_name='studentenquiry',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('reviewed', 'Reviewed'), ('resolved', 'Resolved')], default='not-replied', max_length=20),
        ),
    ]