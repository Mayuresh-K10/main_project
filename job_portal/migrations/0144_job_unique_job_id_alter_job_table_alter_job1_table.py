# Generated by Django 4.2.15 on 2024-10-28 07:57

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('job_portal', '0143_membership_collegemembership_collegeadvertisement_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='unique_job_id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
        migrations.AlterModelTable(
            name='job',
            table='job',
        ),
        migrations.AlterModelTable(
            name='job1',
            table='job1',
        ),
    ]