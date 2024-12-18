# Generated by Django 4.2.15 on 2024-10-27 07:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0017_new_user_is_deleted'),
        ('job_portal', '0135_rename_sender_job_seeker_message_receiptent_job_seeker_job_seeker_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='message',
            old_name='receiptent_job_seeker_job_seeker',
            new_name='receiptent_job_seeker',
        ),
        migrations.AddField(
            model_name='message',
            name='company_in_charge',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='login.companyincharge'),
        ),
    ]
