# Generated by Django 4.2.15 on 2024-10-16 11:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('job_portal', '0087_delete_jobrole'),
    ]

    operations = [
        migrations.AlterField(
            model_name='application',
            name='student',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='job_portal.student'),
        ),
    ]
