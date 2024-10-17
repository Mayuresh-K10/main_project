# Generated by Django 4.2.14 on 2024-08-13 14:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('test_series', '0026_remove_question_time_limit_question_duration_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='section',
            field=models.CharField(choices=[('Physics', 'Physics'), ('Chemistry', 'Chemistry'), ('Mathematics', 'Mathematics')], max_length=50),
        ),
        migrations.AlterField(
            model_name='question',
            name='status',
            field=models.CharField(choices=[('Answered', 'Answered'), ('Mark for Review', 'Mark for Review'), ('Not Visited', 'Not Visited'), ('Not Answered', 'Not Answered')], max_length=50),
        ),
    ]