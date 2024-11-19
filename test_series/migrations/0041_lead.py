# Generated by Django 4.2.16 on 2024-11-19 07:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('test_series', '0040_remove_attachment1_message_remove_messages_candidate_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Lead',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254)),
                ('mobile', models.CharField(max_length=15)),
                ('page', models.CharField(choices=[('Your Page', 'Your Page'), ('CollegeCUE', 'CollegeCUE')], max_length=50)),
                ('time_duration', models.CharField(max_length=100)),
                ('approx_cost_to_invest', models.DecimalField(decimal_places=2, max_digits=10)),
                ('targeted_audience', models.CharField(choices=[('Student', 'Student'), ('Consultant', 'Consultant'), ('Other College', 'Other College'), ('Institute', 'Institute')], max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]