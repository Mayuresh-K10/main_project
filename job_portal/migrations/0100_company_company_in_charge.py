# Generated by Django 4.2.15 on 2024-10-23 09:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0014_alter_companyincharge_token_alter_consultant_token_and_more'),
        ('job_portal', '0099_remove_job_card_number_remove_job_country_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='company_in_charge',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='login.companyincharge'),
        ),
    ]
