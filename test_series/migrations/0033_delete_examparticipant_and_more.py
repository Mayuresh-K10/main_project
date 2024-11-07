# Generated by Django 4.2.15 on 2024-10-23 08:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('test_series', '0032_alter_proctoringsession_status'),
    ]

    operations = [
        migrations.DeleteModel(
            name='ExamParticipant',
        ),
        migrations.RemoveField(
            model_name='proctoringevent',
            name='session',
        ),
        migrations.RemoveField(
            model_name='proctoringsession',
            name='exam',
        ),
        migrations.RemoveField(
            model_name='proctoringsession',
            name='user',
        ),
        migrations.RemoveField(
            model_name='question',
            name='exam',
        ),
        migrations.RemoveField(
            model_name='userresponse',
            name='question',
        ),
        migrations.RemoveField(
            model_name='userresponse',
            name='session',
        ),
        migrations.RemoveField(
            model_name='userresponse',
            name='user',
        ),
        migrations.RemoveField(
            model_name='userscore',
            name='exam',
        ),
        migrations.RemoveField(
            model_name='userscore',
            name='user',
        ),
        migrations.DeleteModel(
            name='Exam',
        ),
        migrations.DeleteModel(
            name='ProctoringEvent',
        ),
        migrations.DeleteModel(
            name='ProctoringSession',
        ),
        migrations.DeleteModel(
            name='Question',
        ),
        migrations.DeleteModel(
            name='UserResponse',
        ),
        migrations.DeleteModel(
            name='UserScore',
        ),
    ]
