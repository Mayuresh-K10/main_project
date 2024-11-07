import uuid
from django.db import DatabaseError, IntegrityError, OperationalError, transaction
from django.shortcuts import get_object_or_404 # type: ignore
from django.http import JsonResponse # type: ignore
from django.middleware.csrf import get_token # type: ignore
from django.views.decorators.csrf import csrf_exempt # type: ignore
from django.utils import timezone # type: ignore
from django.db.models import Q # type: ignore
from rest_framework.response import Response
from login.models import CompanyInCharge, JobSeeker, UniversityInCharge, new_user
from .models import Advertisement, Application, Application1, Attachment, College_Attachment, CollegeAdvertisement, CollegeMembership, CollegeScreeningAnswer, CollegeScreeningQuestion, CompanyScreeningAnswer, CompanyScreeningQuestion, Membership, Message,Candidate1Status_not_eligible, Candidate1Status_rejected, Candidate1Status_selected, Candidate1Status_under_review, CandidateStatus_not_eligible, College_Message, JobSeeker_Resume, CandidateStatus_rejected, CandidateStatus_selected, CandidateStatus_under_review, College, CollegeEnquiry, Interview, Job, Company, Job1, Resume, Student, StudentEnquiry, Visitor
from .forms import AchievementForm, AdvertisementForm, AdvertisementForm1, Application1Form, ApplicationForm,CertificationForm, CollegeForm, CompanyForm, EducationForm, ExperienceForm, Job1Form, JobForm, JobseekerAchievementForm, JobseekerCertificationForm, JobseekerEducationForm, JobseekerExperienceForm, JobseekerObjectiveForm, JobseekerProjectForm, JobseekerPublicationForm, JobseekerReferenceForm, JobseekerResumeForm, MembershipForm, MembershipForm1,  ObjectiveForm, ProjectForm, PublicationForm, ReferenceForm, ResumeForm, StudentForm, VisitorRegistrationForm
import json, operator, os
from datetime import timedelta
from django.utils.decorators import method_decorator # type: ignore
from django.views import View # type: ignore
from functools import reduce
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
from itertools import chain
from django.db.models import Count
from django.db.models.functions import TruncMonth

def home(request):
    try:
        return JsonResponse({"message": "Welcome to CollegeCue!"}, status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

def get_csrf_token(request):
    try:
        csrf_token = get_token(request)
        return JsonResponse({'csrf_token': csrf_token}, status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def job_list(request):
    try:
        if request.method == 'GET':
            filter_params = {
                'search_query': request.GET.get('search', ''),
                'job_title': request.GET.get('job_title', ''),
                'sort_order': request.GET.get('sort', ''),
                'job_type': request.GET.get('job_type', ''),
                'company_name': request.GET.get('company', ''),
                'experience_level': request.GET.get('experience', ''),
                'explore_new_jobs': request.GET.get('explore_new_jobs', ''),
                'category': request.GET.get('category', ''),
                'skills': request.GET.get('skills', ''),
                'workplaceTypes': request.GET.get('workplaceTypes', '')
            }

            jobs = Job.objects.all()
            filters = []

            if filter_params['search_query']:
                filters.append(Q(job_title__icontains=filter_params['search_query']))
            if filter_params['company_name']:
                filters.append(Q(company__icontains=filter_params['company_name']))
            if filter_params['job_title']:
                filters.append(Q(job_title__icontains=filter_params['job_title']))
            if filter_params['job_type']:
                filters.append(Q(job_type__icontains=filter_params['job_type']))
            if filter_params['experience_level']:
                filters.append(Q(experience__icontains=filter_params['experience_level']))
            if filter_params['category']:
                filters.append(Q(category__icontains=filter_params['category']))
            if filter_params['workplaceTypes']:
                filters.append(Q(workplaceTypes__icontains=filter_params['workplaceTypes']))

            if filter_params['skills']:
                skills_list = filter_params['skills'].split(',')
                for skill in skills_list:
                    filters.append(Q(skills__icontains=skill))

            if filters:
                jobs = jobs.filter(reduce(operator.and_, filters))

            if filter_params['explore_new_jobs']:
                days = 7 if filter_params['explore_new_jobs'] == 'week' else 30
                start_date = timezone.now() - timedelta(days=days)
                jobs = jobs.filter(published_at__gte=start_date)

            if filter_params['sort_order']:
                jobs = jobs.order_by(filter_params['sort_order'])

            jobs_list = [
                {
                'id': job.id,
                'job_title': job.job_title,
                'company':job.company.name,
                'location': job.location,
                'requirements': job.requirements,
                'job_type': job.job_type,
                'experience': job.experience,
                'category': job.category,
                'published_at': job.published_at,
                'skills': job.skills,
                'workplaceTypes': job.workplaceTypes,
                'questions': job.questions,
                "unique_job_id_as_int":job.unique_job_id_as_int
            } for job in jobs]

            return JsonResponse(jobs_list, safe=False, status=200)

        # elif request.method == 'POST':
        #     return handle_post_request(request, company_in_charge_id) # type: ignore

        return JsonResponse({'error': 'Method not allowed'}, status=405)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def create_company_jobs(request, company_in_charge_id):
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return JsonResponse({'error': 'Token is missing or in an invalid format'}, status=400)

    token = auth_header.split(' ')[1]
    
    try:
        company_in_charge = CompanyInCharge.objects.get(token=token, id=company_in_charge_id)
    except CompanyInCharge.DoesNotExist:
        return JsonResponse({'error': 'Invalid token or company in charge not found'}, status=401)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    company_name = data.get('company')
    if not company_name:
        return JsonResponse({'error': 'Company name is required'}, status=400)
    
    try:
        company = Company.objects.get(name=company_name, company_in_charge=company_in_charge)
    except Company.DoesNotExist:
        return JsonResponse({'error': f'Company with name "{company_name}" does not exist'}, status=404)

    if Job.objects.filter(company=company).count() >= 100:
        return JsonResponse({'message': 'Limit exceeded for job postings by this company'}, status=200)

    job_skills = data.get('skills', '')
    if job_skills:
        unique_job_list = list(set(job_skills.split(', ')))
        data['skills'] = ', '.join(unique_job_list)

    data['company'] = company.id
    data['company_in_charge'] = company_in_charge.id

    form = JobForm(data)
    if form.is_valid():
        try:
            job = form.save(commit=False)
            job.company = company
            job.company_in_charge = company_in_charge
            job.save()  # unique_job_id_as_int will be set in `save()` method
            return JsonResponse({'message': 'Job created successfully'}, status=201)
        except Exception as e:
            return JsonResponse({'error': f'Error saving job: {str(e)}'}, status=500)
    else:
        return JsonResponse({'errors': form.errors}, status=400)

@csrf_exempt
def job_detail(request, job_id):
    try:
        job = get_object_or_404(Job, id=job_id)
        if request.method == 'GET':
            return JsonResponse({
                'id': job.id,
                'title': job.job_title,
                'company':job.company.name,
                'location': job.location,
                'description': job.description,
                'requirements': job.requirements,
                'job_type': job.job_type,
                'experience': job.experience,
                'category': job.category,
                'published_at': job.published_at
            })

        elif request.method == 'PUT':
            data = json.loads(request.body)
            company_name = data.get('company')

            if company_name:
                try:
                    company = Company.objects.get(name=company_name)
                    data['company'] = company.id
                except Company.DoesNotExist:
                    return JsonResponse({'error': f'Company "{company_name}" does not exist.'}, status=404)

            form = JobForm(data, instance=job)
            if form.is_valid():
                form.save()
                return JsonResponse({'message': 'Job updated successfully'}, status=200)
            return JsonResponse({'errors': form.errors}, status=400)

        elif request.method == 'DELETE':
            job.delete()
            return JsonResponse({'message': 'Job deleted successfully'}, status=200)
        else:
            return JsonResponse({'error': 'Method not allowed'}, status=405)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def apply_job(request, job_id, company_in_charge_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return JsonResponse({'error': 'Token is missing or invalid format'}, status=400)

    token = auth_header.split(' ')[1]

    try:
        company_in_charge = CompanyInCharge.objects.get(id=company_in_charge_id, token=token)
        
        json_data = json.loads(request.POST.get('data', '{}'))
        job = get_object_or_404(Job, id=job_id, company_in_charge=company_in_charge)

        email = json_data.get('email')
        if not email:
            return JsonResponse({'error': 'Email is required'}, status=400)

        if Application.objects.filter(email=email, job=job).exists():
            return JsonResponse({'error': 'An application with this email already exists for this job.'}, status=400)

        new_user_exists = new_user.objects.filter(email=email).exists()
        job_seeker_exists = JobSeeker.objects.filter(email=email).exists()

        if not new_user_exists and not job_seeker_exists:
            return JsonResponse({'error': 'No account found for this email in NewUser or JobSeeker'}, status=404)

        form = ApplicationForm(json_data, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.company_in_charge = company_in_charge

            job_skills = set(job.skills.split(', '))
            candidate_skills = set(json_data.get('skills', '').split(', '))
            application.skills = ', '.join(candidate_skills)

            if not job_skills.intersection(candidate_skills):
                return JsonResponse({'message': 'Candidate is not eligible to apply'}, status=404)

            application.save()
            return JsonResponse({'message': 'Application submitted successfully', 'application_id': application.id}, status=201)

        return JsonResponse({'errors': form.errors}, status=400)

    except CompanyInCharge.DoesNotExist:
        return JsonResponse({'error': 'Invalid token or company_in_charge ID'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def job_applications(request, job_id):
    try:
        job = get_object_or_404(Job, id=job_id)
        applications = Application.objects.filter(job=job)
        applications_list = [{
            'id': app.id,
            'first_name': app.first_name,
            'last_name': app.last_name,
            'email': app.email,
            'phone_number': app.phone_number,
            'resume_url': app.resume.url if app.resume else '',
            'cover_letter': app.cover_letter,
            'status': app.status,
            'applied_at': app.applied_at,
        } for app in applications]
        return JsonResponse(applications_list, safe=False, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def job_status(request, job_id):
    try:
        pending_applications = Application.objects.filter(job_id=job_id, status='pending')
        pending_count = pending_applications.count()

        return JsonResponse({
            'job_id': job_id,
            'pending_count': pending_count
        }, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
def fetch_all_companies(request):
    companies = Company.objects.filter(is_deleted=False).values(
        'id','company_in_charge','name', 'email', 'phone', 'address', 'city', 'state', 
        'country', 'zipcode', 'website', 'about_company', 
        'sector_type', 'category', 'established_date', 
        'employee_size', 'Attachment'
    )
    
    return JsonResponse(list(companies), safe=False)

@method_decorator(csrf_exempt, name='dispatch') 
class CompanyListCreateView(View):    
    def post(self, request, company_in_charge_id):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({'status': 'error', 'message': 'Token is missing or invalid format'}, status=400)

        token = auth_header.split(' ')[1]

        try:
            company_in_charge = CompanyInCharge.objects.get(id=company_in_charge_id, token=token)

            company_email = request.POST.get('email')
            if not company_email:
                return JsonResponse({'status': 'error', 'message': 'Email is required'}, status=400)
            
            if company_email != company_in_charge.official_email:
                return JsonResponse({'status': 'error', 'message': 'Email does not match the email of the company in charge'}, status=400)

            company = Company.objects.filter(email=company_email, company_in_charge=company_in_charge).first()
            company_form = CompanyForm(request.POST, request.FILES, instance=company) if company else CompanyForm(request.POST, request.FILES)

            if company_form.is_valid():
                company = company_form.save(commit=False)
                company.company_in_charge = company_in_charge
                company.save()

                delete_attachment = request.POST.get('is_deleted', 'false').lower() == 'true'
                if delete_attachment and company.Attachment:
                    if os.path.exists(company.Attachment.path):
                        os.remove(company.Attachment.path)
                    company.Attachment = None
                    company.save()
                    return JsonResponse({'status': 'success', 'message': 'Attachment deleted successfully', 'company_id': company.id}, status=200)

                return JsonResponse({'status': 'success', 'message': 'Company created/updated successfully', 'company_id': company.id}, status=201)
            else:
                return JsonResponse(company_form.errors, status=400)

        except CompanyInCharge.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Invalid token or company in charge ID'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class CompanyDetailView(View):
    def get(self, request, pk):
        try:
            company = Company.objects.get(pk=pk)
            return JsonResponse({
                "id": company.id,
                "name": company.name,
                "email": company.email,
                "phone": company.phone,
                "address": company.address,
                "city": company.city,
                "state": company.state,
                "country": company.country,
                "zipcode": company.zipcode,
                "website": company.website,
                "website_urls": company.website_urls,
                "about_company": company.about_company,
                "sector_type": company.sector_type,
                "category": company.category,
                "established_date": company.established_date,
                "employee_size": company.employee_size,
            })
        except Company.DoesNotExist:
            return JsonResponse({'error': 'Company not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    def post(self, request, pk):
        try:
            company = Company.objects.get(pk=pk)

            form = CompanyForm(request.POST, request.FILES, instance=company)

            if form.is_valid():
                form.save()
                return JsonResponse({'message': 'Company updated successfully'}, status=200)
            else:
                return JsonResponse(form.errors, status=400)

        except Company.DoesNotExist:
            return JsonResponse({'error': 'Company not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    def delete(self, request, pk):
        try:
            company = Company.objects.get(pk=pk)
            company.delete()
            return JsonResponse({'message': 'Company deleted successfully'}, status=200)
        except Company.DoesNotExist:
            return JsonResponse({'error': 'Company not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

def find_status(request):
    try:
        co_name = request.GET['name']

        try:
            company = Company.objects.get(name=co_name)
        except Company.DoesNotExist:
            return JsonResponse({'error': f'Company "{co_name}" does not exist.'}, status=404)

        job_ids = Job.objects.filter(company=company)

        applications = Application.objects.filter(job__in=job_ids)

        statuses = {}
        for application in applications:
            if application.status not in statuses:
                statuses[application.status] = 1
            else:
                statuses[application.status] += 1

        return JsonResponse({'message': statuses}, status=200)

    except Exception as e:
         return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def candidate_profile(request):
    try:
        json_data = json.loads(request.POST.get('data'))
        skills_can = json_data['skills']
        can_skills_set = set(skills_can.split(', '))
        skills_of_can = ', '.join(can_skills_set)
        print(skills_of_can)
        can_location = json_data['location']
        experience_year = json_data['experience_years']
        print(experience_year)
        matching_jobs = []
        all_jobs = Job.objects.all()
        for job in all_jobs:
            job_skills_set = set(job.skills.split(', '))
            ex_year_arr = job.experience_yr.split('-')
            print(ex_year_arr)
            if can_skills_set.intersection(job_skills_set) and experience_year >= int(ex_year_arr[0]) and experience_year <= int(ex_year_arr[1]) and job.location == can_location:
                matching_jobs.append({
                    "id": job.id,
                    "title": job.job_title,
                    "company":job.company.name,
                    "experience_year": job.experience_yr,
                    "location": job.location,
                })

        return JsonResponse({'matching_jobs': matching_jobs})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def company_status(request, status_choice, company_in_charge_id):

    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return JsonResponse({'error': 'Token is missing or invalid format'}, status=400)

    token = auth_header.split(' ')[1]

    try:
        company_in_charge = CompanyInCharge.objects.get(id=company_in_charge_id, token=token)

        co_name = request.GET.get('name')
        if not co_name:
            return JsonResponse({'error': 'Company name is required.'}, status=400)

        try:
            company = Company.objects.get(name=co_name, company_in_charge=company_in_charge)
        except Company.DoesNotExist:
            return JsonResponse({'error': f'Company "{co_name}" does not exist.'}, status=404)

        job_ids = Job.objects.filter(company=company)

        apply_ids = Application.objects.filter(job__in=job_ids)

        names = []
        if status_choice == 'selected':
            candidate_status_modelname = CandidateStatus_selected
        elif status_choice == 'rejected':
            candidate_status_modelname = CandidateStatus_rejected
        elif status_choice == 'not_eligible':
            candidate_status_modelname = CandidateStatus_not_eligible
        elif status_choice == 'under_review':
            candidate_status_modelname = CandidateStatus_under_review
        else:
            return JsonResponse({'error': 'Invalid status choice.'}, status=400)

        for application in apply_ids:
            if application.status == status_choice:
                names.append(application.first_name)
                candidate_status_modelname.objects.create(
                    first_name=application.first_name,
                    status=status_choice,
                    company_name=co_name,
                    job_id=application.job_id,
                )

        return JsonResponse({'message': names}, status=200)
    
    except CompanyInCharge.DoesNotExist:
        return JsonResponse({'error': 'Invalid token or company in charge not found.'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def create_user_resume(request, user_id):
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return JsonResponse({'status': 'error', 'message': 'Token is missing or invalid format'}, status=400)
    
    token = auth_header.split(' ')[1]

    try:
        user = new_user.objects.get(id=user_id, token=token)
    except new_user.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Invalid token or user not found'}, status=401)

    if request.method == 'POST':
        try:
            with transaction.atomic():
                user_instance = get_object_or_404(new_user, id=user_id)
                user_email = request.POST.get('email')

                if not user_email:
                    return JsonResponse({'status': 'error', 'message': 'Email is required'}, status=400)
                if user_email != user.email:
                    return JsonResponse({'status': 'error', 'message': 'Email mismatch'}, status=400)

                resume = Resume.objects.filter(email=user_email, user=user_instance).first()
                resume_form = ResumeForm(request.POST, request.FILES, instance=resume)

                if resume_form.is_valid():
                    resume = resume_form.save(commit=False)
                    resume.user = user_instance

                    delete_attachment = resume_form.cleaned_data.get('delete', False)
                    new_attachment = resume_form.cleaned_data.get('Attachment')

                    if new_attachment and resume and resume.Attachment and os.path.exists(resume.Attachment.path):
                        os.remove(resume.Attachment.path)
                    resume.save()

                    if delete_attachment and resume.Attachment and os.path.exists(resume.Attachment.path):
                        os.remove(resume.Attachment.path)
                        resume.Attachment = None
                        resume.save()
                        return JsonResponse({'status': 'success', 'message': 'Attachment deleted successfully', 'resume_id': resume.id})

                else:
                    return JsonResponse({'status': 'error', 'errors': resume_form.errors}, status=400)

                objective_data = json.loads(request.POST.get('objective', '{}'))
                if objective_data:
                    objective_instance = resume.objective if hasattr(resume, 'objective') else None
                    objective_form = ObjectiveForm(objective_data, instance=objective_instance)

                    if objective_form.is_valid():
                        objective = objective_form.save(commit=False)
                        objective.resume = resume
                        objective.user = user_instance
                        objective.save()

                def save_related_data(form_class, data_list, related_name, existing_items):
                    existing_items.delete()  
                    for item in data_list:
                        form = form_class(item)
                        if form.is_valid():
                            obj = form.save(commit=False)
                            obj.resume = resume
                            obj.user= user_instance
                            obj.save()

                save_related_data(EducationForm, json.loads(request.POST.get('education', '[]')), 'Education', resume.education_entries.all())
                save_related_data(ExperienceForm, json.loads(request.POST.get('experience', '[]')), 'Experience', resume.experience_entries.all())
                save_related_data(ProjectForm, json.loads(request.POST.get('projects', '[]')), 'Projects', resume.projects.all())
                save_related_data(ReferenceForm, json.loads(request.POST.get('references', '[]')), 'References', resume.references.all())
                save_related_data(CertificationForm, json.loads(request.POST.get('certifications', '[]')), 'Certifications', resume.certifications.all())
                save_related_data(AchievementForm, json.loads(request.POST.get('achievements', '[]')), 'Achievements', resume.achievements.all())
                save_related_data(PublicationForm, json.loads(request.POST.get('publications', '[]')), 'Publications', resume.publications.all())

                return JsonResponse({
                    'status': 'success',
                    'message': 'Resume created/updated successfully',
                    'resume_id': resume.id
                })

        except json.JSONDecodeError as e:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON data'}, status=400)
        except IntegrityError as e:
            return JsonResponse({'status': 'error', 'message': 'Database integrity error', 'details': str(e)}, status=500)
        except OperationalError as e:
            return JsonResponse({'status': 'error', 'message': 'Database operational error', 'details': str(e)}, status=500)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

def get_user_resume_detail_by_id(request, user_id, resume_id):
    auth_header = request.headers.get('Authorization')
    
    try:
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({'status': 'error', 'message': 'Token is missing or invalid format'}, status=400)

        token = auth_header.split(' ')[1]

        user= new_user.objects.get(id=user_id,token=token)

        if request.method == 'GET':
            resume = get_object_or_404(Resume, user=user ,id=resume_id)

            resume_data = {
                "first_name": resume.first_name, 
                "last_name": resume.last_name,
                "email": resume.email,
                "phone": resume.phone,
                "address": resume.address,
                "date_of_birth": resume.date_of_birth,
                "website_urls": resume.website_urls,
                "skills": resume.skills,
                "activities": resume.activities,
                "interests": resume.interests,
                "languages": resume.languages,
                "bio": resume.bio,
                "city": resume.city,
                "state": resume.state,
                "country": resume.country,
                "zipcode": resume.zipcode,
                # "attachments": resume.Attachment,
                "objective": resume.objective.text if hasattr(resume, 'objective') else 'Not specified',
                "education": [
                    {
                        "course_or_degree": education.course_or_degree,
                        "school_or_university": education.school_or_university,
                        "grade_or_cgpa": education.grade_or_cgpa,
                        "start_date": education.start_date,
                        "end_date": education.end_date,
                        "description": education.description
                    } for education in resume.education_entries.all()
                ],
                "experience": [
                    {
                        "job_title": experience.job_title,
                        "company_name": experience.company_name,
                        "start_date": experience.start_date,
                        "end_date": experience.end_date,
                        "description": experience.description,
                    } for experience in resume.experience_entries.all()
                ],
                "projects": [
                    {
                        "title": project.title,
                        "description": project.description,
                        "project_link": project.project_link
                    } for project in resume.projects.all()
                ],
                "references": [
                    {
                        "name": reference.name,
                        "contact_info": reference.contact_info,
                        "relationship": reference.relationship,
                    } for reference in resume.references.all()
                ],
                "certifications": [
                    {
                        "name": certification.name,
                        "start_date": certification.start_date,
                        "end_date": certification.end_date,
                    } for certification in resume.certifications.all()
                ],
                "achievements": [
                    {
                        "title": achievement.title,
                        "publisher": achievement.publisher,
                        "start_date": achievement.start_date,
                        "end_date": achievement.end_date,
                    } for achievement in resume.achievements.all()
                ],
                "publications": [
                    {
                        "title": publication.title,
                        "start_date": publication.start_date,
                        "end_date": publication.end_date,
                    } for publication in resume.publications.all()
                ]
            }

            return JsonResponse(resume_data, status=200)
        else:
            return JsonResponse({"error": "Method not allowed"}, status=405)
    except new_user.DoesNotExist:
        return JsonResponse({"error": "Invalid token or job seeker not found"}, status=401)
    except ObjectDoesNotExist:
        return JsonResponse({"error": "Resume not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)   

@csrf_exempt
def count_jobs_by_category(request):
    if request.method == 'GET':
        try:
            category_counts = {}

            jobs = Job.objects.all()

            for job in jobs:
                category = job.category.strip()
                if category and category in category_counts:
                    category_counts[category] += 1
                elif category:
                    category_counts[category] = 1

            response_data = [
                {'category': category, 'job_count': count}
                for category, count in category_counts.items()
            ]

            return JsonResponse({'category_counts': response_data}, safe=False)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method.'}, status=400)

# class CustomObtainAuthToken(ObtainAuthToken):
#     def post(self, request, *args, **kwargs):
#         serializer = self.serializer_class(data=request.data)
#         try:
#             serializer.is_valid(raise_exception=True)
#             user = serializer.validated_data['user']
#             token, created = Token.objects.get_or_create(user=user)
#             message = "New token created" if created else "Existing token retrieved"
#             return Response({
#                 'token': token.key,
#                 'username': user.username,
#                 'message': message
#             })
#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
def fetch_jobs_by_exp_skills(request):
    try:
        if request.method == 'GET':
            experience = request.GET.get('experience')
            skills = request.GET.get('skills')

            skills_list = [skill.strip().lower() for skill in skills.split(',')] if skills else []

            jobs = Job.objects.all()

            if experience:
                jobs = jobs.filter(experience=experience)
            if skills_list:
                queries = Q()
                for skill in skills_list:
                    queries |= Q(skills__icontains=skill)
                jobs = jobs.filter(queries).distinct()

            if not (experience or skills_list):
                return JsonResponse({'error': 'Please enter at least one filter: experience or skills.'}, status=400)

            job_list = []
            for job in jobs:
                job_list.append({
                    'job_title': job.job_title,
                    'company':job.company.name,
                    'location': job.location,
                    'workplaceType': job.workplaceTypes,
                    'description': job.description,
                    'requirements': job.requirements,
                    'job_type': job.job_type,
                    'experience': job.experience,
                    'category': job.category,
                    'required_skills': job.skills,
                    'experience_yr': job.experience_yr,
                })

            return JsonResponse({'jobs': job_list}, safe=False)
        else:
            return JsonResponse({'error': 'Invalid request method.'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def fetch_jobs_by_category_location_skills(request):
    try:
        if request.method == 'GET':
            category = request.GET.get('category')
            location = request.GET.get('location')
            skills = request.GET.get('skills')

            skills_list = [skill.strip().lower() for skill in skills.split(',')] if skills else []

            jobs = Job.objects.all()

            if category:
                jobs = jobs.filter(category=category)
            if location:
                jobs = jobs.filter(location=location)
            if skills_list:
                queries = Q()
                for skill in skills_list:
                    queries |= Q(skills__icontains=skill)
                jobs = jobs.filter(queries).distinct()

            if not (category or location or skills_list):
                return JsonResponse({'error': 'Please enter at least one filter: category, location or skills.'}, status=400)

            job_list = []
            for job in jobs:
                job_list.append({
                    'job_title': job.job_title,
                    'company':job.company.name,
                    'location': job.location,
                    'workplaceType': job.workplaceTypes,
                    'description': job.description,
                    'requirements': job.requirements,
                    'job_type': job.job_type,
                    'experience': job.experience,
                    'category': job.category,
                    'required_skills': job.skills,
                    'experience_yr': job.experience_yr,
                })

            return JsonResponse({'jobs': job_list}, safe=False)
        else:
            return JsonResponse({'error': 'Invalid request method.'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def fetch_job_titles(request):
    if request.method == 'GET':
        try:
            job_titles = Job.objects.exclude(job_title='').values_list('job_title', flat=True).distinct()
            return JsonResponse({'job_title': list(job_titles)})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method.'}, status=400)

def fetch_job_types(request):
    if request.method == 'GET':
        try:
            job_types = Job.objects.exclude(job_type='').values_list('job_type', flat=True).distinct()
            return JsonResponse({'job_types': list(job_types)})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method.'}, status=400)

def fetch_job_experience(request):
    if request.method == 'GET':
        try:
            exp_types = Job.objects.exclude(experience='').values_list('experience', flat=True).distinct()
            return JsonResponse({'exp_types': list(exp_types)})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method.'}, status=400)

def fetch_job_category(request):
    if request.method == 'GET':
        try:
            categories = Job.objects.exclude(category='').values_list('category', flat=True).distinct()
            return JsonResponse({'category': list(categories)})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method.'}, status=400)

def fetch_job_workplaceTypes(request):
    if request.method == 'GET':
        try:
            workplace_types = Job.objects.exclude(workplaceTypes='').values_list('workplaceTypes', flat=True).distinct()
            return JsonResponse({'workplaceTypes': list(workplace_types)})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method.'}, status=400)

def fetch_job_location(request):
    if request.method == 'GET':
        try:
            locations = Job.objects.exclude(location='').values_list('location', flat=True).distinct()
            return JsonResponse({'location': list(locations)})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method.'}, status=400)

def fetch_sector_types(request):
    if request.method == 'GET':
        try:
            sector_types = Company.objects.exclude(sector_type='').values_list('sector_type', flat=True).distinct()
            return JsonResponse({'sector_type': list(sector_types)})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method.'}, status=400)

def fetch_country_types(request):
    if request.method == 'GET':
        try:
            country_names = Company.objects.exclude(country='').values_list('country', flat=True).distinct()
            return JsonResponse({'country_name': list(country_names)})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method.'}, status=400)

def fetch_status_choices(request):
    if request.method == 'GET':
        try:
            status_choices = Application.objects.exclude(status='').values_list('status', flat=True).distinct()
            return JsonResponse({'status': list(status_choices)})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method.'}, status=400)


@csrf_exempt
def user_application_status_counts(request, user_id):
    auth_header = request.headers.get('Authorization')

    try:
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({'error': 'Token is missing or invalid format'}, status=400)

        token = auth_header.split(' ')[1]

        user = new_user.objects.get(id=user_id, token=token)

        email = request.GET.get('email')
        if not email or user.email != email:
            return JsonResponse({'error': 'Invalid email parameter or email does not match'}, status=400)

        total_jobs_applied_count = (
            Application.objects.filter(user=user).count() +
            Application1.objects.filter(user=user).count()
        )

        pending_count = (
            Application.objects.filter(user=user, status='pending').count() +
            Application1.objects.filter(user=user, status='pending').count()
        )

        interview_scheduled_count = (
            Application.objects.filter(user=user, status='interview_scheduled').count() +
            Application1.objects.filter(user=user, status='interview_scheduled').count()
        )

        rejected_count = (
            Application.objects.filter(user=user, status='rejected').count() +
            Application1.objects.filter(user=user, status='rejected').count()
        )

        college_enquiries_count = CollegeEnquiry.objects.filter(new_user=user).count()

        return JsonResponse({
            'total_jobs_applied': total_jobs_applied_count,
            'pending_count': pending_count,
            'interview_scheduled': interview_scheduled_count,
            'rejected_count': rejected_count,
            'total_college_enquiries_count': college_enquiries_count
        })

    except new_user.DoesNotExist:
        return JsonResponse({'error': 'User not found or invalid token'}, status=404)
    except Application.DoesNotExist:
        return JsonResponse({'error': 'No applications found for the provided user.'}, status=404)
    except Exception as e:
        return JsonResponse({'error': 'An error occurred', 'details': str(e)}, status=500)


@csrf_exempt
def filter_user_applied_jobs(request, user_id):
    auth_header = request.headers.get('Authorization')

    try:
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({'error': 'Token is missing or invalid format'}, status=400)

        token = auth_header.split(' ')[1]
		
        user = new_user.objects.get(id=user_id, token=token)

        email = request.GET.get('email')
        if not email or user.email != email:
            return JsonResponse({'error': 'Invalid email parameter or email does not match'}, status=400)

        job_title = request.GET.get('job_title')
        status = request.GET.get('status')
        job_type = request.GET.get('job_type')
        sort_by = request.GET.get('sort_by')

        applications_1 = Application.objects.filter(user=user)
        applications_2 = Application1.objects.filter(user=user)

        if job_title:
            applications_1 = applications_1.filter(job__job_title=job_title)
            applications_2 = applications_2.filter(job__job_title=job_title)

        if status:
            applications_1 = applications_1.filter(status=status)
            applications_2 = applications_2.filter(status=status)

        if job_type:
            applications_1 = applications_1.filter(job__job_type=job_type)
            applications_2 = applications_2.filter(job__job_type=job_type)

        applications = list(chain(applications_1, applications_2))

        if sort_by == 'job_title_asc':
            applications.sort(key=lambda x: x.job.job_title)
        elif sort_by == 'job_title_desc':
            applications.sort(key=lambda x: x.job.job_title, reverse=True)
        elif sort_by == 'applied_at_asc':
            applications.sort(key=lambda x: x.applied_at)
        elif sort_by == 'applied_at_desc':
            applications.sort(key=lambda x: x.applied_at, reverse=True)

        result = []
        for application in applications:
            job = application.job  
            if isinstance(job, Job1): 
                result.append({
                    'job_title': job.job_title,
                    'university_in_charge': job.university_in_charge.university_name,  
                    'job_location': job.location,
                    'job_type': job.job_type,
                    'status': application.status,
                    'applied_at': application.applied_at,
                })
            else:  
                result.append({
                    'job_title': job.job_title,
                    'company': job.company.name,
                    'job_location': job.location,
                    'job_type': job.job_type,
                    'status': application.status,
                    'applied_at': application.applied_at,
                })

        return JsonResponse(result, safe=False)

    except new_user.DoesNotExist:
        return JsonResponse({'error': 'User not found or invalid token'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def sort_saved_jobs(request):
    try:
        sort_order = request.GET.get('sort_order', 'latest')

        jobs = Job.objects.all()

        if sort_order == 'latest':
                jobs = jobs.order_by('-published_at')
        elif sort_order == 'oldest':
                jobs = jobs.order_by('published_at')
        else:
            return JsonResponse({'error': 'Invalid sort order. Use "latest" or "oldest".'}, status=400)

        jobs_list = [{
            'id': job.id,
            'job_title': job.job_title,
            'company':job.company.name,
            'location': job.location,
            'requirements': job.requirements,
            'job_type': job.job_type,
            'experience': job.experience,
            'category': job.category,
            'published_at': job.published_at,
            'skills': job.skills,
            'workplaceTypes': job.workplaceTypes,
        } for job in jobs]

        return JsonResponse({'saved_jobs': jobs_list}, safe=False)

    except ObjectDoesNotExist:
        return JsonResponse({'error': 'Job not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# @csrf_exempt
# def delete_account(request, username):
#     if request.method != 'POST':
#         return JsonResponse({"error": "Invalid request method."}, status=400)

#     try:
#         data = json.loads(request.body)
#         confirm = data.get('confirm', '').lower()

#         if confirm == 'yes':
#             user = User.objects.get(username=username, is_superuser=True)
#             user.delete()
#             return JsonResponse({"message": f"Admin user '{username}' has been deleted successfully."})
#         elif confirm == 'no':
#             return JsonResponse({"message": "Account deletion canceled."})

#         return JsonResponse({"error": "Invalid confirmation input. Please send 'yes' or 'no'."}, status=400)

#     except User.DoesNotExist:
#         return JsonResponse({"error": "Admin user not found."}, status=404)
#     except json.JSONDecodeError:
#         return JsonResponse({"error": "Invalid JSON input."}, status=400)

@csrf_exempt
def save_student(request,user_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    
    user = new_user.objects.filter(id=user_id).first() 
    print(user)
    if not user:
        return JsonResponse({'status': 'error', 'message': 'User not found'}, status=404)

    data = json.loads(request.body)
    email = data.get('email')

    if Student.objects.filter(email=email).exists():
        return JsonResponse({'message': 'Student is already registered with this email'}, status=400)

    form = StudentForm(data)
    if form.is_valid():
        student = form.save(commit=False)
        student.user=user
        student.save()
        return JsonResponse({'message': 'Student data saved successfully', 'student_id': student.id}, status=201)

    return JsonResponse({'errors': form.errors}, status=400)

@csrf_exempt
def fetch_jobs_by_job_seeker_skills(request, job_seeker_id):
    auth_header = request.headers.get('Authorization')

    try:
        if request.method == 'GET':
            if not auth_header or not auth_header.startswith('Bearer '):
                return JsonResponse({'status': 'error', 'message': 'Token is missing or invalid format'}, status=400)

            token = auth_header.split(' ')[1]

            try:
                job_seeker = JobSeeker.objects.get(token=token, id=job_seeker_id)
            except JobSeeker.DoesNotExist:
                return JsonResponse({'error': 'Job Seeker not found.'}, status=404)

            try:
                resume = JobSeeker_Resume.objects.get(job_seeker=job_seeker)
            except JobSeeker_Resume.DoesNotExist:
                return JsonResponse({'error': 'Job Seeker Resume not found.'}, status=404)

            skills = resume.skills
            skills_list = [skill.strip().lower() for skill in skills.split(',')] if skills else []

            if not skills_list:
                return JsonResponse({'error': 'No skills found for this Job Seeker.'}, status=400)

            job_queries = Q()
            for skill in skills_list:
                job_queries |= Q(skills__icontains=skill)

            jobs_from_job_model = Job.objects.filter(job_queries).distinct()
            jobs_from_job1_model = Job1.objects.filter(job_queries).distinct()

            combined_jobs = list(jobs_from_job_model) + list(jobs_from_job1_model)

            sort_order = request.GET.get('sort_order', 'latest')
            if sort_order == 'latest':
                combined_jobs = sorted(combined_jobs, key=lambda x: x.published_at, reverse=True)
            elif sort_order == 'oldest':
                combined_jobs = sorted(combined_jobs, key=lambda x: x.published_at)
            else:
                return JsonResponse({'error': 'Invalid sort order. Use "latest" or "oldest".'}, status=400)

            job_list = []
            for job in combined_jobs:
                if isinstance(job, Job):
                    job_list.append({
                        'company_name': job.company.name,
                        'job_id':job.unique_job_id_as_int,
                        'job_title': job.job_title,
                        'location': job.location,
                        'job_type': job.job_type,
                        'job_posted_date': job.published_at
                    })
                elif isinstance(job, Job1):
                    job_list.append({
                        'college': job.college.college_name,
                        'job_id':job.id,
                        'job_title': job.job_title,
                        'location': job.location,
                        'job_type': job.job_type,
                        'job_posted_date': job.published_at
                    })

            return JsonResponse({'jobs': job_list}, safe=False)
        else:
            return JsonResponse({'error': 'Invalid request method.'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def create_job_alert(request):
    if request.method == 'POST':
        action = request.POST.get('action')

        if action is None:
            return JsonResponse({'status': 'error', 'message': 'Action parameter is missing'}, status=400)

        if action == 'saved':
            return JsonResponse("Job Saved Successfully", safe=False)

        elif action == 'apply':
            return JsonResponse("Applied Successfully", safe=False)

    return JsonResponse({'error': 'Invalid request method'}, status=405)

# @csrf_exempt
# def company_status_counts(request, company_in_charge_id):
#     if request.method != 'GET':
#         return JsonResponse({'error': 'Invalid request method, only GET allowed'}, status=405)

#     auth_header = request.headers.get('Authorization')
#     if not auth_header or not auth_header.startswith('Bearer '):
#         return JsonResponse({'error': 'Token is missing or invalid format'}, status=400)

#     token = auth_header.split(' ')[1]

#     try:
#         company_in_charge = CompanyInCharge.objects.get(id=company_in_charge_id, token=token)

#         company_name = request.GET.get('company_name')
#         if not company_name:
#             return JsonResponse({'error': 'Company name is required'}, status=400)

#         company = Company.objects.get(name=company_name, company_in_charge=company_in_charge)

#         total_applications = Application.objects.filter(job__company=company).count()
#         shortlisted_count = Application.objects.filter(job__company=company, status='shortlisted').count()
#         rejected_count = Application.objects.filter(job__company=company, status='rejected').count()
#         jobs_posted = Job.objects.filter(company=company).count()

#         response_data = {
#             'total_applications': total_applications,
#             'shortlisted_count': shortlisted_count,
#             'rejected_count': rejected_count,
#             'jobs_posted': jobs_posted
#         }

#         return JsonResponse(response_data)

#     except CompanyInCharge.DoesNotExist:
#         return JsonResponse({'error': 'Invalid token or company in charge not found'}, status=404)
#     except Company.DoesNotExist:
#         return JsonResponse({'error': 'Company not found'}, status=404)
#     except Exception as e:
#         return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def company_status_counts(request, company_in_charge_id):
    if request.method != 'GET':
        return JsonResponse({'error': 'Invalid request method, only GET allowed'}, status=405)

    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return JsonResponse({'error': 'Token is missing or invalid format'}, status=400)

    token = auth_header.split(' ')[1]

    try:
        company_in_charge = CompanyInCharge.objects.get(id=company_in_charge_id, token=token)

        company_name = request.GET.get('company_name')
        if not company_name:
            return JsonResponse({'error': 'Company name is required'}, status=400)

        company = Company.objects.get(name=company_name, company_in_charge=company_in_charge)

        total_applications = Application.objects.filter(job__company=company).count()
        shortlisted_count = Application.objects.filter(job__company=company, status='shortlisted').count()
        rejected_count = Application.objects.filter(job__company=company, status='rejected').count()
        jobs_posted = Job.objects.filter(company=company).count()

        jobs_by_month = (
            Job.objects.filter(company=company)
            .annotate(month=TruncMonth('published_at'))
            .values('month')
            .annotate(count=Count('id'))
            .order_by('month')
        )
        applications_by_month = (
            Application.objects.filter(job__company=company)
            .annotate(month=TruncMonth('applied_at'))
            .values('month')
            .annotate(count=Count('id'))
            .order_by('month')
        )
        shortlisted_by_month = (
            Application.objects.filter(job__company=company, status='shortlisted')
            .annotate(month=TruncMonth('applied_at'))
            .values('month')
            .annotate(count=Count('id'))
            .order_by('month')
        )

        rejected_by_month = (
            Application.objects.filter(job__company=company, status='rejected')
            .annotate(month=TruncMonth('applied_at'))
            .values('month')
            .annotate(count=Count('id'))
            .order_by('month')
        )
        response_data = {
            'total_applications': total_applications,
            'shortlisted_count': shortlisted_count,
            'rejected_count': rejected_count,
            'jobs_posted': jobs_posted,
            'jobs_by_month': {job['month'].strftime('%Y-%m'): job['count'] for job in jobs_by_month},
            'applications_by_month': {app['month'].strftime('%Y-%m'): app['count'] for app in applications_by_month},
            'shortlisted_by_month': {app['month'].strftime('%Y-%m'): app['count'] for app in shortlisted_by_month},
            'rejected_by_month': {app['month'].strftime('%Y-%m'): app['count'] for app in rejected_by_month}
        }

        return JsonResponse(response_data)

    except CompanyInCharge.DoesNotExist:
        return JsonResponse({'error': 'Invalid token or company in charge not found'}, status=404)
    except Company.DoesNotExist:
        return JsonResponse({'error': 'Company not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def jobs_by_company(request, company_in_charge_id):
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({'error': 'Token is missing or in an invalid format'}, status=400)

        token = auth_header.split(' ')[1]

        company_in_charge = CompanyInCharge.objects.get(id=company_in_charge_id, token=token)

        company_name = request.GET.get('name')
        sort_order = request.GET.get('sort_order')
        job_status = request.GET.get('job_status')

        if not (company_name or sort_order or job_status):
            return JsonResponse({'error': 'Select at least one parameter'}, status=400)

        jobs = Job.objects.all()
        
        if company_name:
            company = get_object_or_404(Company, name=company_name, company_in_charge=company_in_charge)
            jobs = jobs.filter(company=company)

        if job_status:
            if job_status.lower() == 'active':
                jobs = jobs.filter(job_status='active')
            elif job_status.lower() == 'closed':
                jobs = jobs.filter(job_status='closed')
            else:
                return JsonResponse({'error': 'Invalid job status'}, status=400)

        if sort_order:
            if sort_order == 'latest':
                jobs = jobs.order_by('-published_at')
            elif sort_order == 'oldest':
                jobs = jobs.order_by('published_at')
            else:
                return JsonResponse({'error': 'Invalid sort order'}, status=400)

        jobs_list = [{
            'id': job.id,
            'company_in_charge': str(company_in_charge),
            'job_title': job.job_title,
            'location': job.location,
            'description': job.description,
            'requirements': job.requirements,
            'job_type': job.job_type,
            'experience': job.experience,
            'category': job.category,
            'published_at': job.published_at,
            'status': job.job_status
        } for job in jobs]

        return JsonResponse(jobs_list, safe=False, status=200)

    except CompanyInCharge.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Invalid token or company in charge not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def save_screening_questions_and_answers_for_company(request, company_in_charge_id):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)
    
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return JsonResponse({'status': 'error', 'message': 'Token is missing or in an invalid format'}, status=400)

    token = auth_header.split(' ')[1]

    try:
        company_in_charge = CompanyInCharge.objects.get(token=token, id=company_in_charge_id)
    except CompanyInCharge.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Invalid token or company in charge not found'}, status=401)

    try:
        data = json.loads(request.body.decode('utf-8'))
        job_id = data.get('job_id')
        questions_and_answers = data.get('questions_and_answers')

        if not job_id:
            return JsonResponse({'status': 'error', 'message': 'Job ID is missing'}, status=400)
        if not questions_and_answers:
            return JsonResponse({'status': 'error', 'message': 'Questions and answers are missing'}, status=400)
			
        try:
            job = Job.objects.get(id=job_id, company_in_charge=company_in_charge)
        except Job.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Job not found'}, status=404)

        for qa in questions_and_answers:
            question_text = qa.get('question')
            correct_answer = qa.get('correct_answer')

            CompanyScreeningQuestion.objects.create(
                job=job,
                question_text=question_text,
                correct_answer=correct_answer,
                company_in_charge=company_in_charge
            )

        return JsonResponse({'status': 'success', 'message': 'Questions and answers saved successfully'}, status=201)

    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON format'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@csrf_exempt
def submit_application_with_screening_for_company(request, job_id, company_in_charge_id):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)
    
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return JsonResponse({'status': 'error', 'message': 'Token is missing or in an invalid format'}, status=400)

    token = auth_header.split(' ')[1]

    try:
        company_in_charge = CompanyInCharge.objects.get(token=token, id=company_in_charge_id)
    except CompanyInCharge.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Invalid token or company in charge not found'}, status=401)

    try:
        job = Job.objects.get(id=job_id)
    except Job.DoesNotExist:
        return JsonResponse({"error": "Job not found"}, status=404)

    try:
        data = json.loads(request.body)
        email = data.get('email')
        skills = data.get('skills')
        must_have_qualification = data.get('must_have_qualification', False)
        answers = data.get('answers')

        if not email or not answers:
            return JsonResponse({"error": "Email or answers are missing"}, status=400)

        newuser = new_user.objects.filter(email=email).first()
        jobseeker = JobSeeker.objects.filter(email=email).first()
        
        if not newuser and not jobseeker:
            return JsonResponse({"error": "No registration found for NewUser or JobSeeker with this email"}, status=404)

        first_question_id = answers[0].get('question_id')
        if not first_question_id:
            return JsonResponse({"error": "First question ID is missing"}, status=400)

        if not CompanyScreeningQuestion.objects.filter(id=first_question_id, job=job).exists():
            return JsonResponse({"error": f"Invalid question_id: {first_question_id}"}, status=404)

        if Application.objects.filter(job=job, user=newuser, job_seeker=jobseeker, company_in_charge=company_in_charge).exists():
            return JsonResponse({"error": f"Application for this job has already been submitted by {email}."}, status=400)

        application = Application.objects.create(
            job=job,
            email=email,
            skills=skills,
            status="pending",
            user=newuser,
            job_seeker=jobseeker,
            company_in_charge=company_in_charge,
            first_name=newuser.firstname if newuser else jobseeker.first_name,
            last_name=newuser.lastname if newuser else jobseeker.last_name
        )
		
        correct_answers = {q.id: q.correct_answer for q in CompanyScreeningQuestion.objects.filter(job=job)}
        all_answers_correct = True

        for answer_data in answers:
            question_id = answer_data.get('question_id')
            answer_text = answer_data.get('answer')

            if not question_id or not answer_text:
                return JsonResponse({"error": "Question ID or answer is missing"}, status=400)

            question = CompanyScreeningQuestion.objects.filter(id=question_id, job=job).first()
            if not question:
                return JsonResponse({"error": f"Invalid question_id: {question_id}"}, status=404)

            is_correct = (correct_answers.get(question.id) == answer_text)

            CompanyScreeningAnswer.objects.create(
                application=application,
                question=question,
                answer_text=answer_text,
                company_in_charge=company_in_charge
            )

            if not is_correct:
                all_answers_correct = False

        if all_answers_correct and must_have_qualification:
            application.status = 'selected'
            application.save()

            email_subject = "Job Application Status"
            email_body = f"Dear Applicant,\n\nYour application for the job {job.job_title} has been accepted."
            send_mail(email_subject, email_body, settings.EMAIL_HOST_USER, [application.email], fail_silently=False)
            return JsonResponse({"message": "Application submitted successfully and applicant selected."}, status=201)

        elif must_have_qualification and not all_answers_correct:
            application.status = 'rejected'
            application.save()

            email_subject = "Job Application Status"
            email_body = f"Dear Applicant,\n\nUnfortunately, your application for the job {job.job_title} has been rejected."
            send_mail(email_subject, email_body, settings.EMAIL_HOST_USER, [application.email], fail_silently=False)
            return JsonResponse({"message": "Application submitted successfully and applicant rejected."}, status=201)

        elif not must_have_qualification and all_answers_correct:
            application.status = 'pending'
            application.save()
            return JsonResponse({"message": "Applicant moves to the above list."}, status=201)

        else:
            application.status = 'pending'
            application.save()
            return JsonResponse({"message": "Applicant moves to the below list."}, status=201)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

### Company to new_user and jobseeker
@csrf_exempt
def myInbox(request):
    if request.method != "GET":
        return JsonResponse({'status': 'false', 'message': 'Invalid request method'}, status=405)
    
    email = request.GET.get('email')
    if not email:
        return JsonResponse({'status': 'false', 'message': 'Email is required'}, status=400)
    
    filter_value = request.GET.get('filter')    

    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return JsonResponse({'error': 'Token is missing or in an invalid format'}, status=400)

    token = auth_header.split(' ')[1]

    try:
        company_in_charge = CompanyInCharge.objects.get(token=token)
        
        if company_in_charge.official_email != email:
            return JsonResponse({'status': 'false', 'message': 'Sender email does not match the token'}, status=403)
        
        messages_query = Message.objects.filter(
            Q(receiptent_new_user__email=email) | 
            Q(receiptent_job_seeker__email=email) | 
            Q(company_in_charge=company_in_charge)
        ).order_by('-timestamp')

        if filter_value in ['read', 'unread']:
            is_read = filter_value == 'read'
            messages_query = messages_query.filter(is_read=is_read)
        
        message_list = [
            {
                'id': message.id,
                'sender_email': message.company_in_charge.official_email,
                'recipient_email': (
                    message.receiptent_new_user.email if message.receiptent_new_user else
                    message.receiptent_job_seeker.email
                ),
                'content': message.content,
                'timestamp': message.timestamp,
                'is_read': message.is_read,
                'attachments': [
                    {
                        'id': attachment.id,
                        'file_url': attachment.file.url,
                        'uploaded_at': attachment.uploaded_at
                    } for attachment in message.attachments.all()
                ]
            }
            for message in messages_query
        ]

        return JsonResponse({'status': 'success', 'messages': message_list}, status=200)

    except CompanyInCharge.DoesNotExist:
        return JsonResponse({'status': 'false', 'message': 'Invalid token'}, status=403)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@csrf_exempt
def getMessages(request):
    if request.method != "GET":
        return JsonResponse({'status': 'false', 'message': 'Invalid request method'}, status=405)

    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return JsonResponse({'error': 'Token is missing or in an invalid format'}, status=400)

    token = auth_header.split(' ')[1]
    
    sender_email = request.GET.get('sender_email')
    recipient_email = request.GET.get('recipient_email')

    if not all([sender_email, recipient_email]):
        return JsonResponse({'status': 'false', 'message': 'Required fields missing'}, status=400)
    
    try:
        company_in_charge = CompanyInCharge.objects.get(token=token,official_email=sender_email)
        
        if company_in_charge.official_email != sender_email:
            return JsonResponse({'status': 'false', 'message': 'Sender email does not match the token'}, status=403)

        receipent_user = new_user.objects.filter(email=recipient_email).first()
        receipent_jobseeker = JobSeeker.objects.filter(email=recipient_email).first()

        if not receipent_user and not receipent_jobseeker:
            return JsonResponse({'status': 'false', 'message': 'Recipient not found'}, status=404)

        all_messages = Message.objects.filter(
            Q(receiptent_new_user=receipent_user) | Q(receiptent_job_seeker=receipent_jobseeker),
            company_in_charge=company_in_charge
        ).prefetch_related('attachments')

        if not all_messages.exists():
            return JsonResponse({'status': 'false', 'message': 'No messages found'}, status=404)

        all_messages.filter(is_read=False).update(is_read=True)

        messages_data = [
            {
                'message_id': message.id,
                'sender_email': message.company_in_charge.official_email,
                'recipient_email': (
                    message.receiptent_new_user.email if message.receiptent_new_user else
                    message.receiptent_job_seeker.email
                ),
                'content': message.content,
                'timestamp': message.timestamp,
                'is_read': message.is_read,
                'attachments': [
                    {
                        'file_url': attachment.file.url,
                        'uploaded_at': attachment.uploaded_at
                    }
                    for attachment in message.attachments.all()
                ]
            }
            for message in all_messages
        ]
        return JsonResponse({'status': 'success', 'messages': messages_data}, status=200)

    except CompanyInCharge.DoesNotExist:
        return JsonResponse({'status': 'false', 'message': 'Invalid token'}, status=403)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@csrf_exempt
def sendMessage(request):
    if request.method != "POST":
        return JsonResponse({'status': 'false', 'message': 'Invalid request method'}, status=405)

    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return JsonResponse({'error': 'Token is missing or invalid format'}, status=400)

    token = auth_header.split(' ')[1]

    sender_email = request.POST.get('sender_email')
    recipient_email = request.POST.get('recipient_email')
    message_content = request.POST.get('content')

    if not all([sender_email, recipient_email, message_content]):
        return JsonResponse({'status': 'false', 'message': 'Required fields missing'}, status=400)

    try:
        company_in_charge = CompanyInCharge.objects.get(token=token,official_email=sender_email)
        
        if company_in_charge.official_email != sender_email:
            return JsonResponse({'status': 'false', 'message': 'Sender email does not match the token'}, status=403)

        receiptent_new_user = new_user.objects.filter(email=recipient_email).first()
        receiptent_job_seeker = JobSeeker.objects.filter(email=recipient_email).first()

        if not receiptent_new_user and not receiptent_job_seeker:
            return JsonResponse({'status': 'false', 'message': 'Recipient not found'}, status=404)

        message = Message.objects.create(
            company_in_charge=company_in_charge,
            receiptent_new_user=receiptent_new_user if receiptent_new_user else None,
            receiptent_job_seeker=receiptent_job_seeker if receiptent_job_seeker else None,
            content=message_content
        )

        attachments = request.FILES.getlist('attachments', [])
        Attachment.objects.bulk_create([
            Attachment(message=message, file=file) for file in attachments
        ])

        email_subject = f'New Message from {sender_email}'
        email_body = (
            f'You have received a new message from {sender_email}.\n\n'
            f'Content: {message_content}\n\n'
            'You can view the message in your inbox.'
        )
        send_mail(
            email_subject,
            email_body,
            settings.EMAIL_HOST_USER,
            [recipient_email],
            fail_silently=False,
        )

        return JsonResponse({'status': 'success', 'message': 'Message sent successfully!'}, status=201)

    except CompanyInCharge.DoesNotExist:
        return JsonResponse({'status': 'false', 'message': 'Invalid token'}, status=403)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@csrf_exempt
def searchUser(request):
    if request.method != "GET":
        return JsonResponse({'status': 'false', 'message': 'Invalid request method'}, status=405)
	
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
             return JsonResponse({'error': 'Token is missing or in an invalid format'}, status=400)
        
        token = auth_header.split(' ')[1]
        sender_email = request.GET.get('sender_email')
       
        company_in_charge = CompanyInCharge.objects.get(token=token)
        
        if company_in_charge.official_email != sender_email:
            return JsonResponse({'status': 'false', 'message': 'Sender email does not match the token'}, status=403)

        query = request.GET.get('q', '').strip()

        student_contacts = new_user.objects.all().values('id', 'firstname', 'lastname', 'email')
        jobseeker_contacts = JobSeeker.objects.all().values('id', 'first_name', 'last_name', 'email')
        company_contacts = CompanyInCharge.objects.all().values('id', 'company_name', 'official_email')

        if query:
            student_contacts = student_contacts.filter(
                Q(firstname__icontains=query) |
                Q(email__icontains=query)
            )
            jobseeker_contacts = jobseeker_contacts.filter(
                Q(first_name__icontains=query) |
                Q(email__icontains=query)
            )
            company_contacts = company_contacts.filter(
                Q(company_name__icontains=query) |
                Q(official_email__icontains=query)
            )
        
        if not query:
            return JsonResponse({'status': 'success', 'contacts': []}, status=200)    

        contact_list = list(student_contacts) + list(jobseeker_contacts) + list(company_contacts)

        return JsonResponse({
            'status': 'success',
            'contacts': contact_list
        }, status=200)

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

# @csrf_exempt
# @login_required
# def choose_plan(request):
#     try:
#         subscription, _ = UserSubscription.objects.get_or_create(user=request.user)

#         if request.method == 'POST':
#             form = SubscriptionForm(request.POST)
#             if form.is_valid():
#                 plan_id = form.cleaned_data['plan']
#                 membership_plan = MembershipPlan.objects.get(id=plan_id)

#                 subscription.current_plan = membership_plan
#                 subscription.save()

#                 return JsonResponse({'message': 'Subscription plan updated successfully'}, status=200)
#             else:
#                 return JsonResponse({'errors': form.errors}, status=400)
#         else:
#             initial_plan = subscription.current_plan if subscription.current_plan in MembershipPlan.objects.all() else None
#             form = SubscriptionForm(initial={'plan': initial_plan})

#             plan_choices = [{'id': plan.id, 'name': plan.name} for plan in form.fields['plan'].queryset]

#             return JsonResponse({
#                 'message': 'Choose a plan',
#                 'current_plan': subscription.current_plan.name if subscription.current_plan else None,
#                 'plan_choices': plan_choices
#             })

#     except DatabaseError as db_err:
#         return JsonResponse({'error': 'Database error occurred', 'details': str(db_err)}, status=500)
#     except MembershipPlan.DoesNotExist:
#         return JsonResponse({'error': 'Selected plan does not exist'}, status=400)
#     except Exception as e:
#         return JsonResponse({'error': 'An unexpected error occurred', 'details': str(e)}, status=500)

# @csrf_exempt
# @login_required
# def cancel_plan(request):
#     try:
#         subscription = get_object_or_404(UserSubscription, user=request.user)

#         if request.method == 'POST':
#             form = CancelSubscriptionForm(request.POST)
#             if form.is_valid():
#                 form.cancel_subscription(user=request.user)
#                 return JsonResponse({'message': 'Subscription cancelled successfully'}, status=200)
#             else:
#                 return JsonResponse({'errors': form.errors}, status=400)
#         else:
#             return JsonResponse({
#                 'message': 'Confirm cancellation',
#                 'current_plan': subscription.current_plan.name if subscription.current_plan else 'No Plan',
#                 'active': subscription.active
#             })

#     except DatabaseError as db_err:
#         return JsonResponse({'error': 'Database error occurred', 'details': str(db_err)}, status=500)
#     except Exception as e:
#         return JsonResponse({'error': 'An unexpected error occurred', 'details': str(e)}, status=500)

# @login_required
# def subscription_detail(request):
#     try:
#         subscription = get_object_or_404(UserSubscription, user=request.user)

#         subscription_data = {
#             'plan_name': subscription.current_plan.name if subscription.current_plan else 'No Plan',
#             'renewal_date': subscription.renewal_date,
#             'active': subscription.active,
#         }

#         return JsonResponse(subscription_data, status=200)

#     except DatabaseError as db_err:
#         return JsonResponse({'error': 'Database error occurred', 'details': str(db_err)}, status=500)
#     except Exception as e:
#         return JsonResponse({'error': 'An unexpected error occurred', 'details': str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class CollegeListCreateView(View):
    def post(self, request, university_in_charge_id):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({'status': 'error', 'message': 'Token is missing or invalid format'}, status=400)

        token = auth_header.split(' ')[1]

        try:
            university_in_charge = UniversityInCharge.objects.get(id=university_in_charge_id, token=token)
        except UniversityInCharge.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Invalid token or university in charge not found'}, status=404)

        try:
            college_email = request.POST.get('email')
            if not college_email:
                return JsonResponse({'status': 'error', 'message': 'Email is required'}, status=400)

            if college_email != university_in_charge.official_email:
                return JsonResponse({'status': 'error', 'message': 'Email does not match university in charge email'}, status=400)

            college = College.objects.filter(email=college_email).first()

            if college:
                college_form = CollegeForm(request.POST, request.FILES, instance=college)
            else:
                college_form = CollegeForm(request.POST, request.FILES)

            if college_form.is_valid():
                college = college_form.save(commit=False)
                college.university_in_charge = university_in_charge
                college.save()

                if request.POST.get('is_deleted', 'false').lower() == 'true' and college.Attachment:
                    attachment_path = college.Attachment.path
                    if os.path.exists(attachment_path):
                        os.remove(attachment_path)
                    college.Attachment = None
                    college.save(update_fields=['Attachment'])

                    return JsonResponse({'status': 'success', 'message': 'Attachment deleted successfully', 'college_id': college.id}, status=200)

                return JsonResponse({'status': 'success', 'message': 'College created/updated successfully', 'college_id': college.id}, status=201)
            else:
                return JsonResponse(college_form.errors, status=400)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def submit_college_enquiry(request, user_id, college_id):
    auth_header = request.headers.get('Authorization')

    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    
    try:
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({'error': 'Token is missing or invalid format'}, status=400)

        token = auth_header.split(' ')[1]
		
        user = new_user.objects.get(id=user_id, token=token)

        data = json.loads(request.body)
        
        if user.email != data.get("email"):
            return JsonResponse({"error":"User is not register with this email"},status=403)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except new_user.DoesNotExist:
        return JsonResponse({'error': 'User not found or invalid token'}, status=404)

    required_fields = ['first_name', 'last_name', 'email', 'mobile_number', 'course', 'status']
    if not all(data.get(field) for field in required_fields):
        return JsonResponse({'error': 'All fields are required'}, status=400)

    first_name, last_name, email, mobile_number, course, status = (
        data['first_name'], data['last_name'], data['email'], data['mobile_number'], data['course'], data['status']
    )

    try:
        college = College.objects.get(id=college_id)
    except College.DoesNotExist:
        return JsonResponse({'error': 'Invalid college ID'}, status=400)

    if CollegeEnquiry.objects.filter(college=college, new_user=user).exists():
        return JsonResponse({'error': 'An enquiry has already been submitted for this college by this user.'}, status=400)

    try:
        enquiry = CollegeEnquiry.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            mobile_number=mobile_number,
            course=course,
            status=status,
            college=college,
            new_user=user 
        )
        return JsonResponse({'message': 'Enquiry submitted successfully', 'enquiry_id': enquiry.id}, status=201)
    except IntegrityError:
        return JsonResponse({'error': 'Error while saving enquiry. Please try again.'}, status=400)

@csrf_exempt
def get_user_enquiries(request, user_id):
    auth_header = request.headers.get('Authorization')

    if request.method != 'GET':
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    
    try:
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({'error': 'Token is missing or invalid format'}, status=400)

        token = auth_header.split(' ')[1]
		
        user = new_user.objects.get(id=user_id, token=token)

        enquiries = CollegeEnquiry.objects.filter(new_user=user).select_related('college')
        enquiries_data = []
        for enquiry in enquiries:
            enquiries_data.append({
                'college_name': enquiry.college.college_name if enquiry.college else "N/A",
                'first_name': enquiry.first_name,
                'last_name': enquiry.last_name,
                'course': enquiry.course,
                'status': enquiry.status,
            })
        
        return JsonResponse({'enquiries': enquiries_data}, status=200)

    except new_user.DoesNotExist:
        return JsonResponse({'error': 'User not found or invalid token.'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
@csrf_exempt
def college_status_counts(request, university_in_charge_id):
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return JsonResponse({'status': 'error', 'message': 'Token is missing or invalid format'}, status=400)

    token = auth_header.split(' ')[1]

    try:
        university_in_charge = UniversityInCharge.objects.get(id=university_in_charge_id, token=token)
    except UniversityInCharge.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Invalid token or university in charge not found'}, status=404)

    college_id = request.GET.get('college_id')

    if not college_id:
        return JsonResponse({'error': 'college_id is required'}, status=400)

    try:
        college_id = int(college_id)
    except ValueError:
        return JsonResponse({'error': 'Invalid college_id. It must be an integer.'}, status=400)

    if not College.objects.filter(id=college_id, university_in_charge=university_in_charge).exists():
        return JsonResponse({'error': 'College not found'}, status=404)

    try:
        enquiry_count = StudentEnquiry.objects.filter(college_id=college_id, university_in_charge=university_in_charge).count()
        job_posted_count = Job1.objects.filter(college_id=college_id, university_in_charge=university_in_charge).count()
        total_visitor_count = Visitor.objects.filter(college_id=college_id, university_in_charge=university_in_charge).count()
        shortlisted_count = Application1.objects.filter(job__college_id=college_id, university_in_charge=university_in_charge, status='shortlisted').count()

        return JsonResponse({
            'total_visitor_count': total_visitor_count,
            'shortlisted_count': shortlisted_count,
            'job_posted_count': job_posted_count,
            'enquiry_count': enquiry_count
        }, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def create_job_for_college(request, university_incharge_id):

    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return JsonResponse({'error': 'Token is missing or invalid format'}, status=400)

    token = auth_header.split(' ')[1]

    try:
        university_in_charge = UniversityInCharge.objects.get(token=token, id=university_incharge_id)
    except UniversityInCharge.DoesNotExist:
        return JsonResponse({'error': 'Invalid token or university in charge not found'}, status=401)

    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            college_id = data.get('college')
            if not college_id:
                return JsonResponse({'error': 'College ID is required'}, status=400)

            try:
                university_in_charge = UniversityInCharge.objects.get(id=university_incharge_id)
            except UniversityInCharge.DoesNotExist:
                return JsonResponse({'error': 'UniversityInCharge not found'}, status=404)

            try:
                college = College.objects.get(id=college_id, university_in_charge=university_in_charge)
            except College.DoesNotExist:
                return JsonResponse({'error': 'College not found'}, status=404)
            
            if Job1.objects.filter(college=college).count() >= 100:
                return JsonResponse({'message': 'Limit exceeded for job postings by this company'}, status=200)


            form = Job1Form(data)
            if form.is_valid():
                jobs = form.save(commit=False)
                jobs.college = college
                jobs.university_in_charge = university_in_charge
                jobs.save()

                return JsonResponse({'message': 'Job created successfully'}, status=201)

            else:
                return JsonResponse({'error': 'Invalid form data', 'errors': form.errors}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method. Use POST.'}, status=405)

@csrf_exempt
def apply_college_job(request, job_id, university_in_charge_id):
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return JsonResponse({'status': 'error', 'message': 'Token is missing or invalid format'}, status=400)

    token = auth_header.split(' ')[1]

    try:
        university_in_charge = UniversityInCharge.objects.get(id=university_in_charge_id, token=token)
    except UniversityInCharge.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Invalid token or university in charge not found'}, status=404)

    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        json_data = json.loads(request.POST.get('data', '{}'))
        job = get_object_or_404(Job1, id=job_id, university_in_charge=university_in_charge)

        email = json_data.get('email')
        if not email:
            return JsonResponse({'error': 'Email is required'}, status=400)

        if Application1.objects.filter(Q(email=email) & Q(job=job)).exists():
            return JsonResponse({'error': 'An application with this email already exists for this job.'}, status=400)

        new_user_exists = new_user.objects.filter(email=email).exists()
        job_seeker_exists = JobSeeker.objects.filter(email=email).exists()

        if not new_user_exists and not job_seeker_exists:
            return JsonResponse({'error': 'No account found for this email in NewUser or JobSeeker'}, status=404)
        
        form = Application1Form(json_data, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.university_in_charge = university_in_charge

            job_skills = set(job.skills.split(', '))
            candidate_skills = set(json_data.get('skills', '').split(', '))
            application.skills = ', '.join(candidate_skills)

            if not job_skills.intersection(candidate_skills):
                return JsonResponse({'message': 'Candidate is not eligible to apply'}, status=404)

            application.save()
            return JsonResponse({'message': 'Application submitted successfully', 'application_id': application.id}, status=201)

        return JsonResponse({'errors': form.errors}, status=400)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def register_visitor(request, college_id, university_in_charge_id):
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return JsonResponse({'status': 'error', 'message': 'Token is missing or invalid format'}, status=400)

    token = auth_header.split(' ')[1]

    try:
        university_in_charge = UniversityInCharge.objects.get(id=university_in_charge_id, token=token)
    except UniversityInCharge.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Invalid token or university in charge not found'}, status=404)

    if request.method != "POST":
        return JsonResponse({'error': 'Invalid request method'}, status=405)

    try:
        data = json.loads(request.body.decode('utf-8'))
        
        college = get_object_or_404(College, id=college_id, university_in_charge=university_in_charge)

        email = data.get('email')
        if not email:
            return JsonResponse({'error': 'Email is required'}, status=400)

        if Visitor.objects.filter(email=email, college=college).exists():
            return JsonResponse({'error': 'Visitor already registered'}, status=400)

        form = VisitorRegistrationForm(data=data)
        if form.is_valid():
            visitor = form.save(commit=False)
            visitor.password = make_password(data.get('password'))
            visitor.college = college
            visitor.university_in_charge = university_in_charge
            visitor.save()

            return JsonResponse({'message': 'Visitor registered successfully'}, status=201)
        else:
            return JsonResponse({'error': form.errors}, status=400)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON format'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def login_visitor(request, university_in_charge_id):
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return JsonResponse({'status': 'error', 'message': 'Token is missing or invalid format'}, status=400)

    token = auth_header.split(' ')[1]

    try:
        university_in_charge = UniversityInCharge.objects.get(id=university_in_charge_id, token=token)
    except UniversityInCharge.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Invalid token or university in charge not found'}, status=404)

    if request.method != "POST":
        return JsonResponse({'error': 'Invalid request method'}, status=405)

    try:
        data = json.loads(request.body.decode('utf-8'))
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return JsonResponse({'error': 'Email and password are required'}, status=400)

        visitor = get_object_or_404(Visitor, email=email, university_in_charge=university_in_charge)

        if check_password(password, visitor.password):
            return JsonResponse({'message': 'Login successful'}, status=200)
        else:
            return JsonResponse({'error': 'Invalid credentials'}, status=400)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON format'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def college_jobs_api(request, college_id, university_in_charge_id):
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return JsonResponse({'status': 'error', 'message': 'Token is missing or invalid format'}, status=400)

    token = auth_header.split(' ')[1]

    try:
        university_in_charge = UniversityInCharge.objects.get(id=university_in_charge_id, token=token)
    except UniversityInCharge.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Invalid token or university in charge not found'}, status=404)

    try:
        jobs = Job1.objects.filter(college_id=college_id, university_in_charge=university_in_charge).values('job_title', 'location', 'job_status')

        if not jobs:
            return JsonResponse({"message": "No jobs found for the given college ID"}, status=404)

        return JsonResponse(list(jobs), safe=False, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def student_enquiries(request, college_id, university_in_charge_id):
    try:
        try:
           university_in_charge = UniversityInCharge.objects.get(id=university_in_charge_id)
        except UniversityInCharge.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'University in charge not found'}, status=404)
        
        jobs = StudentEnquiry.objects.filter(college_id=college_id,university_in_charge=university_in_charge).values('first_name','last_name','course','status')

        if not jobs:
            return JsonResponse({"message": "No enquiries found for the given college ID"}, status=404)

        return JsonResponse(list(jobs), safe=False, status=200)

    except ObjectDoesNotExist:
        return JsonResponse({"error": "Invalid college ID"}, status=400)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def jobs_by_college(request, university_in_charge_id):

    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return JsonResponse({'status': 'error', 'message': 'Token is missing or invalid format'}, status=400)

    token = auth_header.split(' ')[1]

    try:
        university_in_charge = UniversityInCharge.objects.get(id=university_in_charge_id, token=token)
    except UniversityInCharge.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Invalid token or university in charge not found'}, status=404)

    try:
        college_id = request.GET.get('college_id')
        sort_order = request.GET.get('sort_order')
        job_status = request.GET.get('job_status')

        if not (college_id or sort_order or job_status):
            return JsonResponse({'error': 'Select at least one parameter'}, status=400)

        jobs = Job1.objects.all()

        if college_id:
            college = get_object_or_404(College, id=college_id, university_in_charge=university_in_charge)
            jobs = jobs.filter(college=college)

        if job_status:
            job_status = job_status.lower()
            if job_status in ['active', 'closed']:
                jobs = jobs.filter(job_status=job_status)
            else:
                return JsonResponse({'error': 'Invalid job status'}, status=400)

        if sort_order in ['latest', 'oldest']:
            order = '-published_at' if sort_order == 'latest' else 'published_at'
            jobs = jobs.order_by(order)
        elif sort_order:
            return JsonResponse({'error': 'Invalid sort order'}, status=400)

        jobs_list = [{
            'id': job.id,
            'university_in_charge': str(university_in_charge),
            'job_title': job.job_title,
            'location': job.location,
            'description': job.description,
            'requirements': job.requirements,
            'job_type': job.job_type,
            'experience': job.experience,
            'category': job.category,
            'published_at': job.published_at,
            'status': job.job_status
        } for job in jobs]

        return JsonResponse(jobs_list, safe=False, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def student_enquiries_for_college(request, college_id, university_in_charge_id):
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return JsonResponse({'status': 'error', 'message': 'Token is missing or invalid format'}, status=400)

    token = auth_header.split(' ')[1]

    try:
        university_in_charge = UniversityInCharge.objects.get(id=university_in_charge_id, token=token)
    except UniversityInCharge.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Invalid token or university in charge not found'}, status=404)

    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    required_fields = ['first_name', 'last_name', 'email', 'mobile_number', 'course', 'status']
    if not all(data.get(field) for field in required_fields):
        return JsonResponse({'error': 'All fields are required'}, status=400)

    try:
        college = College.objects.get(id=college_id, university_in_charge=university_in_charge)
    except College.DoesNotExist:
        return JsonResponse({'error': 'College not found'}, status=404)

    user_email = data.get('email')

    try:
        user = new_user.objects.get(email=user_email)
    except new_user.DoesNotExist:
        return JsonResponse({'error': 'User not found. Please ensure correct email'}, status=404)

    if StudentEnquiry.objects.filter(new_user=user, college=college).exists():
        return JsonResponse({'error': 'You have already submitted an enquiry for this college.'}, status=400)

    try:
        enquiry = StudentEnquiry.objects.create(
            first_name=user.firstname,
            last_name=user.lastname,
            email=user.email,
            mobile_number=user.phonenumber,
            course=data['course'],
            status=data['status'],
            college=college,
            university_in_charge=college.university_in_charge,
            new_user=user
        )
        return JsonResponse({'message': 'Enquiry submitted successfully', 'enquiry_id': enquiry.id}, status=201)
    except IntegrityError:
        return JsonResponse({'error': 'Error while saving enquiry. Please try again.'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def get_student_enquiries_for_college(request, college_id, university_in_charge_id):
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return JsonResponse({'status': 'error', 'message': 'Token is missing or invalid format'}, status=400)

    token = auth_header.split(' ')[1]

    try:
        university_in_charge = UniversityInCharge.objects.get(id=university_in_charge_id, token=token)
    except UniversityInCharge.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Invalid token or university in charge not found'}, status=404)

    if request.method != 'GET':
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    
    try:
        college = College.objects.get(id=college_id, university_in_charge=university_in_charge)
    except College.DoesNotExist:
        return JsonResponse({'error': 'College not found'}, status=404)
    
    try:
        enquiries = StudentEnquiry.objects.filter(college=college, university_in_charge=university_in_charge)

        enquiries_data = [
            {
                'first_name': enquiry.first_name,
                'last_name': enquiry.last_name,
                'course': enquiry.course,
                'status': enquiry.status,
            }
            for enquiry in enquiries
        ]
        
        return JsonResponse({'enquiries': enquiries_data}, status=200)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def fetch_company_applicants_count(request, company_in_charge_id):

    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return JsonResponse({'error': 'Token is missing or invalid format'}, status=400)

    token = auth_header.split(' ')[1]
	
    try:
        company_in_charge = CompanyInCharge.objects.get(id=company_in_charge_id, token=token)
        
        job_title = request.GET.get('job_title')
        
        if  not job_title:
            return JsonResponse({'error': 'job_title parameters are required.'}, status=400)

        company = get_object_or_404(Company, company_in_charge=company_in_charge)
        job = get_object_or_404(Job, job_title=job_title, company=company)

        applicants = Application.objects.filter(job=job)

        applicants_list = list(applicants)
        applicants_count = len(applicants_list)

        return JsonResponse({
            'applicants_count': applicants_count,
            # 'applicants': applicants_list
        })

    except CompanyInCharge.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Company in charge not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def schedule_interview_from_company(request, company_in_charge_id):
    if request.method != "POST":
        return JsonResponse({'error': 'Invalid request method. Please use POST.'}, status=405)
    
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return JsonResponse({'error': 'Token is missing or invalid format'}, status=400)

    token = auth_header.split(' ')[1]

    try:
        company_in_charge = CompanyInCharge.objects.get(id=company_in_charge_id, token=token)
    except CompanyInCharge.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Company in charge not found'}, status=404)

    try:
        data = json.loads(request.body)

        action = data.get('action')
        applicant_id = data.get('applicant_id')
        interview_round = data.get('round')
        interview_date = data.get('interview_date')

        if not action or not applicant_id or not interview_round or not interview_date:
            return JsonResponse({'error': 'action, applicant_id, round, and interview_date parameters are required.'}, status=400)

        applicant = get_object_or_404(Application, id=applicant_id, company_in_charge=company_in_charge)
        
        if Interview.objects.filter(applicant=applicant).exists():
            return JsonResponse({
                'message': f'Interview is already scheduled for applicant ID {applicant_id}.'
            }, status=400)

        applicant_email = applicant.email  
        
        new_user_obj = new_user.objects.filter(email=applicant_email).first()
        job_seeker_obj = JobSeeker.objects.filter(email=applicant_email).first()

        if action == 'collegecue platform':
            job = applicant.job
            company_name = job.company.name if job.company else "N/A"

            Interview.objects.create(
                candidate_name=applicant.first_name,
                applicant=applicant,
                round=interview_round,
                interview_date=interview_date,
                job=job,
                company_in_charge=company_in_charge,
                user=new_user_obj if new_user_obj else None,
                job_seeker=job_seeker_obj if job_seeker_obj else None
            )

            interview_details = {
                'company_name': company_name,
                'applicant_name': f"{applicant.first_name} {applicant.last_name}",
                'job_profile': job.job_title,
                'applicant_id': applicant.id,
                'interview_date': interview_date,
            }

            return JsonResponse({
                'message': 'Interview scheduled successfully.',
                'interview_details': interview_details
            })

        return JsonResponse({
            'message': 'Applicant\'s interview will be taken outside the CollegeCue platform.'
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data.'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def get_upcoming_interviews_from_company(request, company_in_charge_id):
    if request.method != "GET":
        return JsonResponse({'error': 'Invalid request method. Please use GET.'}, status=405)
    
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return JsonResponse({'status': 'error', 'message': 'Token is missing or in an invalid format'}, status=400)

    token = auth_header.split(' ')[1]
	
    try:
        company_in_charge = CompanyInCharge.objects.get(token=token, id=company_in_charge_id)
    except CompanyInCharge.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Invalid token or company in charge not found'}, status=401)

    company_name = request.GET.get('company_name')
    if not company_name:
        return JsonResponse({'error': 'company_name parameter is required.'}, status=400)

    try:
        upcoming_interviews = Interview.objects.filter(
            job__company__name=company_name,
            company_in_charge=company_in_charge,
            interview_date__gte=timezone.now()
        ).select_related('job__company')

        interviews_list = [
            {
                'candidate_name': interview.candidate_name,
                'job_title': interview.job.job_title,
                'interview_date': interview.interview_date,
                'round': interview.round,
                'status': interview.status,
                'time_left': str(interview.time_left()) if interview.time_left() else 'Expired',
                'can_attend': interview.time_left() and interview.time_left().total_seconds() > 0,
            }
            for interview in upcoming_interviews
        ]

        return JsonResponse({'upcoming_interviews': interviews_list}, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def get_past_interviews_from_company(request, company_in_charge_id):
    if request.method != "GET":
        return JsonResponse({'error': 'Invalid request method. Please use GET.'}, status=405)

    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return JsonResponse({'status': 'error', 'message': 'Token is missing or in an invalid format'}, status=400)

    token = auth_header.split(' ')[1]

    try:
        company_in_charge = CompanyInCharge.objects.get(token=token, id=company_in_charge_id)
    except CompanyInCharge.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Invalid token or company in charge not found'}, status=401)

    company_name = request.GET.get('company_name')
    if not company_name:
        return JsonResponse({'error': 'company_name parameter is required.'}, status=400)

    try:
        past_interviews = Interview.objects.filter(
            job__company__name=company_name,
            company_in_charge=company_in_charge,
            interview_date__lt=timezone.now()
        ).select_related('job__company')

        interviews_list = [
            {
                'candidate_name': interview.candidate_name,
                'job_title': interview.job.job_title,
                'interview_date': interview.interview_date,
                'round': interview.round,
                'status': interview.status,
                'time_left': 'Expired',
                'can_attend': False,
            }
            for interview in past_interviews
        ]

        return JsonResponse({'past_interviews': interviews_list}, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def get_upcoming_interviews_by_job_title(request, job_seeker_id):
    auth_header = request.headers.get('Authorization')

    if request.method != "GET":
        return JsonResponse({'error': 'Invalid request method. Please use GET.'}, status=405)

    try:
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({'error': 'Token is missing or invalid format'}, status=400)

        token = auth_header.split(' ')[1]

        job_seeker = JobSeeker.objects.get(token=token, id=job_seeker_id)

    except JobSeeker.DoesNotExist:
        return JsonResponse({'error': 'Job Seeker not found.'}, status=404)

    job_title = request.GET.get('job_title')
    if not job_title:
        return JsonResponse({'error': 'job_title parameter is required.'}, status=400)

    try:
        upcoming_interviews = Interview.objects.filter(
            job_seeker=job_seeker,
            interview_date__gte=timezone.now(),
            job__job_title=job_title
        ).select_related('job__company')

        interviews_data = []
        for interview in upcoming_interviews:
            company_name = interview.job.company.name if interview.job.company else "N/A"
            interviews_data.append({
                'job_title': interview.job.job_title,
                'job_id': interview.job.id,
                'company_name': company_name,
                'interview_date': interview.interview_date.date(),
                'interview_time': interview.interview_date.time(),
                'time_left': str(interview.time_left()) if interview.time_left() else 'Expired',
                'can_attend': interview.time_left() and interview.time_left().total_seconds() > 0,
            })

        return JsonResponse({'upcoming_interviews': interviews_data})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def get_past_interviews_by_job_title(request, job_seeker_id):
    auth_header = request.headers.get('Authorization')

    if request.method != "GET":
        return JsonResponse({'error': 'Invalid request method. Please use GET.'}, status=405)

    try:
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({'error': 'Token is missing or invalid format'}, status=400)

        token = auth_header.split(' ')[1]
		
        job_seeker = JobSeeker.objects.get(token=token, id=job_seeker_id)

    except JobSeeker.DoesNotExist:
        return JsonResponse({'error': 'Job Seeker not found.'}, status=404)

    job_title = request.GET.get('job_title')
    if not job_title:
        return JsonResponse({'error': 'job_title parameter is required.'}, status=400)

    try:
        past_interviews = Interview.objects.filter(
            job_seeker=job_seeker,
            interview_date__lt=timezone.now(),
            job__job_title=job_title
        ).select_related('job__company')

        interviews_data = []
        for interview in past_interviews:
            company_name = interview.job.company.name if interview.job.company else "N/A"
            interviews_data.append({
                'job_title': interview.job.job_title,
                'job_id': interview.job.id,
                'company_name': company_name,
                'interview_date': interview.interview_date.date(),
                'interview_time': interview.interview_date.time(),
                'time_left': 'Expired', 
                'can_attend': False,
            })

        return JsonResponse({'past_interviews': interviews_data})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

### College to new_user and jobseeker
@csrf_exempt
def search_clg_user(request):
    if request.method != "GET":
        return JsonResponse({'status': 'false', 'message': 'Invalid request method'}, status=405)
	
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
             return JsonResponse({'error': 'Token is missing or in an invalid format'}, status=400)
        
        token = auth_header.split(' ')[1]
        sender_email = request.GET.get('sender_email')
       
        university_in_charge = UniversityInCharge.objects.get(token=token)
        
        if university_in_charge.official_email != sender_email:
            return JsonResponse({'status': 'false', 'message': 'Sender email does not match the token'}, status=403)

        query = request.GET.get('q', '').strip()

        student_contacts = new_user.objects.all().values('id', 'firstname', 'lastname', 'email')
        jobseeker_contacts = JobSeeker.objects.all().values('id', 'first_name', 'last_name', 'email')
        company_contacts = UniversityInCharge.objects.all().values('id', 'university_name', 'official_email')

        if query:
            student_contacts = student_contacts.filter(
                Q(firstname__icontains=query) |
                Q(email__icontains=query)
            )
            jobseeker_contacts = jobseeker_contacts.filter(
                Q(first_name__icontains=query) |
                Q(email__icontains=query)
            )
            company_contacts = company_contacts.filter(
                Q(university_name__icontains=query) |
                Q(official_email__icontains=query)
            )
        
        if not query:
            return JsonResponse({'status': 'success', 'contacts': []}, status=200)    

        contact_list = list(student_contacts) + list(jobseeker_contacts) + list(company_contacts)

        return JsonResponse({
            'status': 'success',
            'contacts': contact_list
        }, status=200)

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@csrf_exempt
def send_msg_clg(request):
    if request.method != "POST":
        return JsonResponse({'status': 'false', 'message': 'Invalid request method'}, status=405)

    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return JsonResponse({'error': 'Token is missing or invalid format'}, status=400)

    token = auth_header.split(' ')[1]

    sender_email = request.POST.get('sender_email')
    recipient_email = request.POST.get('recipient_email')
    message_content = request.POST.get('content')

    if not all([sender_email, recipient_email, message_content]):
        return JsonResponse({'status': 'false', 'message': 'Required fields missing'}, status=400)

    try:
        university_in_charge = UniversityInCharge.objects.get(token=token, official_email=sender_email)
        
        if university_in_charge.official_email != sender_email:
            return JsonResponse({'status': 'false', 'message': 'Sender email does not match the token'}, status=403)

        receiptent_new_user = new_user.objects.filter(email=recipient_email).first()
        receiptent_job_seeker = JobSeeker.objects.filter(email=recipient_email).first()

        if not receiptent_new_user and not receiptent_job_seeker:
            return JsonResponse({'status': 'false', 'message': 'Recipient not found'}, status=404)

        message = College_Message.objects.create(
            university_in_charge=university_in_charge,
            receiptent_new_user=receiptent_new_user if receiptent_new_user else None,
            receiptent_job_seeker=receiptent_job_seeker if receiptent_job_seeker else None,
            content=message_content
        )

        attachments = request.FILES.getlist('attachments', [])
        College_Attachment.objects.bulk_create([
            College_Attachment(message=message, file=file) for file in attachments
        ])

        email_subject = f'New Message from {sender_email}'
        email_body = (
            f'You have received a new message from {sender_email}.\n\n'
            f'Content: {message_content}\n\n'
            'You can view the message in your inbox.'
        )
        send_mail(
            email_subject,
            email_body,
            settings.EMAIL_HOST_USER,
            [recipient_email],
            fail_silently=False,
        )

        return JsonResponse({'status': 'success', 'message': 'Message sent successfully!'}, status=201)

    except UniversityInCharge.DoesNotExist:
        return JsonResponse({'status': 'false', 'message': 'Invalid token'}, status=403)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@csrf_exempt
def clg_inbox(request):

    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return JsonResponse({'status': 'error', 'message': 'Token is missing or invalid format'}, status=400)

    token = auth_header.split(' ')[1]

    try:
        university_in_charge = UniversityInCharge.objects.get(token=token)
    except UniversityInCharge.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Invalid token or university in charge not found'}, status=404)

    if request.method != "GET":
        return JsonResponse({'status': 'false', 'message': 'Invalid request method'}, status=405)

    email = request.GET.get('email')
    filter_value = request.GET.get('filter')

    if not email:
        return JsonResponse({'status': 'false', 'message': 'Email is required'}, status=400)
    
    if university_in_charge.official_email != email:
            return JsonResponse({'status': 'false', 'message': 'Sender email does not match the token'}, status=403)

    try:
        messages_query = College_Message.objects.filter(
            Q(receiptent_new_user__email=email) | Q(receiptent_job_seeker__email=email) | Q(university_in_charge__official_email=email)
        ).order_by('-timestamp')

        if filter_value in ['read', 'unread']:
            is_read = filter_value == 'read'
            messages_query = messages_query.filter(is_read=is_read)

        message_list = [
            {
                'id': message.id,
                'sender_email': message.university_in_charge.official_email,
                'recipient_email': (
                    message.receiptent_new_user.email if message.receiptent_new_user else
                    message.receiptent_job_seeker.email
                ),
                'content': message.content,
                'timestamp': message.timestamp,
                'is_read': message.is_read,
                'attachments': [
                    {
                        'id': attachment.id,
                        'file_url': attachment.file.url,
                        'uploaded_at': attachment.uploaded_at
                    } for attachment in message.attachment.all()
                ]
            }
            for message in messages_query
        ]

        return JsonResponse({'status': 'success', 'messages': message_list}, status=200)

    except Exception as e:
        return JsonResponse({'status': 'false', 'error': str(e)}, status=500)

@csrf_exempt
def get_messages_clg(request):
    if request.method != "GET":
        return JsonResponse({'status': 'false', 'message': 'Invalid request method'}, status=405)
    
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return JsonResponse({'status': 'error', 'message': 'Token is missing or invalid format'}, status=400)

    token = auth_header.split(' ')[1]
    
    sender_email = request.GET.get('sender_email')
    recipient_email = request.GET.get('recipient_email')

    if not all([sender_email, recipient_email]):
        return JsonResponse({'status': 'false', 'message': 'Required fields missing'}, status=400)

    try:
        university_in_charge = UniversityInCharge.objects.get(token=token, official_email=sender_email)
       
        if university_in_charge.official_email != sender_email:
            return JsonResponse({'status': 'false', 'message': 'Sender email does not match the token'}, status=403)

        receipent_new_user = new_user.objects.filter(email=recipient_email).first()
        receipent_job_seeker = JobSeeker.objects.filter(email=recipient_email).first()

        if not receipent_new_user and not receipent_job_seeker:
            return JsonResponse({'status': 'false', 'message': 'Recipient not found'}, status=404)

        all_messages = College_Message.objects.filter(
            receiptent_new_user=receipent_new_user,
            receiptent_job_seeker=receipent_job_seeker,
            university_in_charge=university_in_charge
        ).prefetch_related('attachment')

        if not all_messages.exists():
            return JsonResponse({'status': 'false', 'message': 'No messages found'}, status=404)

        all_messages.filter(is_read=False).update(is_read=True)

        messages_data = []
        for message in all_messages:
            attachments = message.attachment.all()
            attachments_data = [
                {
                    'file_url': attachment.file.url,
                    'uploaded_at': attachment.uploaded_at
                }
                for attachment in attachments
            ]

            messages_data.append({
                'message_id': message.id,
                'sender_email': message.university_in_charge.official_email,
                'recipient_email': (
                    message.receiptent_new_user.email if message.receiptent_new_user else
                    message.receiptent_job_seeker.email
                ),
                'content': message.content,
                'timestamp': message.timestamp,
                'is_read': message.is_read,
                'attachments': attachments_data
            })

        return JsonResponse({'status': 'success', 'messages': messages_data}, status=200)

    except UniversityInCharge.DoesNotExist:
        return JsonResponse({'status': 'false', 'message': 'Invalid token or sender email'}, status=403)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

### new_user to college and company
@csrf_exempt
def search_company_college_user(request):
    auth_header = request.headers.get('Authorization')

    if request.method != "GET":
        return JsonResponse({'status': 'false', 'message': 'Invalid request method'}, status=405)

    try:
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({'status': 'false', 'message': 'Token is missing or invalid format'}, status=400)

        token = auth_header.split(' ')[1]
        sender_email = request.GET.get('sender_email')

        sender = new_user.objects.get(token=token)
        
        if sender.email != sender_email:
            return JsonResponse({'status': 'false', 'message': 'Sender email does not match the token'}, status=403)

        query = request.GET.get('q', '').strip()

        if not query:
            return JsonResponse({'status': 'success', 'contacts': []}, status=200)

        user_contacts = new_user.objects.filter(
            Q(firstname__icontains=query) | Q(email__icontains=query)
        ).values('id', 'firstname', 'email')

        company_contacts = CompanyInCharge.objects.filter(
            Q(company_name__icontains=query) | Q(official_email__icontains=query)
        ).values('id', 'company_name', 'official_email')

        college_contacts = UniversityInCharge.objects.filter(
            Q(university_name__icontains=query) | Q(official_email__icontains=query)
        ).values('id', 'university_name', 'official_email')

        contact_list = list(user_contacts) + list(company_contacts) + list(college_contacts)

        return JsonResponse({
            'status': 'success',
            'contacts': contact_list
        }, status=200)

    except new_user.DoesNotExist:
        return JsonResponse({'status': 'false', 'message': 'Invalid token or user not found'}, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@csrf_exempt
def send_msg_clg_comp(request):
    auth_header = request.headers.get('Authorization')

    if request.method != "POST":
        return JsonResponse({'status': 'false', 'message': 'Invalid request method'}, status=405)

    sender_email = request.POST.get('sender_email')
    recipient_email = request.POST.get('recipient_email')
    message_content = request.POST.get('content')

    if not all([sender_email, recipient_email, message_content]):
        return JsonResponse({'status': 'false', 'message': 'Required fields missing'}, status=400)

    try:
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({'status': 'false', 'message': 'Token is missing or invalid format'}, status=400)

        token = auth_header.split(' ')[1]

        sender = new_user.objects.get(token=token, email=sender_email)
        if sender.email != sender_email:
            return JsonResponse({'status': 'false', 'message': 'Sender email does not match the token'}, status=403)

        recipient_company = CompanyInCharge.objects.filter(official_email=recipient_email).first()
        recipient_college = UniversityInCharge.objects.filter(official_email=recipient_email).first()

        if recipient_company:
            message = Message.objects.create(
                receiptent_new_user=sender,
                company_in_charge=recipient_company,
                content=message_content
            )

            attachments = request.FILES.getlist('attachments', [])
            if attachments:
                Attachment.objects.bulk_create([
                    Attachment(message=message, file=file) for file in attachments
                ])

        elif recipient_college:
            message = College_Message.objects.create(
                receiptent_new_user=sender,
                university_in_charge=recipient_college,
                content=message_content
            )

            attachments = request.FILES.getlist('attachments', [])
            if attachments:
                College_Attachment.objects.bulk_create([
                    College_Attachment(message=message, file=file) for file in attachments
                ])

        else:
            return JsonResponse({'status': 'false', 'message': 'Recipient not found'}, status=404)

        email_subject = f'New Message from {sender.email}'
        email_body = (
            f'You have received a new message from {sender.email}.\n\n'
            f'Content: {message_content}\n\n'
            'You can view the message in your inbox.'
        )
        send_mail(
            email_subject,
            email_body,
            settings.EMAIL_HOST_USER,
            [recipient_email],
            fail_silently=False,
        )

        return JsonResponse({'status': 'success', 'message': 'Message sent successfully!'}, status=201)

    except new_user.DoesNotExist:
        return JsonResponse({'status': 'false', 'message': 'Invalid token or user not found'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@csrf_exempt
def get_clg_comp_messages(request):
    auth_header = request.headers.get('Authorization')

    if request.method != "GET":
        return JsonResponse({'status': 'false', 'message': 'Invalid request method'}, status=405)

    try:
        sender_email = request.GET.get('sender_email')
        recipient_email = request.GET.get('recipient_email')

        if not all([sender_email, recipient_email]):
            return JsonResponse({'status': 'false', 'message': 'Required fields missing'}, status=400)

        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({'status': 'false', 'message': 'Token is missing or invalid format'}, status=400)

        token = auth_header.split(' ')[1]

        sender = new_user.objects.get(token=token)

        if sender.email != sender_email:
            return JsonResponse({'status': 'false', 'message': 'Sender email does not match the token'}, status=403)

        company_recipient = CompanyInCharge.objects.filter(official_email=recipient_email).first()
        college_recipient = UniversityInCharge.objects.filter(official_email=recipient_email).first()

        if company_recipient:
            all_messages = Message.objects.filter(
                receiptent_new_user=sender,
                company_in_charge=company_recipient
            ).prefetch_related('attachments')

        elif college_recipient:
            all_messages = College_Message.objects.filter(
                receiptent_new_user=sender,
                university_in_charge=college_recipient
            ).prefetch_related('attachment')

        else:
            return JsonResponse({'status': 'false', 'message': 'Recipient not found'}, status=404)

        if not all_messages.exists():
            return JsonResponse({'status': 'false', 'message': 'No messages found'}, status=404)

        all_messages.filter(is_read=False).update(is_read=True)

        messages_data = [
            {
                'message_id': message.id,
                'sender_email': message.receiptent_new_user.email,
                'recipient_email': company_recipient.official_email if company_recipient else college_recipient.official_email,
                'content': message.content,
                'timestamp': message.timestamp,
                'is_read': message.is_read,
                'attachments': [
                    {
                        'file_url': attachment.file.url,
                        'uploaded_at': attachment.uploaded_at
                    }
                    for attachment in (message.attachments.all() if company_recipient else message.attachment.all())
                ]
            }
            for message in all_messages
        ]

        return JsonResponse({'status': 'success', 'messages': messages_data}, status=200)

    except new_user.DoesNotExist:
        return JsonResponse({'status': 'false', 'message': 'Invalid token or user not found'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
@csrf_exempt
def clg_comp_inbox(request):
    auth_header = request.headers.get('Authorization')

    if request.method != "GET":
        return JsonResponse({'status': 'false', 'message': 'Invalid request method'}, status=405)

    email = request.GET.get('email')
    filter_value = request.GET.get('filter')

    if not email:
        return JsonResponse({'status': 'false', 'message': 'Email is required'}, status=400)

    if not auth_header or not auth_header.startswith('Bearer '):
        return JsonResponse({'status': 'false', 'message': 'Token is missing or invalid format'}, status=400)

    token = auth_header.split(' ')[1]

    try:
        sender = new_user.objects.get(token=token)

        if sender.email != email:
            return JsonResponse({'status': 'false', 'message': 'Sender email does not match the token'}, status=403)

        company_messages_query = Message.objects.filter(
            Q(receiptent_new_user__email=email) | Q(company_in_charge__official_email=email)
        )

        college_messages_query = College_Message.objects.filter(
            Q(receiptent_new_user__email=email) | Q(university_in_charge__official_email=email)
        )

        if filter_value in ['read', 'unread']:
            is_read = filter_value == 'read'
            company_messages_query = company_messages_query.filter(is_read=is_read)
            college_messages_query = college_messages_query.filter(is_read=is_read)

        messages_list = []

        for message in company_messages_query.order_by('-timestamp'):
            messages_list.append({
                'id': message.id,
                'sender': message.receiptent_new_user.email,
                'recipient': message.company_in_charge.official_email,
                'content': message.content,
                'timestamp': message.timestamp,
                'is_read': message.is_read,
                'attachments': [
                    {
                        'id': attachment.id,
                        'file_url': attachment.file.url,
                        'uploaded_at': attachment.uploaded_at
                    } for attachment in message.attachments.all()
                ]
            })

        for message in college_messages_query.order_by('-timestamp'):
            messages_list.append({
                'id': message.id,
                'sender': message.receiptent_new_user.email,
                'recipient': message.university_in_charge.official_email,
                'content': message.content,
                'timestamp': message.timestamp,
                'is_read': message.is_read,
                'attachments': [
                    {
                        'id': attachment.id,
                        'file_url': attachment.file.url,
                        'uploaded_at': attachment.uploaded_at
                    } for attachment in message.attachment.all()
                ]
            })

        messages_list.sort(key=lambda x: x['timestamp'], reverse=True)

        return JsonResponse({'status': 'success', 'messages': messages_list}, status=200)

    except new_user.DoesNotExist:
        return JsonResponse({'status': 'false', 'message': 'Invalid token or user not found'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'false', 'error': str(e)}, status=500)


def fetch_colleges_jobs(request):
    if request.method == 'GET':
        try:
            jobs = Job1.objects.all()
            jobs_list = list(jobs.values())
            return JsonResponse({'colleges_jobs': jobs_list})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method.'}, status=400)

def fetch_colleges(request):
    if request.method == 'GET':
        try:
            colleges = College.objects.all()
            college_list = list(colleges.values())
            return JsonResponse({'colleges_jobs': college_list})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method.'}, status=400)

@csrf_exempt
def create_jobseeker_resume(request, jobseeker_id):
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return JsonResponse({'status': 'error', 'message': 'Token is missing or invalid format'}, status=400)

    token = auth_header.split(' ')[1]

    try:
        jobseeker = JobSeeker.objects.get(id=jobseeker_id,token=token)
    except JobSeeker.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Invalid token or job seeker not found'}, status=401)

    if request.method == 'POST':
        try:
            with transaction.atomic():
                jobseeker = get_object_or_404(JobSeeker, id=jobseeker_id)

                jobseeker_email = request.POST.get('email')
                if not jobseeker:
                    return JsonResponse({'status': 'error', 'message': 'Email is required'}, status=400)
                
                if jobseeker_email != jobseeker.email:
                    return JsonResponse({'status': 'error', 'message': 'Email does not match the email of the jobseeker'}, status=400)

                resume = JobSeeker_Resume.objects.filter(email=jobseeker_email, job_seeker=jobseeker).first()

                if resume:
                    resume_form = JobseekerResumeForm(request.POST, request.FILES, instance=resume)
                else:
                    resume_form = JobseekerResumeForm(request.POST, request.FILES)

                print("Resume Form Validity:", resume_form.is_valid())

                if resume_form.is_valid():
                    resume = resume_form.save(commit=False) 
                    resume.job_seeker = jobseeker
                    print("Resume before save:", resume) 
                     
                    delete_attachment = resume_form.cleaned_data.get('delete', False)
                    new_attachment = resume_form.cleaned_data.get('Attachment')

                    if new_attachment and resume and resume.Attachment:
                        if os.path.exists(resume.Attachment.path):
                            print("Deleting old attachment:", resume.Attachment.path)
                            os.remove(resume.Attachment.path)
                             
                    resume.save()

                    if delete_attachment and resume.Attachment and os.path.exists(resume.Attachment.path):
                        print("Attachment Path for Deletion:", resume.Attachment.path)
                        os.remove(resume.Attachment.path)
                        resume.Attachment = None
                        resume.save()
                        return JsonResponse({'status': 'success', 'message': 'Attachment deleted successfully', 'resume_id': resume.id})

                objective_data = request.POST.get('objective', '{}')
                if objective_data:
                    objective_data = json.loads(objective_data)
                    objective_instance = resume.objective if hasattr(resume, 'objective') else None

                    if objective_instance:
                        objective_form = JobseekerObjectiveForm(objective_data, instance=objective_instance)
                    else:
                        objective_form = JobseekerObjectiveForm(objective_data)

                    if objective_form.is_valid():
                        objective = objective_form.save(commit=False)
                        objective.resume = resume
                        objective.job_seeker = jobseeker
                        objective.save()

                def save_related_data(form_class, data_list, related_name, existing_items):
                    existing_items.delete()
                    
                    for item in data_list:
                        form = form_class(item)
                        if form.is_valid():
                            obj = form.save(commit=False)
                            obj.resume = resume
                            obj.job_seeker = jobseeker
                            obj.save()
                        else:
                            print(f"{related_name} Form Errors:", form.errors)

                save_related_data(JobseekerEducationForm, json.loads(request.POST.get('education', '[]')), 'Education', resume.education_entries.all())
                save_related_data(JobseekerExperienceForm, json.loads(request.POST.get('experience', '[]')), 'Experience', resume.experience_entries.all())
                save_related_data(JobseekerProjectForm, json.loads(request.POST.get('projects', '[]')), 'Projects', resume.projects.all())
                save_related_data(JobseekerReferenceForm, json.loads(request.POST.get('references', '[]')), 'References', resume.references.all())
                save_related_data(JobseekerCertificationForm, json.loads(request.POST.get('certifications', '[]')), 'Certifications', resume.certifications.all())
                save_related_data(JobseekerAchievementForm, json.loads(request.POST.get('achievements', '[]')), 'Achievements', resume.achievements.all())
                save_related_data(JobseekerPublicationForm, json.loads(request.POST.get('publications', '[]')), 'Publications', resume.publications.all())

                return JsonResponse({
                    'status': 'success',
                    'message': 'Resume created/updated successfully',
                    'resume_id': resume.id
                })

            print("Form Errors:", resume_form.errors)
            return JsonResponse({'status': 'error', 'errors': resume_form.errors}, status=400)

        except json.JSONDecodeError as e:
            print("JSONDecodeError:", str(e))
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON data'}, status=400)

        except IntegrityError as e:
            print("IntegrityError:", str(e))
            return JsonResponse({'status': 'error', 'message': 'Database integrity error', 'details': str(e)}, status=500)

        except OperationalError as e:
            print("OperationalError:", str(e))
            return JsonResponse({'status': 'error', 'message': 'Database operational error', 'details': str(e)}, status=500)

        except Exception as e:
            print("General Exception:", str(e))
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)
    
def get_jobseeker_resume_detail_by_id(request, jobseeker_id, resume_id):
    auth_header = request.headers.get('Authorization')
    
    try:
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({'status': 'error', 'message': 'Token is missing or invalid format'}, status=400)

        token = auth_header.split(' ')[1]

        jobseeker = JobSeeker.objects.get(id=jobseeker_id,token=token)

        if request.method == 'GET':
            resume = get_object_or_404(JobSeeker_Resume,job_seeker=jobseeker ,id=resume_id)

            resume_data = {
                "first_name": resume.first_name, 
                "last_name": resume.last_name,
                "email": resume.email,
                "phone": resume.phone,
                "address": resume.address,
                "date_of_birth": resume.date_of_birth,
                "website_urls": resume.website_urls,
                "skills": resume.skills,
                "activities": resume.activities,
                "interests": resume.interests,
                "languages": resume.languages,
                "bio": resume.bio,
                "city": resume.city,
                "state": resume.state,
                "country": resume.country,
                "zipcode": resume.zipcode,
                # "attachments": resume.Attachment,
                "objective": resume.objective.text if hasattr(resume, 'objective') else 'Not specified',
                "education": [
                    {
                        "course_or_degree": education.course_or_degree,
                        "school_or_university": education.school_or_university,
                        "grade_or_cgpa": education.grade_or_cgpa,
                        "start_date": education.start_date,
                        "end_date": education.end_date,
                        "description": education.description
                    } for education in resume.education_entries.all()
                ],
                "experience": [
                    {
                        "job_title": experience.job_title,
                        "company_name": experience.company_name,
                        "start_date": experience.start_date,
                        "end_date": experience.end_date,
                        "description": experience.description,
                    } for experience in resume.experience_entries.all()
                ],
                "projects": [
                    {
                        "title": project.title,
                        "description": project.description,
                        "project_link": project.project_link
                    } for project in resume.projects.all()
                ],
                "references": [
                    {
                        "name": reference.name,
                        "contact_info": reference.contact_info,
                        "relationship": reference.relationship,
                    } for reference in resume.references.all()
                ],
                "certifications": [
                    {
                        "name": certification.name,
                        "start_date": certification.start_date,
                        "end_date": certification.end_date,
                    } for certification in resume.certifications.all()
                ],
                "achievements": [
                    {
                        "title": achievement.title,
                        "publisher": achievement.publisher,
                        "start_date": achievement.start_date,
                        "end_date": achievement.end_date,
                    } for achievement in resume.achievements.all()
                ],
                "publications": [
                    {
                        "title": publication.title,
                        "start_date": publication.start_date,
                        "end_date": publication.end_date,
                    } for publication in resume.publications.all()
                ]
            }

            return JsonResponse(resume_data, status=200)
        else:
            return JsonResponse({"error": "Method not allowed"}, status=405)
    except JobSeeker.DoesNotExist:
        return JsonResponse({"error": "Invalid token or job seeker not found"}, status=401)
    except ObjectDoesNotExist:
        return JsonResponse({"error": "Resume not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)      
    
@csrf_exempt
def college_status(request, status_choice, university_in_charge_id):
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return JsonResponse({'status': 'error', 'message': 'Token is missing or invalid format'}, status=400)

    token = auth_header.split(' ')[1]

    try:
        university_in_charge = UniversityInCharge.objects.get(id=university_in_charge_id, token=token)
    except UniversityInCharge.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Invalid token or university in charge not found'}, status=404)

    try:
        college_id = request.GET['college_id']
        print(college_id)

        college = get_object_or_404(College, id=college_id, university_in_charge=university_in_charge)
        print(college)

        job_id = Job1.objects.filter(college=college)
        apply_id = Application1.objects.filter(job__in=job_id)

        name = []
        if status_choice == 'selected':
            candidate_status_modelname = Candidate1Status_selected
        elif status_choice == 'rejected':
            candidate_status_modelname = Candidate1Status_rejected
        elif status_choice == 'not_eligible':
            candidate_status_modelname = Candidate1Status_not_eligible
        elif status_choice == 'under_review':
            candidate_status_modelname = Candidate1Status_under_review

        for application in apply_id:
            if application.status == status_choice:
                name.append(application.first_name)
                candidate_status_modelname.objects.create(
                    first_name=application.first_name,
                    status=status_choice,
                    college_id=college_id,
                    job_id=application.job_id, 
                )

        return JsonResponse({'message': name}, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

### JobSeeker to Company and College
@csrf_exempt
def search_company_college_jobseeker(request):
    auth_header = request.headers.get('Authorization')

    if request.method != "GET":
        return JsonResponse({'status': 'false', 'message': 'Invalid request method'}, status=405)

    try:
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({'status': 'error', 'message': 'Token is missing or invalid format'}, status=400)

        token = auth_header.split(' ')[1]
        sender_email = request.GET.get('sender_email')
		
        jobseeker = JobSeeker.objects.get(token=token)
        
        if jobseeker.email != sender_email:
            return JsonResponse({'status': 'false', 'message': 'Sender email does not match the token'}, status=403)
        
        query = request.GET.get('q', '').strip()

        if not query:
          return JsonResponse({'status': 'success', 'contacts': []}, status=200)

        user_contacts = JobSeeker.objects.filter(
            Q(first_name__icontains=query) | Q(email__icontains=query)
        ).values('id', 'first_name', 'email')

        company_contacts = CompanyInCharge.objects.filter(
            Q(company_name__icontains=query) | Q(official_email__icontains=query)
        ).values('id', 'company_name', 'official_email')

        college_contacts = UniversityInCharge.objects.filter(
            Q(university_name__icontains=query) | Q(official_email__icontains=query)
        ).values('id', 'university_name', 'official_email')

        contact_list = list(user_contacts) + list(company_contacts) + list(college_contacts)

        return JsonResponse({
            'status': 'success',
            'contacts': contact_list
        }, status=200)

    except JobSeeker.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Invalid token or job seeker not found'}, status=401)

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@csrf_exempt
def send_msg_clg_comp_jobseeker(request):
    auth_header = request.headers.get('Authorization')

    if request.method != "POST":
        return JsonResponse({'status': 'false', 'message': 'Invalid request method'}, status=405)

    sender_email = request.POST.get('sender_email')
    recipient_email = request.POST.get('recipient_email')
    message_content = request.POST.get('content')

    if not all([sender_email, recipient_email, message_content]):
        return JsonResponse({'status': 'false', 'message': 'Required fields missing'}, status=400)

    try:
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({'status': 'error', 'message': 'Token is missing or invalid format'}, status=400)

        token = auth_header.split(' ')[1]

        jobseeker = JobSeeker.objects.get(token=token,email=sender_email)

        if jobseeker.email != sender_email:
            return JsonResponse({'status': 'false', 'message': 'Sender email does not match the token'}, status=403)

        recipient_company = CompanyInCharge.objects.filter(official_email=recipient_email).first()
        recipient_college = UniversityInCharge.objects.filter(official_email=recipient_email).first()

        if recipient_company:
            message = Message.objects.create(
                receiptent_job_seeker=jobseeker,
                company_in_charge=recipient_company,
                content=message_content
            )

            attachments = request.FILES.getlist('attachments', [])
            if attachments:
                Attachment.objects.bulk_create([
                    Attachment(message=message, file=file) for file in attachments
                ])

        elif recipient_college:
            message = College_Message.objects.create(
                receiptent_job_seeker=jobseeker,
                university_in_charge=recipient_college,
                content=message_content
            )

            attachments = request.FILES.getlist('attachments', [])
            if attachments:
                College_Attachment.objects.bulk_create([
                    College_Attachment(message=message, file=file) for file in attachments
                ])

        else:
            return JsonResponse({'status': 'false', 'message': 'Recipient not found'}, status=404)

        email_subject = f'New Message from {jobseeker.email}'
        email_body = (
            f'You have received a new message from {jobseeker.email}.\n\n'
            f'Content: {message_content}\n\n'
            'You can view the message in your inbox.'
        )
        send_mail(
            email_subject,
            email_body,
            settings.EMAIL_HOST_USER,
            [recipient_email],
            fail_silently=False,
        )

        return JsonResponse({'status': 'success', 'message': 'Message sent successfully!'}, status=201)

    except JobSeeker.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Invalid token or job seeker not found'}, status=401)

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@csrf_exempt
def get_clg_comp_jobseeker_messages(request):
    if request.method != "GET":
        return JsonResponse({'status': 'false', 'message': 'Invalid request method'}, status=405)

    try:
        sender_email = request.GET.get('sender_email')
        recipient_email = request.GET.get('recipient_email')
        
        if not all([sender_email, recipient_email]):
            return JsonResponse({'status': 'false', 'message': 'Required fields missing'}, status=400)
        
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({'status': 'error', 'message': 'Token is missing or invalid format'}, status=400)

        token = auth_header.split(' ')[1]

        jobseeker = JobSeeker.objects.get(token=token)

        if  jobseeker.email != sender_email:
            return JsonResponse({'status': 'false', 'message': 'Sender email does not match the token'}, status=403)

        company_recipient = CompanyInCharge.objects.filter(official_email=recipient_email).first()
        college_recipient = UniversityInCharge.objects.filter(official_email=recipient_email).first()

        if company_recipient:
            all_messages = Message.objects.filter(
                receiptent_job_seeker= jobseeker,
                company_in_charge=company_recipient
            ).prefetch_related('attachments')

        elif college_recipient:
            all_messages = College_Message.objects.filter(
                receiptent_job_seeker= jobseeker,
                university_in_charge=college_recipient
            ).prefetch_related('attachment')

        else:
            return JsonResponse({'status': 'false', 'message': 'Recipient not found'}, status=404)

        if not all_messages.exists():
            return JsonResponse({'status': 'false', 'message': 'No messages found'}, status=404)

        all_messages.filter(is_read=False).update(is_read=True)

        messages_data = [
            {
                'message_id': message.id,
                'sender_email': message.receiptent_job_seeker.email,
                'recipient_email': company_recipient.official_email if company_recipient else college_recipient.official_email,
                'content': message.content,
                'timestamp': message.timestamp,
                'is_read': message.is_read,
                'attachments': [
                    {
                        'file_url': attachment.file.url,
                        'uploaded_at': attachment.uploaded_at
                    }
                    for attachment in (message.attachments.all() if company_recipient else message.attachment.all())
                ]
            }
            for message in all_messages
        ]

        return JsonResponse({'status': 'success', 'messages': messages_data}, status=200)

    except JobSeeker.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Invalid token or job seeker not found'}, status=401)

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@csrf_exempt
def clg_comp_jobseeker_inbox(request):
    auth_header = request.headers.get('Authorization')

    if request.method != "GET":
        return JsonResponse({'status': 'false', 'message': 'Invalid request method'}, status=405)

    email = request.GET.get('email')
    filter_value = request.GET.get('filter')

    if not email:
        return JsonResponse({'status': 'false', 'message': 'Email is required'}, status=400)

    try:
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({'status': 'error', 'message': 'Token is missing or invalid format'}, status=400)

        token = auth_header.split(' ')[1]

        sender = JobSeeker.objects.get(token=token)

        if sender.email != email:
            return JsonResponse({'status': 'false', 'message': 'Email does not match the authenticated user'}, status=403)

        company_messages_query = Message.objects.filter(
            Q(receiptent_job_seeker__email=email) | Q(company_in_charge__official_email=email)
        )

        college_messages_query = College_Message.objects.filter(
            Q(receiptent_job_seeker__email=email) | Q(university_in_charge__official_email=email)
        )

        if filter_value in ['read', 'unread']:
            is_read = filter_value == 'read'
            company_messages_query = company_messages_query.filter(is_read=is_read)
            college_messages_query = college_messages_query.filter(is_read=is_read)

        messages_list = []

        for message in company_messages_query.order_by('-timestamp'):
            messages_list.append({
                'id': message.id,
                'sender': message.receiptent_job_seeker.email,
                'recipient': message.company_in_charge.official_email,
                'content': message.content,
                'timestamp': message.timestamp,
                'is_read': message.is_read,
                'attachments': [
                    {
                        'id': attachment.id,
                        'file_url': attachment.file.url,
                        'uploaded_at': attachment.uploaded_at
                    } for attachment in message.attachments.all()
                ]
            })

        for message in college_messages_query.order_by('-timestamp'):
            messages_list.append({
                'id': message.id,
                'sender': message.receiptent_job_seeker.email,
                'recipient': message.university_in_charge.official_email,
                'content': message.content,
                'timestamp': message.timestamp,
                'is_read': message.is_read,
                'attachments': [
                    {
                        'id': attachment.id,
                        'file_url': attachment.file.url,
                        'uploaded_at': attachment.uploaded_at
                    } for attachment in message.attachment.all()
                ]
            })

        messages_list.sort(key=lambda x: x['timestamp'], reverse=True)

        return JsonResponse({'status': 'success', 'messages': messages_list}, status=200)

    except JobSeeker.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Invalid token or job seeker not found'}, status=401)

    except Exception as e:
        return JsonResponse({'status': 'false', 'error': str(e)}, status=500)

@csrf_exempt
def save_screening_questions_and_answers_for_college(request, university_incharge_id):

    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return JsonResponse({'error': 'Token is missing or invalid format'}, status=400)

    token = auth_header.split(' ')[1]

    try:
        university_in_charge = UniversityInCharge.objects.get(token=token)
    except UniversityInCharge.DoesNotExist:
        return JsonResponse({'error': 'Invalid token or university in charge not found'}, status=401)

    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))

            job_id = data.get('job_id')
            questions_and_answers = data.get('questions_and_answers')

            if not job_id:
                return JsonResponse({'status': 'error', 'message': 'Job ID is missing'}, status=400)

            if not questions_and_answers:
                return JsonResponse({'status': 'error', 'message': 'Questions and answers are missing'}, status=400)

            try:
                university_in_charge = UniversityInCharge.objects.get(id=university_incharge_id)
            except UniversityInCharge.DoesNotExist:
                return JsonResponse({'error': f'University in charge with ID "{university_incharge_id}" does not exist'}, status=404)

            job = Job1.objects.get(id=job_id, university_in_charge=university_in_charge)

            for qa in questions_and_answers:
                question_text = qa.get('question')
                correct_answer = qa.get('correct_answer')

                CollegeScreeningQuestion.objects.create(
                    job=job,
                    question_text=question_text,
                    correct_answer=correct_answer,
                    university_in_charge=university_in_charge
                )

            return JsonResponse({'status': 'success', 'message': 'Questions and answers saved successfully'}, status=201)
        except Job1.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Job not found'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

@csrf_exempt
def submit_application_with_screening_for_college(request, job_id, university_incharge_id):

    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return JsonResponse({'error': 'Token is missing or invalid format'}, status=400)

    token = auth_header.split(' ')[1]

    try:
        university_in_charge = UniversityInCharge.objects.get(token=token)
    except UniversityInCharge.DoesNotExist:
        return JsonResponse({'error': 'Invalid token or university in charge not found'}, status=401)

    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        job = Job1.objects.get(id=job_id)  
        print(job)
    except Job1.DoesNotExist:
        return JsonResponse({"error": "Job not found"}, status=404)

    try:
        university_incharge = UniversityInCharge.objects.get(id=university_incharge_id)
    except UniversityInCharge.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'University in charge not found'}, status=404)

    try:
        data = json.loads(request.body)

        email = data.get('email')
        skills = data.get('skills')
        must_have_qualification = data.get('must_have_qualification', False)
        answers = data.get('answers')

        if not email or not answers:
            return JsonResponse({"error": "Email or answers are missing"}, status=400)

        newuser = new_user.objects.filter(email=email).first()
        jobseeker = JobSeeker.objects.filter(email=email).first()
        
        if not newuser and not jobseeker:
            return JsonResponse({"error": "No registration found for NewUser and JobSeeker with this email"}, status=400)

        first_question_id = answers[0].get('question_id')
        if not first_question_id:
            return JsonResponse({"error": "First question ID is missing"}, status=400)

        first_question = CollegeScreeningQuestion.objects.filter(id=first_question_id).first()
        if not first_question:
            return JsonResponse({"error": f"Invalid question_id: {first_question_id}"}, status=400)

        if Application1.objects.filter(job=job, user=newuser, job_seeker=jobseeker, university_in_charge=university_incharge).exists():
            return JsonResponse({"error": f"User or JobSeeker with email {email} has already submitted an application for this job."}, status=400)

        application = Application1.objects.create(
            job=job,
            email=email,
            skills=skills,
            status="pending",
            user=newuser,
            job_seeker=jobseeker,
            university_in_charge=university_incharge,
            first_name=newuser.firstname if newuser else jobseeker.first_name,
            last_name=newuser.lastname if newuser else jobseeker.last_name
        )

        correct_answers = {question.id: question.correct_answer for question in CollegeScreeningQuestion.objects.filter(job=job)}
        all_answers_correct = True

        for answer_data in answers:
            question_id = answer_data.get('question_id')
            answer_text = answer_data.get('answer')

            if not question_id or not answer_text:
                return JsonResponse({"error": "Question ID or answer is missing"}, status=400)

            question = CollegeScreeningQuestion.objects.filter(id=question_id, job=job).first()
            if not question:
                return JsonResponse({"error": f"Invalid question_id: {question_id}"}, status=400)

            is_correct = (correct_answers.get(question.id) == answer_text)

            CollegeScreeningAnswer.objects.create(
                application=application,
                question=question,
                answer_text=answer_text,
                university_in_charge=university_incharge
            )

            if not is_correct:
                all_answers_correct = False

        if all_answers_correct and must_have_qualification:
            application.status = 'selected'
            application.save()

            email_subject = "Job Application Status"
            email_body = f"Dear Applicant,\n\nYour application for the job {job.job_title} has been accepted."
            send_mail(
                email_subject,
                email_body,
                settings.EMAIL_HOST_USER,
                [application.email],
                fail_silently=False,
            )
            return JsonResponse({"message": "Application submitted successfully and applicant selected."}, status=201)

        elif must_have_qualification and not all_answers_correct:
            application.status = 'rejected'
            application.save()

            email_subject = "Job Application Status"
            email_body = f"Dear Applicant,\n\nUnfortunately, your application for the job {job.job_title} has been rejected."
            send_mail(
                email_subject,
                email_body,
                settings.EMAIL_HOST_USER,
                [application.email],
                fail_silently=False,
            )
            return JsonResponse({"message": "Application submitted successfully and applicant rejected."}, status=201)

        elif not must_have_qualification and all_answers_correct:
            application.status = 'pending'
            application.save()

            return JsonResponse({"message": "Applicant moves to the above list."}, status=201)

        elif not must_have_qualification and not all_answers_correct:
            application.status = 'pending'
            application.save()

            return JsonResponse({"message": "Applicant moves to the below list."}, status=201)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)

def jobseeker_application_status_counts(request, jobseeker_id):
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return JsonResponse({'error': 'Token is missing or invalid format'}, status=400)

    token = auth_header.split(' ')[1]

    try:
        jobseeker = JobSeeker.objects.get(id=jobseeker_id,token=token)
    except JobSeeker.DoesNotExist:
        return JsonResponse({'error': 'Invalid token or job seeker not found'}, status=401)

    try:
        email = request.GET.get('email')
        if not email:
            return JsonResponse({'error': 'Email parameter is required'}, status=400)

        jobseeker = JobSeeker.objects.get(id=jobseeker_id, email=email)

        total_jobs_applied_count = (
            Application.objects.filter(job_seeker=jobseeker).count() +
            Application1.objects.filter(job_seeker=jobseeker).count()
        )
        
        pending_count = (
            Application.objects.filter(job_seeker=jobseeker, status='pending').count() +
            Application1.objects.filter(job_seeker=jobseeker, status='pending').count()
        )
        
        interview_scheduled_count = (
            Application.objects.filter(job_seeker=jobseeker, status='interview_scheduled').count() +
            Application1.objects.filter(job_seeker=jobseeker, status='interview_scheduled').count()
        )
        
        rejected_count = (
            Application.objects.filter(job_seeker=jobseeker, status='rejected').count() +
            Application1.objects.filter(job_seeker=jobseeker, status='rejected').count()
        )

        return JsonResponse({
            'total_jobs_applied': total_jobs_applied_count,
            'pending_count': pending_count,
            'interview_scheduled_count': interview_scheduled_count,
            'rejected_count': rejected_count,
        })

    except JobSeeker.DoesNotExist:
        return JsonResponse({'error': 'Job seeker not found with the provided email.'}, status=404)
    except Exception as e:
        return JsonResponse({'error': 'An error occurred', 'details': str(e)}, status=500)
    
def filterjobseeker__applied_jobs(request, jobseeker_id):
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return JsonResponse({'error': 'Token is missing or invalid format'}, status=400)

    token = auth_header.split(' ')[1]

    try:
        jobseeker = JobSeeker.objects.get(id=jobseeker_id,token=token)
    except JobSeeker.DoesNotExist:
        return JsonResponse({'error': 'Invalid token or job seeker not found'}, status=401)

    try:
        email = request.GET.get('email')
        if not email:
            return JsonResponse({'error': 'Email parameter is required'}, status=400)
        
        jobseeker = JobSeeker.objects.get(id=jobseeker_id, email=email)
        if not jobseeker:
            return JsonResponse({"error": "JobSeeker not found"}, status=400)

        job_title = request.GET.get('job_title')
        status = request.GET.get('status')
        job_type = request.GET.get('job_type')
        sort_by = request.GET.get('sort_by')

        applications_1 = Application.objects.filter(job_seeker=jobseeker)
        applications_2 = Application1.objects.filter(job_seeker=jobseeker)

        if job_title:
            applications_1 = applications_1.filter(job__job_title=job_title)
            applications_2 = applications_2.filter(job__job_title=job_title)

        if status:
            applications_1 = applications_1.filter(status=status)
            applications_2 = applications_2.filter(status=status)

        if job_type:
            applications_1 = applications_1.filter(job__job_type=job_type)
            applications_2 = applications_2.filter(job__job_type=job_type)

        applications = list(chain(applications_1, applications_2))

        if sort_by == 'job_title_asc':
            applications.sort(key=lambda x: x.job.job_title)
        elif sort_by == 'job_title_desc':
            applications.sort(key=lambda x: x.job.job_title, reverse=True)
        elif sort_by == 'applied_at_asc':
            applications.sort(key=lambda x: x.applied_at)
        elif sort_by == 'applied_at_desc':
            applications.sort(key=lambda x: x.applied_at, reverse=True)

        result = []
        for application in applications:
            job = application.job
            if isinstance(job, Job1):
                result.append({
                    'job_title': job.job_title,
                    'university_in_charge': job.university_in_charge.university_name,
                    'job_location': job.location,
                    'job_type': job.job_type,
                    'status': application.status,
                    'applied_at': application.applied_at,
                })
            else:
                result.append({
                    'job_title': job.job_title,
                    'company': job.company.name,
                    'job_location': job.location,
                    'job_type': job.job_type,
                    'status': application.status,
                    'applied_at': application.applied_at,
                })

        return JsonResponse(result, safe=False)

    except JobSeeker.DoesNotExist:
        return JsonResponse({'error': 'Job seeker not found with the provided email'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
@csrf_exempt
def fetch_jobs_by_new_user_skills(request, user_id):
    auth_header = request.headers.get('Authorization')

    try:
        if request.method == 'GET':
            if not auth_header or not auth_header.startswith('Bearer '):
                return JsonResponse({'status': 'error', 'message': 'Token is missing or invalid format'}, status=400)

            token = auth_header.split(' ')[1]

            try:
                new_user_obj= new_user.objects.get(id=user_id, token=token)
            except new_user.DoesNotExist:
                return JsonResponse({'error': 'new user not found.'}, status=404)

            try:
                resume = Resume.objects.get(user=new_user_obj)
            except Resume.DoesNotExist:
                return JsonResponse({'error': 'New_user Resume not found.'}, status=404)

            skills = resume.skills
            skills_list = [skill.strip().lower() for skill in skills.split(',')] if skills else []

            if not skills_list:
                return JsonResponse({'error': 'No skills found for this new user.'}, status=400)

            job_queries = Q()
            for skill in skills_list:
                job_queries |= Q(skills__icontains=skill)

            jobs_from_job_model = Job.objects.filter(job_queries).distinct()
            jobs_from_job1_model = Job1.objects.filter(job_queries).distinct()

            combined_jobs = list(jobs_from_job_model) + list(jobs_from_job1_model)

            sort_order = request.GET.get('sort_order', 'latest')
            if sort_order == 'latest':
                combined_jobs = sorted(combined_jobs, key=lambda x: x.published_at, reverse=True)
            elif sort_order == 'oldest':
                combined_jobs = sorted(combined_jobs, key=lambda x: x.published_at)
            else:
                return JsonResponse({'error': 'Invalid sort order. Use "latest" or "oldest".'}, status=400)

            job_list = []
            for job in combined_jobs:
                if isinstance(job, Job):
                    job_list.append({
                        'company_name': job.company.name,
                        'job_id':job.unique_job_id_as_int,
                        'job_title': job.job_title,
                        'location': job.location,
                        'job_type': job.job_type,
                        'job_posted_date': job.published_at
                    })
                elif isinstance(job, Job1):
                    job_list.append({
                        'college': job.college.college_name,
                        'job_id':job.id,
                        'job_title': job.job_title,
                        'location': job.location,
                        'job_type': job.job_type,
                        'job_posted_date': job.published_at
                    })

            return JsonResponse({'jobs': job_list}, safe=False)
        else:
            return JsonResponse({'error': 'Invalid request method.'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500) 
    

@csrf_exempt
def membership_form_view(request, company_in_charge_id):
    if request.method == 'POST':
        try:
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return JsonResponse({'status': 'error', 'message': 'Token is missing or invalid format'}, status=400)

            token = auth_header.split(' ')[1]
            
            company_in_charge = CompanyInCharge.objects.get(id=company_in_charge_id, token=token)

            data = json.loads(request.body)
            email = data.get('email')

            if Membership.objects.filter(email=email, company_in_charge=company_in_charge).exists():
                return JsonResponse({
                    'status': 'error',
                    'message': 'A membership with this email already exists for this company. You can only submit the form once.'
                }, status=400)
            
            if email != company_in_charge.official_email:
                return JsonResponse({
                    'status': 'error',
                    'message': 'The provided email does not match the company in charge email.'
                }, status=400)
            
            form = MembershipForm(data)

            if form.is_valid():
                membership = form.save(commit=False)
                membership.company_in_charge = company_in_charge
                membership.save()
                return JsonResponse({
                    'status': 'success',
                    'message': 'Membership created successfully.',
                    'data': {
                        'id': membership.id,
                        'name': membership.name,
                        'email': membership.email,
                        'mobile': membership.mobile,
                        'course_to_purchase': membership.course_to_purchase,
                        'quantity_of_leads': membership.quantity_of_leads,
                        'location_for_leads': membership.location_for_leads,
                        'intake_year': membership.intake_year,
                    }
                }, status=201)
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Invalid data',
                    'errors': form.errors
                }, status=400)

        except CompanyInCharge.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Invalid token or company in charge not found'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)


@csrf_exempt
def advertisement_form_view(request, company_in_charge_id):
    if request.method == 'POST':
        try:
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return JsonResponse({'status': 'error', 'message': 'Token is missing or invalid format'}, status=400)

            token = auth_header.split(' ')[1]
            company_in_charge = CompanyInCharge.objects.get(id=company_in_charge_id, token=token)

            data = json.loads(request.body)
            email = data.get('email')

            if Advertisement.objects.filter(email=email, company_in_charge=company_in_charge).exists():
                return JsonResponse({
                    'status': 'error',
                    'message': 'An advertisement with this email already exists for this company. You can only submit the form once.'
                }, status=400)
            
            if email != company_in_charge.official_email:
                return JsonResponse({
                    'status': 'error',
                    'message': 'The provided email does not match the company in charge email.'
                }, status=400)
            
            form = AdvertisementForm(data)
            if form.is_valid():
                advertisement = form.save(commit=False)
                advertisement.company_in_charge = company_in_charge
                advertisement.save()
                return JsonResponse({
                    'status': 'success',
                    'message': 'Advertisement created successfully.',
                    'data': {
                        'id': advertisement.id,
                        'name': advertisement.name,
                        'email': advertisement.email,
                        'contact': advertisement.contact,
                        'advertisement_placement': advertisement.advertisement_placement,
                        'time_duration': advertisement.time_duration,
                        'investment_cost': str(advertisement.investment_cost),
                        'target_audience': advertisement.target_audience,
                    }
                }, status=201)
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Invalid data',
                    'errors': form.errors
                }, status=400)

        except CompanyInCharge.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Invalid token or company in charge not found'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

@csrf_exempt
def advertisement_form_view1(request, university_in_charge_id):
    if request.method == 'POST':
        try:
            auth_header = request.headers.get('Authorization')

            if not auth_header or not auth_header.startswith('Bearer '):
                return JsonResponse({'status': 'error', 'message': 'Token is missing or invalid format'}, status=400)

            token = auth_header.split(' ')[1]
            university = UniversityInCharge.objects.get(id=university_in_charge_id, token=token)

            data = json.loads(request.body)
            email = data.get('email')

            if CollegeAdvertisement.objects.filter(email=email).exists():
                return JsonResponse({
                    'status': 'error',
                    'message': 'An advertisement with this email already exists. You can only submit the form once.'
                }, status=400)
            
			           
            if email != university.official_email:
                return JsonResponse({
                    'status': 'error',
                    'message': 'The provided email does not match the college in charge email.'
                }, status=400)
				
            form = AdvertisementForm1(data)
            if form.is_valid():
                advertisement = form.save(commit=False)
                advertisement.university_in_charge = university
                advertisement.save()
                return JsonResponse({
                    'status': 'success',
                    'message': 'Advertisement created successfully.',
                    'data': {
                        'id': advertisement.id,
                        'name': advertisement.name,
                        'email': advertisement.email,
                        'contact': advertisement.contact,
                        'advertisement_placement': advertisement.advertisement_placement,
                        'time_duration': advertisement.time_duration,
                        'investment_cost': str(advertisement.investment_cost),
                        'target_audience': advertisement.target_audience,
                    }
                }, status=201)
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Invalid data',
                    'errors': form.errors
                }, status=400)

        except UniversityInCharge.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Invalid token or university in charge not found'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

@csrf_exempt
def membership_form_view1(request, university_in_charge_id):
    if request.method == 'POST':
        try:
            auth_header = request.headers.get('Authorization')

            if not auth_header or not auth_header.startswith('Bearer '):
                return JsonResponse({'status': 'error', 'message': 'Token is missing or invalid format'}, status=400)

            token = auth_header.split(' ')[1]
            university = UniversityInCharge.objects.get(id=university_in_charge_id, token=token)

            data = json.loads(request.body)
            email = data.get('email')

            if CollegeMembership.objects.filter(email=email).exists():
                return JsonResponse({
                    'status': 'error',
                    'message': 'A membership with this email already exists. You can only submit the form once.'
                }, status=400)
                
            if email != university.official_email:
                return JsonResponse({
                    'status': 'error',
                    'message': 'The provided email does not match the college in charge email.'
                }, status=400)
            
            form = MembershipForm1(data)
            if form.is_valid():
                membership = form.save(commit=False)
                membership.university_in_charge = university
                membership.save()
                return JsonResponse({
                    'status': 'success',
                    'message': 'Membership created successfully.',
                    'data': {
                        'id': membership.id,
                        'name': membership.name,
                        'email': membership.email,
                        'mobile': membership.mobile,
                        'course_to_purchase': membership.course_to_purchase,
                        'quantity_of_leads': membership.quantity_of_leads,
                        'location_for_leads': membership.location_for_leads,
                        'intake_year': membership.intake_year,
                    }
                }, status=201)
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Invalid data',
                    'errors': form.errors
                }, status=400)

        except UniversityInCharge.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Invalid token or university in charge not found'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

@csrf_exempt
def user_apply_for_job(request, job_id, user_id):
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return JsonResponse({'status': 'error', 'message': 'Token is missing or in an invalid format'}, status=400)

    token = auth_header.split(' ')[1]

    try:
        user = new_user.objects.get(id=user_id, token=token)
        print(user)
    except new_user.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Invalid token or user not found'}, status=404)
    
    try:
        resume = Resume.objects.get(id=user_id)
    except Resume.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Resume Not Found'}, status=404)

    try:
        job = None
        application_model = None
        university_in_charge = None
        company_in_charge = None

        try:
            job = Job1.objects.get(id=job_id)
            application_model = Application1
            university_in_charge = job.university_in_charge
        except Job1.DoesNotExist:
            try:
                job = Job.objects.get(unique_job_id_as_int=job_id)
                application_model = Application
                company_in_charge = job.company_in_charge
            except Job.DoesNotExist:
                return JsonResponse({'error': f'No jobs found for job_id {job_id} in both company and college'}, status=404)

        email = user.email

        if application_model.objects.filter(Q(email=email) & Q(job=job)).exists():
            return JsonResponse({'error': 'An application with this email already exists for this job.'}, status=400)
        
        education_entries = list(resume.education_entries.values('course_or_degree', 'school_or_university'))
        experience_entries = list(resume.experience_entries.values('company_name', 'job_title', 'start_date', 'end_date'))
       
        if application_model == Application1:
            application = Application1(
                user=user,
                job=job,
                first_name=user.firstname,
                last_name=user.lastname,
                email=email,
                phone_number=user.phonenumber,
                resume=None,  
                cover_letter="No cover letter provided",  
                skills="No skills provided",  
                university_in_charge=university_in_charge,
                bio=resume.bio,
                education=education_entries,
                experience=experience_entries,
            )
        else:  
            application = Application(
                user=user,
                job=job,
                first_name=user.firstname,
                last_name=user.lastname,
                email=email,
                phone_number=user.phonenumber,
                resume=None,  
                cover_letter="No cover letter provided",  
                skills="No skills provided", 
                company_in_charge=company_in_charge,  
                bio=resume.bio,
                education=education_entries,
                experience=experience_entries,
            )

        application.save()

        return JsonResponse({'message': 'Application submitted successfully', 'application_id': application.id}, status=201)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def jobseeker_apply_for_job(request, job_id, jobseeker_id):
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return JsonResponse({'status': 'error', 'message': 'Token is missing or in an invalid format'}, status=400)

    token = auth_header.split(' ')[1]

    try:
        jobseeker = JobSeeker.objects.get(id=jobseeker_id, token=token)
    except JobSeeker.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Invalid token or user not found'}, status=404)
    
    try:
        jobseeker_resume = JobSeeker_Resume.objects.get(id=jobseeker_id)
    except JobSeeker_Resume.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Resume Not Found'}, status=404)

    try:
        job = None
        application_model = None
        university_in_charge = None
        company_in_charge = None

        try:
            job = Job1.objects.get(id=job_id)
            application_model = Application1
            university_in_charge = job.university_in_charge
        except Job1.DoesNotExist:
            try:
                job = Job.objects.get(unique_job_id_as_int=job_id)
                application_model = Application
                company_in_charge = job.company_in_charge
            except Job.DoesNotExist:
                return JsonResponse({'error': f'No jobs found for job_id {job_id} in both company and college'}, status=404)

        email = jobseeker.email

        if application_model.objects.filter(Q(email=email) & Q(job=job)).exists():
            return JsonResponse({'error': 'An application with this email already exists for this job.'}, status=400)
         
        education_entries = list(
            jobseeker_resume.education_entries.values('course_or_degree', 'school_or_university', 'grade_or_cgpa', 'start_date', 'end_date')
        )

        experience_entries = list(
            jobseeker_resume.experience_entries.values('job_title', 'company_name', 'description', 'start_date', 'end_date')
        )
        
        if application_model == Application1:
            application = Application1(
                job_seeker=jobseeker,
                job=job,
                first_name=jobseeker.first_name,
                last_name=jobseeker.last_name,
                email=email,
                phone_number=jobseeker.mobile_number,
                resume=None,  
                cover_letter="No cover letter provided",  
                skills="No skills provided",  
                university_in_charge=university_in_charge, 
                bio=jobseeker_resume.bio,
                education=education_entries,
                experience=experience_entries 
            )
        else:  
            application = Application(
                job_seeker=jobseeker,
                job=job,
                first_name=jobseeker.first_name,
                last_name=jobseeker.last_name,
                email=email,
                phone_number=jobseeker.mobile_number,
                resume=None,  
                cover_letter="No cover letter provided",  
                skills="No skills provided", 
                company_in_charge=company_in_charge, 
                bio=jobseeker_resume.bio,
                education=education_entries,
                experience=experience_entries 
            )

        application.save()

        return JsonResponse({'message': 'Application submitted successfully', 'application_id': application.id}, status=201)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
@csrf_exempt
def fetch_company_job_applications(request, company_in_charge_id, job_id):
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return JsonResponse({'error': 'Token is missing or not in the correct format'}, status=400)

    token = auth_header.split(' ')[1]

    try:
        company_in_charge = CompanyInCharge.objects.get(id=company_in_charge_id, token=token)
    except CompanyInCharge.DoesNotExist:
        return JsonResponse({'error': 'Invalid token or company in charge not found'}, status=401)

    try:
        job = get_object_or_404(Job, company_in_charge=company_in_charge, unique_job_id_as_int=job_id)
        applications = Application.objects.filter(job=job)
        
        applications_list = [{
            'id': app.id,
            'first_name': app.first_name,
            'last_name': app.last_name,
            'email': app.email,
            'phone_number': app.phone_number,
            'bio':app.bio,
            'education':app.education,
            'experience':app.experience,
            'status': app.status,
            'applied_at': app.applied_at,
        } for app in applications]

        return JsonResponse(applications_list, safe=False, status=200)

    except Exception as e:
        return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=500)  


@csrf_exempt
def fetch_college_job_applications(request, university_in_charge_id, job_id):
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return JsonResponse({'error': 'Token is missing or invalid format'}, status=400)

    token = auth_header.split(' ')[1]

    try:
        university_in_charge = UniversityInCharge.objects.get(id=university_in_charge_id, token=token)
    except UniversityInCharge.DoesNotExist:
        return JsonResponse({'error': 'Invalid token or university in charge not found'}, status=401)

    try:
        job = get_object_or_404(Job1, university_in_charge=university_in_charge, id=job_id)

        applications = Application1.objects.filter(job=job)
        
        applications_list = [{
            'id': app.id,
            'first_name': app.first_name,
            'last_name': app.last_name,
            'email': app.email,
            'phone_number': app.phone_number,
            'bio':app.bio,
            'education':app.education,
            'experience':app.experience,
            'status': app.status,
            'applied_at': app.applied_at,
        } for app in applications]

        return JsonResponse(applications_list, safe=False, status=200)

    except Job1.DoesNotExist:
        return JsonResponse({'error': 'No Jobs Found'}, status=404)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
@csrf_exempt
def fetch_college_applicants_count(request, university_in_charge_id):

    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return JsonResponse({'error': 'Token is missing or invalid format'}, status=400)

    token = auth_header.split(' ')[1]
	
    try:
        university_in_charge =UniversityInCharge.objects.get(id=university_in_charge_id, token=token)
        
        job_title = request.GET.get('job_title')
        
        if not job_title:
            return JsonResponse({'error': 'job_title parameters are required.'}, status=400)

        college = get_object_or_404(College, university_in_charge=university_in_charge)
        job = get_object_or_404(Job1, job_title=job_title, college=college)

        applicants = Application1.objects.filter(job=job)

        applicants_list = list(applicants)
        applicants_count = len(applicants_list)

        return JsonResponse({
            'applicants_count': applicants_count,
            # 'applicants': applicants_list
        })

    except UniversityInCharge.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'University in  charge not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500) 

      

    