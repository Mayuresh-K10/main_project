# Generated by Django 4.2.15 on 2024-10-25 18:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0017_new_user_is_deleted'),
        ('job_portal', '0122_collegescreeninganswer_collegescreeningquestion_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='interview',
            name='student',
        ),
        migrations.AlterField(
            model_name='interview',
            name='job_seeker',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='login.jobseeker'),
        ),
        migrations.AlterField(
            model_name='interview',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='login.new_user'),
        ),
    ]
