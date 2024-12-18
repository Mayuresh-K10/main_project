# Generated by Django 4.2.15 on 2024-10-25 08:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0016_remove_companyincharge_user_remove_consultant_user_and_more'),
        ('job_portal', '0112_candidate1status_not_eligible_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='message',
            old_name='job_seeker',
            new_name='sender1',
        ),
        migrations.RemoveField(
            model_name='message',
            name='user',
        ),
        migrations.AlterField(
            model_name='message',
            name='sender',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sender', to='login.new_user'),
        ),
    ]
