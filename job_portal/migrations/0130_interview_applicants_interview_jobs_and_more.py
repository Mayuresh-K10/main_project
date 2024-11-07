# Generated by Django 4.2.15 on 2024-10-26 15:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0017_new_user_is_deleted'),
        ('job_portal', '0129_alter_studentenquiry_new_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='interview',
            name='applicants',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='job_portal.application1'),
        ),
        migrations.AddField(
            model_name='interview',
            name='jobs',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='job_portal.job1'),
        ),
        migrations.AddField(
            model_name='interview',
            name='university_in_charge',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='login.universityincharge'),
        ),
    ]
