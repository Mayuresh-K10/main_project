# Generated by Django 4.2.15 on 2024-10-23 11:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0014_alter_companyincharge_token_alter_consultant_token_and_more'),
        ('job_portal', '0101_college_university_in_charge_student_job_seeker_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Education1',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('course_or_degree', models.CharField(default='Unknown', max_length=100)),
                ('school_or_university', models.CharField(default='Unknown', max_length=100)),
                ('grade_or_cgpa', models.CharField(default='N/A', max_length=50)),
                ('start_date', models.DateField(blank=True, null=True)),
                ('end_date', models.DateField(blank=True, null=True)),
                ('description', models.TextField(default='No description')),
                ('job_seeker', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='login.jobseeker')),
            ],
        ),
        migrations.AddField(
            model_name='achievements',
            name='job_seeker',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='login.jobseeker'),
        ),
        migrations.AddField(
            model_name='achievements',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='login.new_user'),
        ),
        migrations.AddField(
            model_name='application',
            name='company_in_charge',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='login.companyincharge'),
        ),
        migrations.AddField(
            model_name='application1',
            name='university_in_charge',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='login.universityincharge'),
        ),
        migrations.AddField(
            model_name='attachment',
            name='company_in_charge',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='login.companyincharge'),
        ),
        migrations.AddField(
            model_name='attachment',
            name='job_seeker',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='login.jobseeker'),
        ),
        migrations.AddField(
            model_name='attachment',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='login.new_user'),
        ),
        migrations.AddField(
            model_name='candidatestatus_not_eligible',
            name='job_seeker',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='login.jobseeker'),
        ),
        migrations.AddField(
            model_name='candidatestatus_not_eligible',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='login.new_user'),
        ),
        migrations.AddField(
            model_name='candidatestatus_rejected',
            name='job_seeker',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='login.jobseeker'),
        ),
        migrations.AddField(
            model_name='candidatestatus_rejected',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='login.new_user'),
        ),
        migrations.AddField(
            model_name='candidatestatus_selected',
            name='job_seeker',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='login.jobseeker'),
        ),
        migrations.AddField(
            model_name='candidatestatus_selected',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='login.new_user'),
        ),
        migrations.AddField(
            model_name='candidatestatus_under_review',
            name='job_seeker',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='login.jobseeker'),
        ),
        migrations.AddField(
            model_name='candidatestatus_under_review',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='login.new_user'),
        ),
        migrations.AddField(
            model_name='certification',
            name='job_seeker',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='login.jobseeker'),
        ),
        migrations.AddField(
            model_name='certification',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='login.new_user'),
        ),
        migrations.AddField(
            model_name='college_attachment',
            name='university_in_charge',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='login.universityincharge'),
        ),
        migrations.AddField(
            model_name='college_message',
            name='university_in_charge',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='login.universityincharge'),
        ),
        migrations.AddField(
            model_name='collegeenquiry',
            name='university_in_charge',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='login.universityincharge'),
        ),
        migrations.AddField(
            model_name='experience',
            name='job_seeker',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='login.jobseeker'),
        ),
        migrations.AddField(
            model_name='experience',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='login.new_user'),
        ),
        migrations.AddField(
            model_name='interview',
            name='job_seeker',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='login.jobseeker'),
        ),
        migrations.AddField(
            model_name='interview',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='login.new_user'),
        ),
        migrations.AddField(
            model_name='job',
            name='company_in_charge',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='login.companyincharge'),
        ),
        migrations.AddField(
            model_name='job1',
            name='university_in_charge',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='login.universityincharge'),
        ),
        migrations.AddField(
            model_name='message',
            name='company_in_charge',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='login.companyincharge'),
        ),
        migrations.AddField(
            model_name='message',
            name='job_seeker',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='login.jobseeker'),
        ),
        migrations.AddField(
            model_name='message',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='login.new_user'),
        ),
        migrations.AddField(
            model_name='objective',
            name='job_seeker',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='login.jobseeker'),
        ),
        migrations.AddField(
            model_name='objective',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='login.new_user'),
        ),
        migrations.AddField(
            model_name='project',
            name='job_seeker',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='login.jobseeker'),
        ),
        migrations.AddField(
            model_name='project',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='login.new_user'),
        ),
        migrations.AddField(
            model_name='publications',
            name='job_seeker',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='login.jobseeker'),
        ),
        migrations.AddField(
            model_name='publications',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='login.new_user'),
        ),
        migrations.AddField(
            model_name='reference',
            name='job_seeker',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='login.jobseeker'),
        ),
        migrations.AddField(
            model_name='reference',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='login.new_user'),
        ),
        migrations.AddField(
            model_name='resume',
            name='job_seeker',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='login.jobseeker'),
        ),
        migrations.AddField(
            model_name='resume',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='login.new_user'),
        ),
        migrations.AddField(
            model_name='screeninganswer',
            name='company_in_charge',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='login.companyincharge'),
        ),
        migrations.AddField(
            model_name='screeninganswer',
            name='job_seeker',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='login.jobseeker'),
        ),
        migrations.AddField(
            model_name='screeninganswer',
            name='university_in_charge',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='login.universityincharge'),
        ),
        migrations.AddField(
            model_name='screeninganswer',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='login.new_user'),
        ),
        migrations.AddField(
            model_name='screeningquestion',
            name='company_in_charge',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='login.companyincharge'),
        ),
        migrations.AddField(
            model_name='screeningquestion',
            name='university_in_charge',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='login.universityincharge'),
        ),
        migrations.AddField(
            model_name='studentenquiry',
            name='university_in_charge',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='login.universityincharge'),
        ),
        migrations.AddField(
            model_name='visitor',
            name='university_in_charge',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='login.universityincharge'),
        ),
        migrations.DeleteModel(
            name='Education',
        ),
        migrations.AddField(
            model_name='education1',
            name='resume',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='education_entries', to='job_portal.resume'),
        ),
        migrations.AddField(
            model_name='education1',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='login.new_user'),
        ),
    ]
