import uuid
from django.db import models # type: ignore
from django.utils import timezone # type: ignore
from login.models import CompanyInCharge, JobSeeker, UniversityInCharge, new_user

class Job(models.Model):
    unique_job_id = models.UUIDField(default=uuid.uuid1, unique=True, editable=False)
    unique_job_id_as_int = models.BigIntegerField(unique=True, editable=False, null=True)
    company_in_charge = models.ForeignKey(CompanyInCharge, on_delete=models.CASCADE)
    company = models.ForeignKey('Company', on_delete=models.CASCADE)
    description = models.TextField()
    requirements = models.TextField()
    published_at = models.DateTimeField(auto_now_add=True)
    experience_yr = models.CharField(max_length=10, default="0-100")
    job_title = models.CharField(max_length=200)
    job_type = models.CharField(max_length=50)
    experience = models.CharField(max_length=50)
    category =models.CharField(max_length=100)
    skills = models.CharField(max_length=1000, blank= False, null=False)
    workplaceTypes = models.CharField(max_length=50)
    location = models.CharField(max_length=100)
    questions = models.TextField(blank=True, null=True)
    job_status = models.CharField(max_length=50, default='active')
    email = models.EmailField(null=False, default="unknown@example.com")
    must_have_qualification = models.BooleanField(default=False)
    filter = models.BooleanField(default=False)
    source = models.CharField(max_length=50,default='LinkedIn')
    # card_number = models.CharField(max_length=20, blank=True, null=True, default='Not Provided') # Credit/Debit card number
    # expiration_code = models.CharField(max_length=5, blank=True, null=True, default='MM/YY') # Expiration code (MM/YY)
    # security_code = models.CharField(max_length=4, blank=True, null=True, default='000') # Security code
    # country = models.CharField(max_length=100, blank=True, null=True, default='India') # Country
    # postal_code = models.CharField(max_length=10, blank=True, null=True, default='000000') # Postal code
    # gst = models.CharField(max_length=15, blank=True, null=True, default='Not Provided') # GST number
    # promoting_job  =  models.BooleanField(default=False)
    # first_name = models.CharField(max_length=255, null=False, default="John")
    # last_name = models.CharField(max_length=255, null=False, default="Doe")

    def __str__(self):
        return self.job_title

    def save(self, *args, **kwargs):
     if not self.unique_job_id_as_int:
          self.unique_job_id_as_int = int(str(self.unique_job_id.int)[-16:])
     super().save(*args, **kwargs)


class Application(models.Model):
    company_in_charge = models.ForeignKey(CompanyInCharge, on_delete=models.CASCADE)
    user = models.ForeignKey(new_user, on_delete=models.CASCADE,null=True, blank=True)
    job_seeker = models.ForeignKey(JobSeeker, on_delete=models.CASCADE,null=True, blank=True)
    job = models.ForeignKey('Job', on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255, null=False, default="John")
    last_name = models.CharField(max_length=255, null=False, default="Doe")
    email = models.EmailField(null=False, default="unknown@example.com")
    phone_number = models.CharField(max_length=15, default="123-456-7890")
    resume = models.FileField(upload_to='resumes/',null=True, blank=True)
    cover_letter = models.TextField(default="No cover letter provided")
    applied_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=50, default='pending')
    skills = models.CharField(max_length=1000, blank= False, null=False)
    bio = models.TextField(blank=True, null=True)
    education = models.TextField(blank=True, null=True)
    experience = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} - {self.job.job_title}"

class Company(models.Model):
    company_in_charge = models.ForeignKey(CompanyInCharge, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    email = models.EmailField(default='example@example.com')
    phone = models.CharField(max_length=20, default='000-000-0000')
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default='India')
    zipcode = models.CharField(max_length=6, default='522426')
    website = models.URLField()
    website_urls = models.CharField(max_length=100, default='Unknown')
    about_company = models.CharField(max_length=255,default='about_company')
    sector_type = models.CharField(max_length=100)
    category = models.CharField(max_length=100, default='Unknown')
    established_date = models.DateField(null=True, blank=True)
    employee_size = models.IntegerField(default=0)
    Attachment = models.FileField(upload_to='attachments/',default='Unknown')
    is_deleted  = models.BooleanField(default=False)


    def _str_(self):
        return self.name

class Resume(models.Model):
    user = models.ForeignKey(new_user, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100, default='John')
    last_name = models.CharField(max_length=100, default='John Doe')
    email = models.EmailField(default='example@example.com')
    phone = models.CharField(max_length=20, default='000-000-0000')
    address = models.TextField(default='N/A')
    date_of_birth = models.DateField(null=True, blank=True)
    website_urls = models.JSONField(default=list)
    skills = models.TextField(default='Not specified')
    activities = models.TextField(default='None')
    interests = models.TextField(default='None')
    languages = models.TextField(default='None')
    bio = models.TextField(default='None')
    city = models.CharField(max_length=100, default='Mumbai')
    state = models.CharField(max_length=100, default='Maharashtra')
    country = models.CharField(max_length=100, default='India')
    zipcode = models.CharField(max_length=6, default='522426')
    Attachment = models.FileField(upload_to='attachments/',default='Unknown')
    delete = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Objective(models.Model):
    user = models.ForeignKey(new_user, on_delete=models.CASCADE)
    resume = models.OneToOneField(Resume, related_name='objective', on_delete=models.CASCADE)
    text = models.TextField(default='Not specified')

class Education(models.Model):
    user = models.ForeignKey(new_user, on_delete=models.CASCADE)
    resume = models.ForeignKey(Resume, related_name='education_entries', on_delete=models.CASCADE)
    course_or_degree = models.CharField(max_length=100, default='Unknown')
    school_or_university = models.CharField(max_length=100, default='Unknown')
    grade_or_cgpa = models.CharField(max_length=50, default='N/A')
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    description = models.TextField(default='No description')

    def __str__(self):
        return f"{self.course_or_degree} at {self.school_or_university}"

class Experience(models.Model):
    user = models.ForeignKey(new_user, on_delete=models.CASCADE)
    resume = models.ForeignKey(Resume, related_name='experience_entries', on_delete=models.CASCADE)
    job_title = models.CharField(max_length=100, default='Unknown')
    company_name = models.CharField(max_length=100, default='Unknown')
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    description = models.TextField(default='No description')

    def __str__(self):
        return f"{self.job_title} at {self.company_name}"

class Project(models.Model):
    user = models.ForeignKey(new_user, on_delete=models.CASCADE)
    resume = models.ForeignKey(Resume, related_name='projects', on_delete=models.CASCADE)
    title = models.CharField(max_length=100, default='Untitled Project')
    description = models.TextField(default='No description')
    project_link = models.TextField(default=list)


    def __str__(self):
        return self.title

class Reference(models.Model):
    user = models.ForeignKey(new_user, on_delete=models.CASCADE)
    resume = models.ForeignKey(Resume, related_name='references', on_delete=models.CASCADE)
    name = models.CharField(max_length=100, default='Unknown')
    contact_info = models.CharField(max_length=100, default='Not provided')
    relationship = models.CharField(max_length=100, default='N/A')

    def __str__(self):
        return self.name

class Certification(models.Model):
    user = models.ForeignKey(new_user, on_delete=models.CASCADE)
    resume = models.ForeignKey(Resume, related_name='certifications', on_delete=models.CASCADE)
    name = models.CharField(max_length=100, default='Unknown')
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

class Achievements(models.Model):
    user = models.ForeignKey(new_user, on_delete=models.CASCADE)
    resume = models.ForeignKey(Resume, related_name='achievements', on_delete=models.CASCADE)
    title = models.CharField(max_length=100, default='Unknown')
    publisher = models.CharField(max_length=100, default='Unknown')
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

class Publications(models.Model):
    user = models.ForeignKey(new_user, on_delete=models.CASCADE)
    resume = models.ForeignKey(Resume, related_name='publications', on_delete=models.CASCADE)
    title = models.CharField(max_length=100, default='Unknown')
    publisher = models.CharField(max_length=100, default='Unknown')
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

class CandidateStatus_selected(models.Model):
    first_name = models.CharField(max_length=255,default='John')
    last_name = models.CharField(max_length=255,default='Doe')
    status = models.CharField(max_length=20,default='selected')
    company_name = models.CharField(max_length=255)
    job_id = models.IntegerField()

class CandidateStatus_rejected(models.Model):
    first_name = models.CharField(max_length=255,default='John')
    last_name = models.CharField(max_length=255,default='Doe')
    status = models.CharField(max_length=20,default='rejected')
    company_name = models.CharField(max_length=255)
    job_id = models.IntegerField()

class CandidateStatus_not_eligible(models.Model):
    first_name = models.CharField(max_length=255,default='John')
    last_name = models.CharField(max_length=255,default='Doe')
    status = models.CharField(max_length=20,default='not_eligible')
    company_name = models.CharField(max_length=255)
    job_id = models.IntegerField()

class CandidateStatus_under_review(models.Model):
    first_name = models.CharField(max_length=255,default='John')
    last_name = models.CharField(max_length=255,default='Doe')
    status = models.CharField(max_length=20,default='under_review')
    company_name = models.CharField(max_length=255)
    job_id = models.IntegerField()

class Candidate1Status_selected(models.Model):
    first_name = models.CharField(max_length=255,default='John')
    last_name = models.CharField(max_length=255,default='Doe')
    status = models.CharField(max_length=20,default='selected')
    college_id = models.IntegerField()
    job_id = models.IntegerField()

class Candidate1Status_rejected(models.Model):
    first_name = models.CharField(max_length=255,default='John')
    last_name = models.CharField(max_length=255,default='Doe')
    status = models.CharField(max_length=20,default='rejected')
    college_id = models.IntegerField()
    job_id = models.IntegerField()

class Candidate1Status_not_eligible(models.Model):
    first_name = models.CharField(max_length=255,default='John')
    last_name = models.CharField(max_length=255,default='Doe')
    status = models.CharField(max_length=20,default='not_eligible')
    college_id = models.IntegerField()
    job_id = models.IntegerField()

class Candidate1Status_under_review(models.Model):
    first_name = models.CharField(max_length=255,default='John')
    last_name = models.CharField(max_length=255,default='Doe')
    status = models.CharField(max_length=20,default='under_review')
    college_id = models.IntegerField()
    job_id = models.IntegerField()

# class Message(models.Model):
#     company_in_charge = models.ForeignKey(CompanyInCharge, on_delete=models.CASCADE, null=True, blank=True)
#     receiptent_new_user = models.ForeignKey(new_user, on_delete=models.CASCADE, null=True, blank=True)
#     receiptent_job_seeker = models.ForeignKey(JobSeeker, on_delete=models.CASCADE, null=True, blank=True)
#     content = models.TextField()
#     timestamp = models.DateTimeField(auto_now_add=True)
#     is_read = models.BooleanField(default=False)

#     def __str__(self):
#         sender_email = (
#             self.company_in_charge.official_email if self.company_in_charge else
#             (self.receiptent_new_user.email if self.receiptent_new_user else
#             (self.receiptent_job_seeker.email if self.receiptent_job_seeker else "Unknown Sender"))
#         )
#         recipient_email = (
#             self.receiptent_new_user.email if self.receiptent_new_user else
#             (self.receiptent_job_seeker.email if self.receiptent_job_seeker else "Unknown Recipient")
#         )
#         return f"{sender_email} -> {recipient_email}"

#     class Meta:
#         ordering = ['timestamp']


# class Attachment(models.Model):
#     # user = models.ForeignKey(new_user, on_delete=models.CASCADE)
#     # job_seeker = models.ForeignKey(JobSeeker, on_delete=models.CASCADE)
#     # company_in_charge = models.ForeignKey(CompanyInCharge, on_delete=models.CASCADE)
#     message = models.ForeignKey(Message, related_name='attachments', on_delete=models.CASCADE)
#     file = models.FileField(upload_to='attachments/')
#     uploaded_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"Attachment for message {self.message.id}"

class Student(models.Model):
    user = models.ForeignKey(new_user, on_delete=models.CASCADE)
    # job_seeker = models.ForeignKey(JobSeeker, on_delete=models.CASCADE)
    first_name =  models.CharField(max_length=100, default='John')
    last_name = models.CharField(max_length=100, default='Doe')
    email = models.EmailField(default='example@example.com')
    contact_no = models.CharField(max_length=20, default='000-000-0000')
    qualification = models.TextField(default='N/A')
    skills = models.TextField(default='Not specified')

class CompanyScreeningQuestion(models.Model):
    company_in_charge = models.ForeignKey(CompanyInCharge, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, related_name='screening_questions', on_delete=models.CASCADE)
    question_text = models.TextField()
    correct_answer = models.TextField()

    def __str__(self):
        return self.question_text[:50]

class CompanyScreeningAnswer(models.Model):
    company_in_charge = models.ForeignKey(CompanyInCharge, on_delete=models.CASCADE)
    application = models.ForeignKey(Application, related_name='screening_answers', on_delete=models.CASCADE)
    question = models.ForeignKey(CompanyScreeningQuestion, related_name='answers', on_delete=models.CASCADE)
    answer_text = models.TextField()

    def __str__(self):
        return f"Answer for {self.question.question_text[:50]}"

class CollegeScreeningQuestion(models.Model):
    university_in_charge = models.ForeignKey(UniversityInCharge, on_delete=models.CASCADE)
    job = models.ForeignKey('Job1', related_name='screening_questions', on_delete=models.CASCADE)
    question_text = models.TextField()
    correct_answer = models.TextField()

    def __str__(self):
        return self.question_text[:50]

class CollegeScreeningAnswer(models.Model):
    university_in_charge = models.ForeignKey(UniversityInCharge, on_delete=models.CASCADE)
    application = models.ForeignKey('Application1', related_name='screening_answers', on_delete=models.CASCADE)
    question = models.ForeignKey(CollegeScreeningQuestion, related_name='answers', on_delete=models.CASCADE)
    answer_text = models.TextField()

    def __str__(self):
        return f"Answer for {self.question.question_text[:50]}"

# class MembershipPlan(models.Model):
#     PLAN_CHOICES = [
#         ('standard', 'Standard'),
#         ('gold', 'Gold'),
#         ('diamond', 'Diamond'),
#     ]

#     name = models.CharField(max_length=20, choices=PLAN_CHOICES, unique=True)
#     price = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
#     job_postings = models.PositiveIntegerField(default=0)
#     featured_jobs = models.PositiveIntegerField(default=0)
#     job_duration_days = models.PositiveIntegerField(default=30)

#     def __str__(self):
#         return self.get_name_display()

# class UserSubscription(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     current_plan = models.ForeignKey(MembershipPlan, on_delete=models.SET_NULL, null=True, blank=True)
#     renewal_date = models.DateField(default=timezone.now)
#     active = models.BooleanField(default=True)
#     plan = models.CharField(max_length=15, default='Standard')

#     def cancel_subscription(self):
#         self.active = False
#         self.save()

#     def renew_subscription(self):
#         if self.current_plan:
#             self.renewal_date = timezone.now() + timezone.timedelta(days=30)
#             self.save()

#     def __str__(self):
#         return f"{self.user.username} - {self.current_plan.name if self.current_plan else 'No Plan'}"

class Job1(models.Model):
    university_in_charge = models.ForeignKey(UniversityInCharge, on_delete=models.CASCADE)
    college = models.ForeignKey('College', on_delete=models.CASCADE)
    description = models.TextField()
    requirements = models.TextField()
    published_at = models.DateTimeField(auto_now_add=True)
    experience_yr = models.CharField(max_length=10, default="0-100")
    job_title = models.CharField(max_length=200)
    job_type = models.CharField(max_length=50)
    experience = models.CharField(max_length=50)
    category =models.CharField(max_length=100)
    skills = models.CharField(max_length=1000, blank= False, null=False)
    workplaceTypes = models.CharField(max_length=50)
    location = models.CharField(max_length=100)
    questions = models.TextField(blank=True, null=True)
    job_status = models.CharField(max_length=50, default='active')
    email = models.EmailField(null=False, default="unknown@example.com")
    must_have_qualification = models.BooleanField(default=False)
    filter = models.BooleanField(default=False)
    source = models.CharField(max_length=50,default='LinkedIn')
    # card_number = models.CharField(max_length=20, blank=True, null=True, default='Not Provided') # Credit/Debit card number
    # expiration_code = models.CharField(max_length=5, blank=True, null=True, default='MM/YY') # Expiration code (MM/YY)
    # security_code = models.CharField(max_length=4, blank=True, null=True, default='000') # Security code
    # country = models.CharField(max_length=100, blank=True, null=True, default='India') # Country
    # postal_code = models.CharField(max_length=10, blank=True, null=True, default='000000') # Postal code
    # gst = models.CharField(max_length=15, blank=True, null=True, default='Not Provided') # GST number
    # promoting_job  =  models.BooleanField(default=False)
    # first_name = models.CharField(max_length=255, null=False, default="John")
    # last_name = models.CharField(max_length=255, null=False, default="Doe")

    def __str__(self):
        return self.job_title

    class Meta:
        db_table = 'job1'  # Custom table name for Job1

class Application1(models.Model):
    university_in_charge = models.ForeignKey(UniversityInCharge, on_delete=models.CASCADE)
    user = models.ForeignKey(new_user, on_delete=models.CASCADE,null=True, blank=True)
    job_seeker = models.ForeignKey(JobSeeker, on_delete=models.CASCADE,null=True, blank=True)
    job = models.ForeignKey('Job1', on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255, null=False, default="John")
    last_name = models.CharField(max_length=255, null=False, default="Doe")
    email = models.EmailField(null=False, default="unknown@example.com")
    phone_number = models.CharField(max_length=15, default="123-456-7890")
    resume = models.FileField(upload_to='resumes/',null=True, blank=True)
    cover_letter = models.TextField(default="No cover letter provided")
    applied_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=50, default='pending')
    skills = models.CharField(max_length=1000, blank= False, null=False)
    bio = models.TextField(blank=True, null=True)
    education = models.TextField(blank=True, null=True)
    experience = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} - {self.job.job_title}"

class College(models.Model):
    university_in_charge = models.ForeignKey(UniversityInCharge, on_delete=models.CASCADE)
    college_name = models.CharField(max_length=255)
    email = models.EmailField(default='example@example.com')
    website = models.URLField()
    phone = models.CharField(max_length=20, default='000-000-0000')
    founded_date = models.DateField(null=True, blank=True)
    university_type = models.CharField(max_length=100, default='Unknown')
    about_college = models.CharField(max_length=255,default='about_college')
    website_urls = models.CharField(max_length=100, default='Unknown')
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default='India')
    zipcode = models.CharField(max_length=6, default='522426')
    Attachment = models.FileField(upload_to='attachments/',default='Unknown')
    is_deleted  = models.BooleanField(default=False)

class CollegeEnquiry(models.Model):
    STATUS_CHOICES = [
       ('replied', 'Replied'),
       ('not-replied', 'Not-Replied'),
    ]
    college = models.ForeignKey(College, on_delete=models.CASCADE)
    new_user = models.ForeignKey(new_user, on_delete=models.CASCADE,null=True, blank=True )
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    mobile_number = models.CharField(max_length=15)
    course = models.CharField(max_length=128, default='N/A')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not-replied')
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Visitor(models.Model):
    university_in_charge = models.ForeignKey(UniversityInCharge, on_delete=models.CASCADE)
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name='visitors')
    first_name = models.CharField(max_length=255, null=False, default="John")
    last_name = models.CharField(max_length=255, null=False, default="Doe")
    email = models.EmailField(null=False, default="unknown@example.com")
    mobile_number = models.CharField(max_length=15, default="123-456-7890")
    password = models.CharField(max_length=128)
    visited_at = models.DateTimeField(default=timezone.now)

class StudentEnquiry(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('reviewed', 'Reviewed'),
        ('resolved', 'Resolved'),
    ]
    university_in_charge = models.ForeignKey(UniversityInCharge, on_delete=models.CASCADE)
    college = models.ForeignKey(College, on_delete=models.CASCADE)
    new_user = models.ForeignKey(new_user, on_delete=models.CASCADE,null=True, blank=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    mobile_number = models.CharField(max_length=15)
    course = models.CharField(max_length=128, default='N/A')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(default=timezone.now)


    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Interview(models.Model):
    ROLE_CHOICES = [
        ('Software Engineer', 'Software Engineer'),
        ('UI/UX Designer', 'UI/UX Designer'),
        ('Backend Developer', 'Backend Developer'),
        ('Frontend Developer', 'Frontend Developer'),
        ('DevOps Engineer', 'DevOps Engineer'),
        ('Data Scientist', 'Data Scientist'),
        ('Machine Learning Engineer', 'Machine Learning Engineer'),
        ('Product Manager', 'Product Manager'),
        ('QA Engineer', 'QA Engineer'),
        ('Mobile App Developer', 'Mobile App Developer'),
    ]

    ROUND_CHOICES = [
        ('Technical Round 1', 'Technical Round 1'),
        ('Technical Round 2', 'Technical Round 2'),
        ('HR Round', 'HR Round'),
    ]

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Selected', 'Selected'),
        ('Rejected', 'Rejected'),
    ]

    candidate_name = models.CharField(max_length=100)
    interview_date = models.DateTimeField()
    round = models.CharField(max_length=50, choices=ROUND_CHOICES)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')
    applicant = models.ForeignKey(Application, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    user = models.ForeignKey(new_user, on_delete=models.CASCADE,null=True, blank=True)
    job_seeker = models.ForeignKey(JobSeeker, on_delete=models.CASCADE,null=True, blank=True)
    company_in_charge = models.ForeignKey(CompanyInCharge, on_delete=models.CASCADE,null=True, blank=True)

    def time_left(self):
        """Returns the time left until the interview, or None if in the past"""
        time_diff = self.interview_date - timezone.now()
        if time_diff.total_seconds() > 0:
            return time_diff
        return None

    def __str__(self):
        return f"{self.candidate_name} - {self.role.name} - {self.status}"

# class College_Message(models.Model):
#     university_in_charge = models.ForeignKey(UniversityInCharge, on_delete=models.CASCADE,null=True, blank=True,)
#     receiptent_new_user = models.ForeignKey(new_user, on_delete=models.CASCADE,null=True, blank=True)
#     receiptent_job_seeker  = models.ForeignKey(JobSeeker, on_delete=models.CASCADE,null=True, blank=True)
#     content = models.TextField()
#     timestamp = models.DateTimeField(auto_now_add=True)
#     is_read = models.BooleanField(default=False)

#     def __str__(self):
#         sender_email = self.university_in_charge.official_email if self.university_in_charge else "Unknown Sender"
#         recipient_email = (
#             self.receiptent_new_user.email if self.receiptent_new_user else
#             (self.receiptent_job_seeker.email if self.receiptent_job_seeker else "Unknown Recipient")
#         )
#         return f"{sender_email} -> {recipient_email}"

#     class Meta:
#         ordering = ['timestamp']

# class College_Attachment(models.Model):
#     # university_in_charge = models.ForeignKey(UniversityInCharge, on_delete=models.CASCADE)
#     message = models.ForeignKey(College_Message, related_name='attachment', on_delete=models.CASCADE)
#     file = models.FileField(upload_to='attachments/')
#     uploaded_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"Attachment for message {self.message.id}"

class JobSeeker_Resume(models.Model):
    job_seeker = models.ForeignKey(JobSeeker, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100, default='John')
    last_name = models.CharField(max_length=100, default='John Doe')
    email = models.EmailField(default='example@example.com')
    phone = models.CharField(max_length=20, default='000-000-0000')
    address = models.TextField(default='N/A')
    date_of_birth = models.DateField(null=True, blank=True)
    website_urls = models.JSONField(default=list)
    skills = models.TextField(default='Not specified')
    activities = models.TextField(default='None')
    interests = models.TextField(default='None')
    languages = models.TextField(default='None')
    bio = models.TextField(default='None')
    city = models.CharField(max_length=100, default='Mumbai')
    state = models.CharField(max_length=100, default='Maharashtra')
    country = models.CharField(max_length=100, default='India')
    zipcode = models.CharField(max_length=6, default='522426')
    Attachment = models.FileField(upload_to='attachments/',default='Unknown')
    delete = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class JobSeeker_Objective(models.Model):
    job_seeker = models.ForeignKey(JobSeeker, on_delete=models.CASCADE)
    resume = models.OneToOneField(JobSeeker_Resume, related_name='objective', on_delete=models.CASCADE)
    text = models.TextField(default='Not specified')

class JobSeeker_Education(models.Model):
    job_seeker = models.ForeignKey(JobSeeker, on_delete=models.CASCADE)
    resume = models.ForeignKey(JobSeeker_Resume, related_name='education_entries', on_delete=models.CASCADE)
    course_or_degree = models.CharField(max_length=100, default='Unknown')
    school_or_university = models.CharField(max_length=100, default='Unknown')
    grade_or_cgpa = models.CharField(max_length=50, default='N/A')
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    description = models.TextField(default='No description')

    def __str__(self):
        return f"{self.course_or_degree} at {self.school_or_university}"

class JobSeeker_Experience(models.Model):
    job_seeker = models.ForeignKey(JobSeeker, on_delete=models.CASCADE)
    resume = models.ForeignKey(JobSeeker_Resume, related_name='experience_entries', on_delete=models.CASCADE)
    job_title = models.CharField(max_length=100, default='Unknown')
    company_name = models.CharField(max_length=100, default='Unknown')
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    description = models.TextField(default='No description')

    def __str__(self):
        return f"{self.job_title} at {self.company_name}"

class JobSeeker_Project(models.Model):
    job_seeker = models.ForeignKey(JobSeeker, on_delete=models.CASCADE)
    resume = models.ForeignKey(JobSeeker_Resume, related_name='projects', on_delete=models.CASCADE)
    title = models.CharField(max_length=100, default='Untitled Project')
    description = models.TextField(default='No description')
    project_link = models.TextField(default=list)


    def __str__(self):
        return self.title

class JobSeeker_Reference(models.Model):
    job_seeker = models.ForeignKey(JobSeeker, on_delete=models.CASCADE)
    resume = models.ForeignKey(JobSeeker_Resume, related_name='references', on_delete=models.CASCADE)
    name = models.CharField(max_length=100, default='Unknown')
    contact_info = models.CharField(max_length=100, default='Not provided')
    relationship = models.CharField(max_length=100, default='N/A')

    def __str__(self):
        return self.name

class JobSeeker_Certification(models.Model):
    job_seeker = models.ForeignKey(JobSeeker, on_delete=models.CASCADE)
    resume = models.ForeignKey(JobSeeker_Resume, related_name='certifications', on_delete=models.CASCADE)
    name = models.CharField(max_length=100, default='Unknown')
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

class JobSeeker_Achievements(models.Model):
    job_seeker = models.ForeignKey(JobSeeker, on_delete=models.CASCADE)
    resume = models.ForeignKey(JobSeeker_Resume, related_name='achievements', on_delete=models.CASCADE)
    title = models.CharField(max_length=100, default='Unknown')
    publisher = models.CharField(max_length=100, default='Unknown')
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

class JobSeeker_Publications(models.Model):
    job_seeker = models.ForeignKey(JobSeeker, on_delete=models.CASCADE)
    resume = models.ForeignKey(JobSeeker_Resume, related_name='publications', on_delete=models.CASCADE)
    title = models.CharField(max_length=100, default='Unknown')
    publisher = models.CharField(max_length=100, default='Unknown')
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

class Membership(models.Model):
    company_in_charge = models.ForeignKey(CompanyInCharge, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    mobile = models.CharField(max_length=15)
    course_to_purchase = models.CharField(max_length=100)
    quantity_of_leads = models.IntegerField()
    location_for_leads = models.CharField(max_length=100)
    intake_year = models.IntegerField()

    def __str__(self):
        return self.name

class  CollegeMembership(models.Model):
    university_in_charge = models.ForeignKey(UniversityInCharge, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    mobile = models.CharField(max_length=15)
    course_to_purchase = models.CharField(max_length=100)
    quantity_of_leads = models.IntegerField()
    location_for_leads = models.CharField(max_length=100)
    intake_year = models.IntegerField()

    def __str__(self):
        return self.name

class Advertisement(models.Model):
    company_in_charge = models.ForeignKey(CompanyInCharge, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    contact = models.CharField(max_length=15)
    advertisement_placement = models.CharField(max_length=100)
    time_duration = models.CharField(max_length=50)
    investment_cost = models.DecimalField(max_digits=10, decimal_places=2)
    target_audience = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class CollegeAdvertisement(models.Model):
    university_in_charge = models.ForeignKey(UniversityInCharge, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    contact = models.CharField(max_length=15)
    advertisement_placement = models.CharField(max_length=100)
    time_duration = models.CharField(max_length=50)
    investment_cost = models.DecimalField(max_digits=10, decimal_places=2)
    target_audience = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
class Messages(models.Model):
    student = models.ForeignKey(new_user, on_delete=models.CASCADE, null=True, blank=True)
    candidate = models.ForeignKey(JobSeeker, on_delete=models.CASCADE, null=True, blank=True)
    company = models.ForeignKey(CompanyInCharge, on_delete=models.CASCADE, null=True, blank=True)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    recipient_student = models.ForeignKey(new_user, on_delete=models.CASCADE, null=True, blank=True, related_name='received_messages')
    recipient_candidate = models.ForeignKey(JobSeeker, on_delete=models.CASCADE, null=True, blank=True, related_name='received_messages')
    recipient_company = models.ForeignKey(CompanyInCharge, on_delete=models.CASCADE, null=True, blank=True, related_name='received_messages')

    class Meta:
        ordering = ['timestamp']

class Attachment(models.Model):
    message = models.ForeignKey(Messages, related_name='attachments', on_delete=models.CASCADE)
    file = models.FileField(upload_to='attachments/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Attachment for message {self.message.id}"

class Messages1(models.Model):
    student = models.ForeignKey(new_user, on_delete=models.CASCADE, null=True, blank=True)
    candidate = models.ForeignKey(JobSeeker, on_delete=models.CASCADE, null=True, blank=True)
    college = models.ForeignKey(UniversityInCharge, on_delete=models.CASCADE, null=True, blank=True)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    recipient_student = models.ForeignKey(new_user, on_delete=models.CASCADE, null=True, blank=True, related_name='user_received_messages')
    recipient_candidate = models.ForeignKey(JobSeeker, on_delete=models.CASCADE, null=True, blank=True, related_name='jobseeker_received_messages')
    recipient_college = models.ForeignKey(UniversityInCharge, on_delete=models.CASCADE, null=True, blank=True, related_name='college_received_messages')


    class Meta:
        ordering = ['timestamp']


class Attachment1(models.Model):
    message = models.ForeignKey(Messages1, related_name='attachments', on_delete=models.CASCADE)
    file = models.FileField(upload_to='attachments/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Attachment for message {self.message.id}"    

