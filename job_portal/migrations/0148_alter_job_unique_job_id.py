# Generated by Django 4.2.15 on 2024-10-28 10:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('job_portal', '0147_alter_job_unique_job_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='job',
            name='unique_job_id',
            field=models.UUIDField(default=289285203888616454599870674851870987739, editable=False, unique=True),
        ),
    ]
