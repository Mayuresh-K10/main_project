# Generated by Django 4.2.15 on 2024-10-26 09:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0017_new_user_is_deleted'),
        ('job_portal', '0127_studentenquiry_new_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studentenquiry',
            name='new_user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='login.new_user'),
        ),
    ]
