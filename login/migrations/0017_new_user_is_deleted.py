# Generated by Django 4.2.15 on 2024-10-25 10:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0016_remove_companyincharge_user_remove_consultant_user_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='new_user',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
    ]
