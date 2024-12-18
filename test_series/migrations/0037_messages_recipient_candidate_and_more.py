# Generated by Django 4.2.16 on 2024-11-15 05:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0017_new_user_is_deleted'),
        ('test_series', '0036_messages1_attachment1'),
    ]

    operations = [
        migrations.AddField(
            model_name='messages',
            name='recipient_candidate',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='received_messages', to='login.jobseeker'),
        ),
        migrations.AddField(
            model_name='messages',
            name='recipient_company',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='received_messages', to='login.companyincharge'),
        ),
        migrations.AddField(
            model_name='messages',
            name='recipient_student',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='received_messages', to='login.new_user'),
        ),
    ]
