# Generated by Django 4.2.15 on 2024-10-27 08:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0017_new_user_is_deleted'),
        ('job_portal', '0142_alter_college_message_receiptent_new_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='Membership',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
                ('mobile', models.CharField(max_length=15)),
                ('course_to_purchase', models.CharField(max_length=100)),
                ('quantity_of_leads', models.IntegerField()),
                ('location_for_leads', models.CharField(max_length=100)),
                ('intake_year', models.IntegerField()),
                ('company_in_charge', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='login.companyincharge')),
            ],
        ),
        migrations.CreateModel(
            name='CollegeMembership',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
                ('mobile', models.CharField(max_length=15)),
                ('course_to_purchase', models.CharField(max_length=100)),
                ('quantity_of_leads', models.IntegerField()),
                ('location_for_leads', models.CharField(max_length=100)),
                ('intake_year', models.IntegerField()),
                ('university_in_charge', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='login.universityincharge')),
            ],
        ),
        migrations.CreateModel(
            name='CollegeAdvertisement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
                ('contact', models.CharField(max_length=15)),
                ('advertisement_placement', models.CharField(max_length=100)),
                ('time_duration', models.CharField(max_length=50)),
                ('investment_cost', models.DecimalField(decimal_places=2, max_digits=10)),
                ('target_audience', models.CharField(max_length=100)),
                ('university_in_charge', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='login.universityincharge')),
            ],
        ),
        migrations.CreateModel(
            name='Advertisement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
                ('contact', models.CharField(max_length=15)),
                ('advertisement_placement', models.CharField(max_length=100)),
                ('time_duration', models.CharField(max_length=50)),
                ('investment_cost', models.DecimalField(decimal_places=2, max_digits=10)),
                ('target_audience', models.CharField(max_length=100)),
                ('company_in_charge', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='login.companyincharge')),
            ],
        ),
    ]