# Generated by Django 4.2.15 on 2024-10-26 18:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('job_portal', '0133_collegeenquiry_new_user_alter_collegeenquiry_status_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='collegeenquiry',
            name='university_in_charge',
        ),
    ]
