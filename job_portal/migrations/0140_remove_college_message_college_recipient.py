# Generated by Django 4.2.15 on 2024-10-27 07:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('job_portal', '0139_college_message_college_recipient'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='college_message',
            name='college_recipient',
        ),
    ]
