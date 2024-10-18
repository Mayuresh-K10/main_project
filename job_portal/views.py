from django.db import DatabaseError, IntegrityError, OperationalError, transaction
from django.shortcuts import get_object_or_404 # type: ignore
from django.http import JsonResponse # type: ignore
from django.middleware.csrf import get_token # type: ignore
from django.views.decorators.csrf import csrf_exempt # type: ignore
from django.utils import timezone # type: ignore
from django.db.models import Q # type: ignore
from rest_framework.response import Response # type: ignore
from .models import Application, Application1, Attachment, CandidateStatus_not_eligible, College_Attachment, College_Message,Message, CandidateStatus_rejected, CandidateStatus_selected, CandidateStatus_under_review, College, CollegeEnquiry, Interview, Job, Company, Job1, MembershipPlan, Resume, ScreeningAnswer, ScreeningQuestion, Student, StudentEnquiry, UserSubscription, Visitor
from .forms import AchievementForm, Application1Form, ApplicationForm, CancelSubscriptionForm,CertificationForm, CollegeForm, CompanyForm, EducationForm, ExperienceForm, Job1Form, JobForm, ObjectiveForm, ProjectForm, PublicationForm, ReferenceForm, ResumeForm, StudentForm, SubscriptionForm, VisitorRegistrationForm
import json, operator, os
from datetime import timedelta
from django.utils.decorators import method_decorator # type: ignore
from django.views import View # type: ignore
from rest_framework.authtoken.views import ObtainAuthToken # type: ignore
from rest_framework.authtoken.models import Token # type: ignore
from rest_framework import status # type: ignore
from functools import reduce
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password

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
            } for job in jobs]

            return JsonResponse(jobs_list, safe=False, status=200)

        elif request.method == 'POST':
            return handle_post_request(request)

        return JsonResponse({'error': 'Method not allowed'}, status=405)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def handle_post_request(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    company_name = data.get('company')
    if not company_name:
        return JsonResponse({'error': 'Company name is required'}, status=400)

    try:
        company = Company.objects.get(name=company_name)
    except Company.DoesNotExist:
        return JsonResponse({'error': f'Company with name "{company_name}" does not exist'}, status=404)

    if Job.objects.filter(company=company).count() >= 100:
        return JsonResponse({'message': 'Limit exceeded for job postings by this company'}, status=200)

    job_skills = data.get('skills', '')
    if job_skills:
        unique_job_list = list(set(job_skills.split(', ')))
        data['skills'] = ', '.join(unique_job_list)

    data['company'] = company.id

    form = JobForm(data)
    if form.is_valid():
        job = form.save()

        promoting_job = data.get('promoting_job').lower()
        if promoting_job == 'true':
            return JsonResponse({'message': 'Job Created Successfully with Promoting', 'job_id': job.id}, status=201)
        elif promoting_job == 'false':
            return JsonResponse({'message': 'Job Created Successfully without Promoting', 'job_id': job.id}, status=201)
        else:
            return JsonResponse({'message': 'Please specify if the job is promoting or not', 'job_id': job.id}, status=400)

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
def apply_job(request, job_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        json_data = json.loads(request.POST.get('data', '{}'))
        job = get_object_or_404(Job, id=job_id)

        email = json_data.get('email')
        if not email:
            return JsonResponse({'error': 'Email is required'}, status=400)

        if Application.objects.filter(email=email, job=job).exists():
            return JsonResponse({'error': 'An application with this email already exists for this job.'}, status=400)

        student = Student.objects.filter(email=email).first()
        if not student:
            return JsonResponse({'error': 'Student with this email does not exist'}, status=404)

        form = ApplicationForm(json_data, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.student = student  

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

@method_decorator(csrf_exempt, name='dispatch')
class CompanyListCreateView(View):
    def get(self, request):
        try:
            companies = list(Company.objects.all().values())
            return JsonResponse(companies, safe=False, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    def post(self, request):
        try:
            company_email = request.POST.get('email')
            if not company_email:
                return JsonResponse({'status': 'error', 'message': 'Email is required'}, status=400)

            company = Company.objects.filter(email=company_email).first()

            if company:
                company_form = CompanyForm(request.POST, request.FILES, instance=company)
            else:
                company_form = CompanyForm(request.POST, request.FILES)

            if company_form.is_valid():
                company = company_form.save()

                delete_attachment = request.POST.get('is_deleted', 'false').lower() == 'true'
                if delete_attachment and company.Attachment:
                    if os.path.exists(company.Attachment.path):
                        os.remove(company.Attachment.path)
                    company.Attachment = None
                    company.save()

                    return JsonResponse({'status': 'success', 'message': 'Attachment deleted successfully', 'company_id': company.id}, status=200)

                return JsonResponse({'status': 'success', 'message': 'Company created successfully', 'company_id': company.id}, status=201)
            else:
                return JsonResponse(company_form.errors, status=400)

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

def company_status(request, status_choice):
    try:
        co_name = request.GET['name']

        try:
            company = Company.objects.get(name=co_name)
        except Company.DoesNotExist:
            return JsonResponse({'error': f'Company "{co_name}" does not exist.'}, status=404)

        job_id = Job.objects.filter(company=company)

        apply_id = Application.objects.filter(job__in=job_id)

        name = []
        if status_choice == 'selected':
            candidate_status_modelname = CandidateStatus_selected
        elif status_choice == 'rejected':
            candidate_status_modelname = CandidateStatus_rejected
        elif status_choice == 'not_eligible':
            candidate_status_modelname = CandidateStatus_not_eligible
        elif status_choice == 'under_review':
            candidate_status_modelname = CandidateStatus_under_review
        for application in apply_id:
            if application.status == status_choice:
                name.append(application.first_name)
                candidate_status_modelname.objects.create(
                    first_name=application.first_name,
                    status=status_choice,
                    company_name=co_name,
                    job_id=application.job_id
                )

        return JsonResponse({'message': name}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def create_resume(request):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                user_email = request.POST.get('email')
                print("User Email:", user_email)

                if not user_email:
                    return JsonResponse({'status': 'error', 'message': 'Email is required'}, status=400)

                resume = Resume.objects.filter(email=user_email).first()
                print("Resume Object:", resume)

                if resume:
                    resume_form = ResumeForm(request.POST, request.FILES, instance=resume)
                else:
                    resume_form = ResumeForm(request.POST, request.FILES)

                print("Resume Form Validity:", resume_form.is_valid())

                # if resume_form.is_valid():
                #     delete_attachment = request.POST.get('delete', 'false').lower() == 'true'
                #     new_attachment = request.FILES.get('Attachment')

                if resume_form.is_valid():
                    delete_attachment = resume_form.cleaned_data.get('delete', False)
                    new_attachment = resume_form.cleaned_data.get('Attachment')

                    if new_attachment and resume and resume.Attachment:
                        if os.path.exists(resume.Attachment.path):
                            print("Deleting old attachment:", resume.Attachment.path)
                            os.remove(resume.Attachment.path)

                    resume = resume_form.save()

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

                        objective_form = ObjectiveForm(objective_data, instance=objective_instance)
                    else:
                        objective_form = ObjectiveForm(objective_data)

                    if objective_form.is_valid():
                        objective = objective_form.save(commit=False)
                        objective.resume = resume
                        objective.save()

                def save_related_data(form_class, data_list, related_name):
                    for item in data_list:
                        form = form_class(item)
                        if form.is_valid():
                            obj = form.save(commit=False)
                            obj.resume = resume
                            obj.save()
                        else:
                            print(f"{related_name} Form Errors:", form.errors)

                save_related_data(EducationForm, json.loads(request.POST.get('education', '[]')), 'Education')
                save_related_data(ExperienceForm, json.loads(request.POST.get('experience', '[]')), 'Experience')
                save_related_data(ProjectForm, json.loads(request.POST.get('projects', '[]')), 'Projects')
                save_related_data(ReferenceForm, json.loads(request.POST.get('references', '[]')), 'References')
                save_related_data(CertificationForm, json.loads(request.POST.get('certifications', '[]')), 'Certifications')
                save_related_data(AchievementForm, json.loads(request.POST.get('achievements', '[]')), 'Achievements')
                save_related_data(PublicationForm, json.loads(request.POST.get('publications', '[]')), 'Publications')

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

def get_resume_detail_by_id(request, resume_id):
    try:
        if request.method == 'GET':
            resume = get_object_or_404(Resume, id=resume_id)

            resume_data = {
                "first_name": resume.first_name,
                "last_name":resume.last_name,
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
                        "description" : education.description
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
                        "project_link" : project.project_link
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

class CustomObtainAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            message = "New token created" if created else "Existing token retrieved"
            return Response({
                'token': token.key,
                'username': user.username,
                'message': message
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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

def application_status_counts(request):
    try:
        email = request.GET.get('email')
        if not email:
            return JsonResponse({'error': 'Email parameter is required'}, status=400)

        total_jobs_applied_count = Application.objects.filter(email=email).count()
        pending_count = Application.objects.filter(email=email, status='pending').count()
        interview_scheduled_count = Application.objects.filter(email=email, status='interview_scheduled').count()
        rejected_count = Application.objects.filter(email=email, status='rejected').count()
        college_enquiries_count = StudentEnquiry.objects.filter(email=email).count()

        return JsonResponse({
            'total_jobs_applied':total_jobs_applied_count,
            'pending_count': pending_count,
            'interview_scheduled': interview_scheduled_count,
            'rejected_count': rejected_count,
            'college_enquiries_count': college_enquiries_count
        })

    except Application.DoesNotExist:
        return JsonResponse({'error': 'No applications found for the provided email.'}, status=404)
    except Exception as e:
        return JsonResponse({'error': 'An error occurred', 'details': str(e)}, status=500)

def filter_applied_jobs(request):
    try:
        email = request.GET.get('email')
        if not email:
            return JsonResponse({'error': 'Email parameter is required'}, status=400)

        job_title = request.GET.get('job_title')
        status = request.GET.get('status')
        job_type = request.GET.get('job_type')
        sort_by = request.GET.get('sort_by')

        applications = Application.objects.filter(email=email)

        if job_title:
            applications = applications.filter(job__job_title=job_title)

        if status:
            applications = applications.filter(status=status)

        if job_type:
            applications = applications.filter(job__job_type=job_type)

        if sort_by == 'job_title_asc':
            applications = applications.order_by('job__job_title')
        elif sort_by == 'job_title_desc':
            applications = applications.order_by('-job__job_title')
        elif sort_by == 'applied_at_asc':
            applications = applications.order_by('applied_at')
        elif sort_by == 'applied_at_desc':
            applications = applications.order_by('-applied_at')

        result = []
        for application in applications:
            result.append({
                'job_title': application.job.job_title,
                'company': application.job.company.name,
                'job_location': application.job.location,
                'job_type': application.job.job_type,
                'status': application.status,
                'applied_at': application.applied_at,
            })

        return JsonResponse(result, safe=False)

    except Application.DoesNotExist:
        return JsonResponse({'error': 'No applications found for the provided email'}, status=404)
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

@csrf_exempt
def delete_account(request, username):
    if request.method != 'POST':
        return JsonResponse({"error": "Invalid request method."}, status=400)

    try:
        data = json.loads(request.body)
        confirm = data.get('confirm', '').lower()

        if confirm == 'yes':
            user = User.objects.get(username=username, is_superuser=True)
            user.delete()
            return JsonResponse({"message": f"Admin user '{username}' has been deleted successfully."})
        elif confirm == 'no':
            return JsonResponse({"message": "Account deletion canceled."})

        return JsonResponse({"error": "Invalid confirmation input. Please send 'yes' or 'no'."}, status=400)

    except User.DoesNotExist:
        return JsonResponse({"error": "Admin user not found."}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON input."}, status=400)

@csrf_exempt
def save_student(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)

    data = json.loads(request.body)
    email = data.get('email')

    if Student.objects.filter(email=email).exists():
        return JsonResponse({'message': 'Student is already registered with this email'}, status=400)

    form = StudentForm(data)
    if form.is_valid():
        student = form.save()
        return JsonResponse({'message': 'Student data saved successfully', 'student_id': student.id}, status=201)

    return JsonResponse({'errors': form.errors}, status=400)

@csrf_exempt
def fetch_jobs_by_student_skills(request):
    try:
        if request.method == 'GET':
            student_id = request.GET.get('student_id')
            sort_order = request.GET.get('sort_order', 'latest')

            if not student_id:
                return JsonResponse({'error': 'Please provide a student ID.'}, status=400)

            try:
                student = Student.objects.get(id=student_id)
            except Student.DoesNotExist:
                return JsonResponse({'error': 'Student not found.'}, status=404)

            skills = student.skills
            skills_list = [skill.strip().lower() for skill in skills.split(',')] if skills else []

            jobs = Job.objects.all()
            if skills_list:
                queries = Q()
                for skill in skills_list:
                    queries |= Q(skills__icontains=skill)
                jobs = jobs.filter(queries).distinct()

            if not skills_list:
                return JsonResponse({'error': 'No skills found for this student.'}, status=400)

            if sort_order == 'latest':
                jobs = jobs.order_by('-published_at')
            elif sort_order == 'oldest':
                jobs = jobs.order_by('published_at')
            else:
                return JsonResponse({'error': 'Invalid sort order. Use "latest" or "oldest".'}, status=400)

            job_list = []
            for job in jobs:
                job_list.append({
                    'company_name': job.company.name,
                    'job_title': job.job_title,
                    'location': job.location,
                    'job_type': job.job_type,
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

def company_status_counts(request):
    company_name = request.GET.get('company_name')

    if not company_name:
        return JsonResponse({'error': 'Company name is required'}, status=400)

    try:
        company = Company.objects.get(name=company_name)
        print(company)
    except Company.DoesNotExist:
        return JsonResponse({'error': 'Company not found'}, status=404)

    total_applications = Application.objects.filter(job__company=company).count()
    shortlisted_count = Application.objects.filter(job__company=company, status='shortlisted').count()
    rejected_count = Application.objects.filter(job__company=company, status='rejected').count()
    jobs_posted = Job.objects.filter(company=company).count()

    data = {
        'total_applications': total_applications,
        'shortlisted_count': shortlisted_count,
        'rejected_count': rejected_count,
        'jobs_posted': jobs_posted
    }

    return JsonResponse(data)

def jobs_by_company(request):
    try:
        company_name = request.GET.get('name')
        sort_order = request.GET.get('sort_order')
        job_status = request.GET.get('job_status')

        if not (company_name or sort_order or job_status):
            return JsonResponse({'error': 'Select at least one parameter'}, status=400)

        if company_name:
            company = get_object_or_404(Company, name=company_name)
            jobs = Job.objects.filter(company=company)
        else:
            jobs = Job.objects.all()

        if job_status:
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
def save_screening_questions_and_answers(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))

            job_id = data.get('job_id')
            questions_and_answers = data.get('questions_and_answers')

            if not job_id:
                return JsonResponse({'status': 'error', 'message': 'Job ID is missing'}, status=400)

            if not questions_and_answers:
                return JsonResponse({'status': 'error', 'message': 'Questions and answers are missing'}, status=400)

            job = Job.objects.get(id=job_id)

            for qa in questions_and_answers:
                question_text = qa.get('question')
                correct_answer = qa.get('correct_answer')

                ScreeningQuestion.objects.create(
                    job=job,
                    question_text=question_text,
                    correct_answer=correct_answer
                )

            return JsonResponse({'status': 'success', 'message': 'Questions and answers saved successfully'}, status=201)

        except Job.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Job not found'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

@csrf_exempt
def submit_application_with_screening(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        data = json.loads(request.body)

        email = data.get('email')
        skills = data.get('skills')
        must_have_qualification = data.get('must_have_qualification', False)
        answers = data.get('answers')

        if not email or not answers:
            return JsonResponse({"error": "Email or answers are missing"}, status=400)

        student = Student.objects.filter(email=email).first()
        if not student:
            return JsonResponse({"error": "Student not found with this email"}, status=400)

        first_question_id = answers[0].get('question_id')
        if not first_question_id:
            return JsonResponse({"error": "First question ID is missing"}, status=400)

        first_question = ScreeningQuestion.objects.filter(id=first_question_id).first()
        if not first_question:
            return JsonResponse({"error": f"Invalid question_id: {first_question_id}"}, status=400)

        job = first_question.job

        if Application.objects.filter(job=job, student=student).exists():
            return JsonResponse({"error": f"Student with email {email} has already submitted an application for this job."}, status=400)

        application = Application.objects.create(
            job=job,
            email=email,
            student=student,
            skills=skills,
            status="pending"
        )

        correct_answers = {question.id: question.correct_answer for question in ScreeningQuestion.objects.filter(job=job)}
        all_answers_correct = True

        for answer_data in answers:
            question_id = answer_data.get('question_id')
            answer_text = answer_data.get('answer')

            if not question_id or not answer_text:
                return JsonResponse({"error": "Question ID or answer is missing"}, status=400)

            question = ScreeningQuestion.objects.filter(id=question_id, job=job).first()
            if not question:
                return JsonResponse({"error": f"Invalid question_id: {question_id}"}, status=400)

            is_correct = (correct_answers.get(question.id) == answer_text)

            ScreeningAnswer.objects.create(
                application=application,
                question=question,
                answer_text=answer_text
            )

            if not is_correct:
                all_answers_correct = False

        if all_answers_correct and must_have_qualification:
            application.status = 'selected'
            status_message = "accepted"
        elif must_have_qualification and not all_answers_correct:
            application.status = 'rejected'
            status_message = "rejected"
        else:
            application.status = 'pending'
            status_message = "pending"

        application.save()

        email_subject = "Job Application Status"
        email_body = f"Dear Applicant,\n\nYour application for the job {job.job_title} has been {status_message}."
        send_mail(
            email_subject,
            email_body,
            settings.EMAIL_HOST_USER,
            [application.email],
            fail_silently=False,
        )

        return JsonResponse({"message": f"Application submitted successfully and applicant {status_message}."}, status=201)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

@csrf_exempt
def myInbox(request):
    if request.method != "GET":
        return JsonResponse({'status': 'false', 'message': 'Invalid request method'}, status=405)

    email = request.GET.get('email')
    filter_value = request.GET.get('filter')

    if not email:
        return JsonResponse({'status': 'false', 'message': 'Email is required'}, status=400)

    try:
        messages_query = Message.objects.filter(
            Q(sender__email=email) | Q(company_recipient__email=email)
        ).order_by('-timestamp')

        if filter_value in ['read', 'unread']:
            is_read = filter_value == 'read'
            messages_query = messages_query.filter(is_read=is_read)

        message_list = [
            {
                'id': message.id,
                'sender': message.sender.email,
                'recipient': message.company_recipient.email,
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

    except Exception as e:
        return JsonResponse({'status': 'false', 'error': str(e)}, status=500)

@csrf_exempt
def getMessages(request):
    if request.method != "GET":
        return JsonResponse({'status': 'false', 'message': 'Invalid request method'}, status=405)

    try:
        sender_email = request.GET.get('sender_email')
        recipient_email = request.GET.get('recipient_email')

        if not all([sender_email, recipient_email]):
            return JsonResponse({'status': 'false', 'message': 'Required fields missing'}, status=400)

        sender = get_object_or_404(User, email=sender_email)
        company_recipient = get_object_or_404(Company, email=recipient_email)

        all_messages = Message.objects.filter(
            sender=sender,
            company_recipient=company_recipient
        ).prefetch_related('attachments')

        if not all_messages.exists():
            return JsonResponse({'status': 'false', 'message': 'No messages found'}, status=404)

        all_messages.filter(is_read=False).update(is_read=True)

        messages_data = []
        for message in all_messages:
            attachments = message.attachments.all()
            attachments_data = [
                {
                    'file_url': attachment.file.url,
                    'uploaded_at': attachment.uploaded_at
                }
                for attachment in attachments
            ]

            messages_data.append({
                'message_id': message.id,
                'sender_email': message.sender.email,
                'recipient_email': message.company_recipient.email,
                'content': message.content,
                'timestamp': message.timestamp,
                'is_read': message.is_read,  
                'attachments': attachments_data
            })

        return JsonResponse({'status': 'success', 'messages': messages_data}, status=200)

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@csrf_exempt
def sendMessage(request):
    if request.method != "POST":
        return JsonResponse({'status': 'false', 'message': 'Invalid request method'}, status=405)

    sender_email = request.POST.get('sender_email')
    recipient_email = request.POST.get('recipient_email')
    message_content = request.POST.get('content')

    if not all([sender_email, recipient_email, message_content]):
        return JsonResponse({'status': 'false', 'message': 'Required fields missing'}, status=400)

    try:
        sender = get_object_or_404(User, email=sender_email)
        recipient = get_object_or_404(Company, email=recipient_email)

        message = Message.objects.create(sender=sender, company_recipient=recipient, content=message_content)

        attachments = request.FILES.getlist('attachments', [])
        Attachment.objects.bulk_create([
            Attachment(message=message, file=file) for file in attachments
        ])

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
            [recipient.email],
            fail_silently=False,
        )

        return JsonResponse({'status': 'success', 'message': 'Message sent successfully!'}, status=201)

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@csrf_exempt
def searchUser(request):
    if request.method != "GET":
        return JsonResponse({'status': 'false', 'message': 'Invalid request method'}, status=405)

    query = request.GET.get('q', '').strip()

    try:
        user_contacts = User.objects.all().values('id', 'username', 'email')
        company_contacts = Company.objects.all().values('id', 'name', 'email')

        if query:
            user_contacts = user_contacts.filter(
                Q(username__icontains=query) |
                Q(email__icontains=query)
            )
            company_contacts = company_contacts.filter(
                Q(name__icontains=query) |
                Q(email__icontains=query)
            )

        contact_list = list(user_contacts) + list(company_contacts)

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
@login_required
def choose_plan(request):
    try:
        subscription, _ = UserSubscription.objects.get_or_create(user=request.user)

        if request.method == 'POST':
            form = SubscriptionForm(request.POST)
            if form.is_valid():
                plan_id = form.cleaned_data['plan']
                membership_plan = MembershipPlan.objects.get(id=plan_id)

                subscription.current_plan = membership_plan
                subscription.save()

                return JsonResponse({'message': 'Subscription plan updated successfully'}, status=200)
            else:
                return JsonResponse({'errors': form.errors}, status=400)
        else:
            initial_plan = subscription.current_plan if subscription.current_plan in MembershipPlan.objects.all() else None
            form = SubscriptionForm(initial={'plan': initial_plan})

            plan_choices = [{'id': plan.id, 'name': plan.name} for plan in form.fields['plan'].queryset]

            return JsonResponse({
                'message': 'Choose a plan',
                'current_plan': subscription.current_plan.name if subscription.current_plan else None,
                'plan_choices': plan_choices
            })

    except DatabaseError as db_err:
        return JsonResponse({'error': 'Database error occurred', 'details': str(db_err)}, status=500)
    except MembershipPlan.DoesNotExist:
        return JsonResponse({'error': 'Selected plan does not exist'}, status=400)
    except Exception as e:
        return JsonResponse({'error': 'An unexpected error occurred', 'details': str(e)}, status=500)

@csrf_exempt
@login_required
def cancel_plan(request):
    try:
        subscription = get_object_or_404(UserSubscription, user=request.user)

        if request.method == 'POST':
            form = CancelSubscriptionForm(request.POST)
            if form.is_valid():
                form.cancel_subscription(user=request.user)
                return JsonResponse({'message': 'Subscription cancelled successfully'}, status=200)
            else:
                return JsonResponse({'errors': form.errors}, status=400)
        else:
            return JsonResponse({
                'message': 'Confirm cancellation',
                'current_plan': subscription.current_plan.name if subscription.current_plan else 'No Plan',
                'active': subscription.active
            })

    except DatabaseError as db_err:
        return JsonResponse({'error': 'Database error occurred', 'details': str(db_err)}, status=500)
    except Exception as e:
        return JsonResponse({'error': 'An unexpected error occurred', 'details': str(e)}, status=500)

@login_required
def subscription_detail(request):
    try:
        subscription = get_object_or_404(UserSubscription, user=request.user)

        subscription_data = {
            'plan_name': subscription.current_plan.name if subscription.current_plan else 'No Plan',
            'renewal_date': subscription.renewal_date,
            'active': subscription.active,
        }

        return JsonResponse(subscription_data, status=200)

    except DatabaseError as db_err:
        return JsonResponse({'error': 'Database error occurred', 'details': str(db_err)}, status=500)
    except Exception as e:
        return JsonResponse({'error': 'An unexpected error occurred', 'details': str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class CollegeListCreateView(View):

    def get(self, request):
        try:
            colleges = list(College.objects.values_list('id', 'college_name', 'email', 'Attachment'))  # Optimize query
            return JsonResponse(colleges, safe=False, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    def post(self, request):
        try:
            college_email = request.POST.get('email')
            if not college_email:
                return JsonResponse({'status': 'error', 'message': 'Email is required'}, status=400)

            college = College.objects.filter(email=college_email).first()
            college_form = CollegeForm(request.POST, request.FILES, instance=college if college else None)

            if college_form.is_valid():
                college = college_form.save()

                if request.POST.get('is_deleted', 'false').lower() == 'true' and college.Attachment:
                    attachment_path = college.Attachment.path
                    if os.path.exists(attachment_path):
                        os.remove(attachment_path)
                    college.Attachment = None
                    college.save(update_fields=['Attachment'])

                    return JsonResponse({'status': 'success', 'message': 'Attachment deleted successfully', 'college_id': college.id}, status=200)

                return JsonResponse({'status': 'success', 'message': 'College created successfully', 'college_id': college.id}, status=201)
            else:
                return JsonResponse(college_form.errors, status=400)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def submit_college_enquiry(request, college_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    required_fields = ['first_name', 'last_name', 'email', 'mobile_number', 'course','status']
    if not all(data.get(field) for field in required_fields):
        return JsonResponse({'error': 'All fields are required'}, status=400)

    first_name, last_name, email, mobile_number, course, status= (
        data['first_name'], data['last_name'], data['email'], data['mobile_number'], data['course'], data['status']
    )

    try:
        college = College.objects.get(id=college_id)
    except College.DoesNotExist:
        return JsonResponse({'error': 'Invalid college ID'}, status=400)

    if CollegeEnquiry.objects.filter(email=email, college=college).exists():
        return JsonResponse({'error': 'An enquiry with this email has already been submitted for this college.'}, status=400)

    try:
        enquiry = CollegeEnquiry.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            mobile_number=mobile_number,
            course=course,
            status=status,
            college=college
        )
        return JsonResponse({'message': 'Enquiry submitted successfully', 'enquiry_id': enquiry.id}, status=201)
    except IntegrityError:
        return JsonResponse({'error': 'Error while saving enquiry. Please try again.'}, status=400)

@csrf_exempt
def college_status_counts(request):
    college_id = request.GET.get('college_id')

    if not college_id:
        return JsonResponse({'error': 'college_id is required'}, status=400)

    try:
        college_id = int(college_id)
    except ValueError:
        return JsonResponse({'error': 'Invalid college_id. It must be an integer.'}, status=400)

    if not College.objects.filter(id=college_id).exists():
       return JsonResponse({'error': 'College not found'}, status=404)

    try:
        enquiry_count = CollegeEnquiry.objects.filter(college_id=college_id).count()
        job_posted_count = Job1.objects.filter(college_id=college_id).count()
        total_visitor_count = Visitor.objects.filter(college_id=college_id).count()
        shortlisted_count = Application1.objects.filter(job__college_id=college_id, status='shortlisted').count()

        return JsonResponse({
            'total_visitor_count': total_visitor_count,
            'shortlisted_count': shortlisted_count,
            'job_posted_count': job_posted_count,
            'enquiry_count': enquiry_count
        }, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def create_job_for_college(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            college_id = data.get('college')
            if not college_id:
                return JsonResponse({'error': 'College ID is required'}, status=400)

            try:
                college = College.objects.get(id=college_id)
            except College.DoesNotExist:
                return JsonResponse({'error': 'College not found'}, status=404)

            form = Job1Form(data)
            if form.is_valid():
                jobs = form.save(commit=False)
                jobs.college = college
                jobs.save()

                promoting_job = data.get('promoting_job', '').lower()
                if promoting_job == 'true':
                    return JsonResponse({'message': 'Job Created Successfully with Promoting', 'job_id': jobs.id}, status=201)
                elif promoting_job == 'false':
                    return JsonResponse({'message': 'Job Created Successfully without Promoting', 'job_id': jobs.id}, status=201)
                else:
                    return JsonResponse({'error': 'Please specify if the job is promoting or not'}, status=400)

            else:
                return JsonResponse({'error': 'Invalid form data', 'errors': form.errors}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method. Use POST.'}, status=405)

@csrf_exempt
def apply__college_job(request, job_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        json_data = json.loads(request.POST.get('data', '{}'))
        job = get_object_or_404(Job1, id=job_id)

        email = json_data.get('email')
        if not email:
            return JsonResponse({'error': 'Email is required'}, status=400)

        if Application1.objects.filter(Q(email=email) & Q(job=job)).exists():
            return JsonResponse({'error': 'An application with this email already exists for this job.'}, status=400)

        form = Application1Form(json_data, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job

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
def register_visitor(request, college_id):
    if request.method != "POST":
        return JsonResponse({'error': 'Invalid request method'}, status=405)

    try:
        data = json.loads(request.body.decode('utf-8'))
        college = get_object_or_404(College, id=college_id)

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
            visitor.save()

            return JsonResponse({'message': 'Visitor registered successfully'}, status=201)
        else:
            return JsonResponse({'error': form.errors}, status=400)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON format'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def login_visitor(request):
    if request.method != "POST":
        return JsonResponse({'error': 'Invalid request method'}, status=405)

    try:
        data = json.loads(request.body.decode('utf-8'))
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return JsonResponse({'error': 'Email and password are required'}, status=400)

        visitor = get_object_or_404(Visitor, email=email)

        if check_password(password, visitor.password):
            return JsonResponse({'message': 'Login successful'}, status=200)
        else:
            return JsonResponse({'error': 'Invalid credentials'}, status=400)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON format'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def college_jobs_api(request, college_id):
    try:
        jobs = Job1.objects.filter(college_id=college_id).values('job_title', 'location', 'job_status')

        if not jobs:
            return JsonResponse({"message": "No jobs found for the given college ID"}, status=404)

        return JsonResponse(list(jobs), safe=False, status=200)

    except ObjectDoesNotExist:
        return JsonResponse({"error": "Invalid college ID"}, status=400)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def student_enquiries(request, college_id):
    try:
        jobs = CollegeEnquiry.objects.filter(college_id=college_id).values('first_name','last_name','course','status')

        if not jobs:
            return JsonResponse({"message": "No enquiries found for the given college ID"}, status=404)

        return JsonResponse(list(jobs), safe=False, status=200)

    except ObjectDoesNotExist:
        return JsonResponse({"error": "Invalid college ID"}, status=400)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def jobs_by_college(request):
    try:
        college_id = request.GET.get('college_id')
        sort_order = request.GET.get('sort_order')
        job_status = request.GET.get('job_status')

        if not (college_id or sort_order or job_status):
            return JsonResponse({'error': 'Select at least one parameter'}, status=400)

        jobs = Job1.objects.all()

        if college_id:
            college = get_object_or_404(College, id=college_id)
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
def student_enquiries_for_college(request, college_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    required_fields = ['first_name', 'last_name', 'email', 'mobile_number', 'course','status']
    if not all(data.get(field) for field in required_fields):
        return JsonResponse({'error': 'All fields are required'}, status=400)

    college = get_object_or_404(College, id=college_id)

    if StudentEnquiry.objects.filter(email=data['email'], college=college).exists():
        return JsonResponse({'error': 'An enquiry with this email has already been submitted for this college.'}, status=400)

    try:
        enquiry = StudentEnquiry.objects.create(
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            mobile_number=data['mobile_number'],
            course=data['course'],
            status=data['status'],
            college=college
        )
        return JsonResponse({'message': 'Enquiry submitted successfully', 'enquiry_id': enquiry.id}, status=201)
    except IntegrityError:
        return JsonResponse({'error': 'Error while saving enquiry. Please try again.'}, status=400)

@csrf_exempt
def fetch_student_enquiries(request):
    email = request.GET.get('email')

    try:
        students = StudentEnquiry.objects.filter(email=email).values('first_name', 'last_name', 'course','status') if email else StudentEnquiry.objects.values('first_name', 'last_name', 'course','status')

        return JsonResponse(list(students), safe=False)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def fetch_applicants(request):
    try:
        company_name = request.GET.get('company_name')
        job_title = request.GET.get('job_title')

        if not company_name or not job_title:
            return JsonResponse({'error': 'Both company_name and job_title parameters are required.'}, status=400)

        company = get_object_or_404(Company, name=company_name)
        job = get_object_or_404(Job, job_title=job_title, company=company)

        applicants = Application.objects.filter(job=job).values(
            'first_name', 'last_name', 'bio', 'education', 'experience', 'status'
        )

        applicants_list = list(applicants)
        applicants_count = len(applicants_list)

        return JsonResponse({
            'applicants_count': applicants_count,
            'applicants': applicants_list
        })

    except Company.DoesNotExist:
        return JsonResponse({'error': 'Company not found.'}, status=404)
    except Job.DoesNotExist:
        return JsonResponse({'error': 'Job not found for this company.'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def schedule_interview(request):
    if request.method != "POST":
        return JsonResponse({'error': 'Invalid request method. Please use POST.'}, status=405)

    try:
        data = json.loads(request.body)

        action = data.get('action')
        applicant_id = data.get('applicant_id')
        round = data.get('round')
        interview_date = data.get('interview_date')

        if not action or not applicant_id or not interview_date:
            return JsonResponse({'error': 'action, applicant_id, and interview_date parameters are required.'}, status=400)

        applicant = get_object_or_404(Application, id=applicant_id)
        student = applicant.student

        if Interview.objects.filter(applicant=applicant).exists():
            return JsonResponse({
                'message': f'Interview is already scheduled for applicant ID {applicant_id}.'
            }, status=400)

        if action == 'collegecue platform':
            job = applicant.job
            company_name = job.company.name if job.company else "N/A"

            interview = Interview.objects.create(
                candidate_name=applicant.first_name,
                applicant=applicant,
                student=student,
                round=round,
                interview_date=interview_date,
                job=job
            )

            interview_details = {
                'company_name': company_name,
                'applicant_name': f"{applicant.first_name} {applicant.last_name}",
                'job_profile': job.job_title,
                'applicant_id': applicant.id,
                'interview_date': interview_date
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
def get_upcoming_interviews(request):
    if request.method != "GET":
        return JsonResponse({'error': 'Invalid request method. Please use GET.'}, status=405)

    company_name = request.GET.get('company_name')
    if not company_name:
        return JsonResponse({'error': 'company_name parameter is required.'}, status=400)

    try:
        upcoming_interviews = Interview.objects.filter(
            job__company__name=company_name,
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

        return JsonResponse({'upcoming_interviews': interviews_list})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def get_past_interviews(request):
    if request.method != "GET":
        return JsonResponse({'error': 'Invalid request method. Please use GET.'}, status=405)

    company_name = request.GET.get('company_name')
    if not company_name:
        return JsonResponse({'error': 'company_name parameter is required.'}, status=400)

    try:
        past_interviews = Interview.objects.filter(
            job__company__name=company_name,
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

        return JsonResponse({'past_interviews': interviews_list})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def get_upcoming_interviews_by_job_title(request):
    if request.method != "GET":
        return JsonResponse({'error': 'Invalid request method. Please use GET.'}, status=405)

    student_email = request.GET.get('student_email')
    job_title = request.GET.get('job_title')

    if not student_email or not job_title:
        return JsonResponse({'error': 'student_email and job_title parameters are required.'}, status=400)

    try:
        student = get_object_or_404(Student, email=student_email)

        upcoming_interviews = Interview.objects.filter(
            student=student,
            applicant__job__job_title=job_title,
            interview_date__gte=timezone.now(),
            applicant__student__email=student.email
        ).select_related('job__company')

        interviews_data = [
            {
                'job_title': interview.job.job_title,
                'job_id': interview.job.id,
                'company_name': interview.job.company.name,
                'interview_date': interview.interview_date.date(),
                'interview_time': interview.interview_date.time(),
                'time_left': str(interview.time_left()) if interview.time_left() else 'Expired',
                'can_attend': interview.time_left() and interview.time_left().total_seconds() > 0,
            }
            for interview in upcoming_interviews
        ]

        return JsonResponse({'upcoming_interviews': interviews_data})

    except Student.DoesNotExist:
        return JsonResponse({'error': 'Student not found.'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def get_past_interviews_by_job_title(request):
    if request.method != "GET":
        return JsonResponse({'error': 'Invalid request method. Please use GET.'}, status=405)

    student_email = request.GET.get('student_email')
    job_title = request.GET.get('job_title')

    if not student_email or not job_title:
        return JsonResponse({'error': 'student_email and job_title parameters are required.'}, status=400)

    try:
        student = get_object_or_404(Student, email=student_email)

        past_interviews = Interview.objects.filter(
            student=student,
            applicant__job__job_title=job_title,
            interview_date__lt=timezone.now(),
            applicant__student__email=student.email
        ).select_related('job__company')

        interviews_data = [
            {
                'job_title': interview.job.job_title,
                'job_id': interview.job.id,
                'company_name': interview.job.company.name,
                'interview_date': interview.interview_date.date(),
                'interview_time': interview.interview_date.time(),
            }
            for interview in past_interviews
        ]

        return JsonResponse({'past_interviews': interviews_data})

    except Student.DoesNotExist:
        return JsonResponse({'error': 'Student not found.'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def search_clg_user(request):
    if request.method != "GET":
        return JsonResponse({'status': 'false', 'message': 'Invalid request method'}, status=405)

    query = request.GET.get('q', '').strip()

    try:
        user_contacts = User.objects.all().values('id', 'username', 'email')
        college_contacts = College.objects.all().values('id', 'college_name', 'email')

        if query:
            user_contacts = user_contacts.filter(
                Q(username__icontains=query) |
                Q(email__icontains=query)
            )
            college_contacts = college_contacts.filter(
                Q(college_name__icontains=query) |
                Q(email__icontains=query)
            )

        contact_list = list(user_contacts) + list(college_contacts)

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

    try:
        sender_email = request.POST.get('sender_email')
        recipient_email = request.POST.get('recipient_email')
        message_content = request.POST.get('content')

        if not all([sender_email, recipient_email, message_content]):
            return JsonResponse({'status': 'false', 'message': 'Required fields missing'}, status=400)

        sender = get_object_or_404(User, email=sender_email)
        recipient = get_object_or_404(College, email=recipient_email)

        message = College_Message.objects.create(
            sender=sender,
            college_recipient=recipient,
            content=message_content
        )
		
        attachments = request.FILES.getlist('attachments', [])
        College_Attachment.objects.bulk_create([
            College_Attachment(message=message, file=file) for file in attachments
        ])
		
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
            [recipient.email],
            fail_silently=False,
        )

        return JsonResponse({'status': 'success', 'message': 'Message sent successfully!'}, status=201)

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500) 

@csrf_exempt
def clg_inbox(request):
    if request.method != "GET":
        return JsonResponse({'status': 'false', 'message': 'Invalid request method'}, status=405)

    try:
        email = request.GET.get('email')
        filter_value = request.GET.get('filter')

        if not email:
            return JsonResponse({'status': 'false', 'message': 'Email is required'}, status=400)

        messages_query = College_Message.objects.filter(
            Q(sender__email=email) | Q(college_recipient__email=email)
        ).order_by('-timestamp')

        if filter_value in ['read', 'unread']:
            is_read = filter_value == 'read'
            messages_query = messages_query.filter(is_read=is_read)

        message_list = [
            {
                'id': message.id,
                'sender': message.sender.email,
                'recipient': message.college_recipient.email,
                'content': message.content,
                'timestamp': message.timestamp,
                'is_read': message.is_read,
                'attachments': [
                    {
                        'id': attachment.id,
                        'file_url': attachment.file.url,
                        'uploaded_at': attachment.uploaded_at
                    }
                    for attachment in message.attachment.all()
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

    try:
        sender_email = request.GET.get('sender_email')
        recipient_email = request.GET.get('recipient_email')

        if not all([sender_email, recipient_email]):
            return JsonResponse({'status': 'false', 'message': 'Required fields missing'}, status=400)

        sender = get_object_or_404(User, email=sender_email)
        college_recipient = get_object_or_404(College, email=recipient_email)

        all_messages = College_Message.objects.filter(
            sender=sender,
            college_recipient=college_recipient
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
                'sender_email': message.sender.email,
                'recipient_email': message.college_recipient.email,
                'content': message.content,
                'timestamp': message.timestamp,
                'is_read': message.is_read,  
                'attachments': attachments_data
            })

        return JsonResponse({'status': 'success', 'messages': messages_data}, status=200)

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
