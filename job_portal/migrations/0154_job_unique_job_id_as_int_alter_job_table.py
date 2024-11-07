# Generated by Django 4.2.15 on 2024-10-28 11:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('job_portal', '0153_alter_job_unique_job_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='unique_job_id_as_int',
            field=models.BigIntegerField(editable=False, null=True, unique=True),
        ),
        migrations.AlterModelTable(
            name='job',
            table=None,
        ),
    ]
