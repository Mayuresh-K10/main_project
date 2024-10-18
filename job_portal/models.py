from django.db import models # type: ignore
from django.utils import timezone # type: ignore
from django.contrib.auth.models import User

class Job(models.Model):
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
    card_number = models.CharField(max_length=20, blank=True, null=True, default='Not Provided') # Credit/Debit card number
    expiration_code = models.CharField(max_length=5, blank=True, null=True, default='MM/YY') # Expiration code (MM/YY)
    security_code = models.CharField(max_length=4, blank=True, null=True, default='000') # Security code
    country = models.CharField(max_length=100, blank=True, null=True, default='India') # Country
    postal_code = models.CharField(max_length=10, blank=True, null=True, default='000000') # Postal code
    gst = models.CharField(max_length=15, blank=True, null=True, default='Not Provided') # GST number
    promoting_job  =  models.BooleanField(default=False)
    first_name = models.CharField(max_length=255, null=False, default="John")
    last_name = models.CharField(max_length=255, null=False, default="Doe")

    def __str__(self):
        return self.job_title


class Application(models.Model):
    job = models.ForeignKey('Job', on_delete=models.CASCADE)
    student = models.ForeignKey('Student', on_delete=models.CASCADE,null=True, blank=True)
    first_name = models.CharField(max_length=255, null=False, default="John")
    last_name = models.CharField(max_length=255, null=False, default="Doe")
    email = models.EmailField(null=False, default="unknown@example.com")
    phone_number = models.CharField(max_length=15, default="123-456-7890")
    resume = models.FileField(upload_to='resumes/')
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
    resume = models.OneToOneField(Resume, related_name='objective', on_delete=models.CASCADE)
    text = models.TextField(default='Not specified')

class Education(models.Model):
    resume = models.ForeignKey(Resume, related_name='education_entries', on_delete=models.CASCADE, default=1)
    course_or_degree = models.CharField(max_length=100, default='Unknown')
    school_or_university = models.CharField(max_length=100, default='Unknown')
    grade_or_cgpa = models.CharField(max_length=50, default='N/A')
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    description = models.TextField(default='No description')

    def __str__(self):
        return f"{self.course_or_degree} at {self.school_or_university}"

class Experience(models.Model):
    resume = models.ForeignKey(Resume, related_name='experience_entries', on_delete=models.CASCADE,default=1)
    job_title = models.CharField(max_length=100, default='Unknown')
    company_name = models.CharField(max_length=100, default='Unknown')
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    description = models.TextField(default='No description')

    def __str__(self):
        return f"{self.job_title} at {self.company_name}"

class Project(models.Model):
    resume = models.ForeignKey(Resume, related_name='projects', on_delete=models.CASCADE)
    title = models.CharField(max_length=100, default='Untitled Project')
    description = models.TextField(default='No description')
    project_link = models.TextField(default=list)


    def __str__(self):
        return self.title

class Reference(models.Model):
    resume = models.ForeignKey(Resume, related_name='references', on_delete=models.CASCADE)
    name = models.CharField(max_length=100, default='Unknown')
    contact_info = models.CharField(max_length=100, default='Not provided')
    relationship = models.CharField(max_length=100, default='N/A')

    def __str__(self):
        return self.name

class Certification(models.Model):
   resume = models.ForeignKey(Resume, related_name='certifications', on_delete=models.CASCADE)
   name = models.CharField(max_length=100, default='Unknown')
   start_date = models.DateField(null=True, blank=True)
   end_date = models.DateField(null=True, blank=True)

class Achievements(models.Model):
    resume = models.ForeignKey(Resume, related_name='achievements', on_delete=models.CASCADE)
    title = models.CharField(max_length=100, default='Unknown')
    publisher = models.CharField(max_length=100, default='Unknown')
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

class Publications(models.Model):
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

class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sender', on_delete=models.CASCADE)
    company_recipient = models.ForeignKey(Company, related_name='recipient', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.sender.email} -> {self.company_recipient.email}"

    class Meta:
        ordering = ['timestamp']

class Attachment(models.Model):
    message = models.ForeignKey('Message', related_name='attachments', on_delete=models.CASCADE)
    file = models.FileField(upload_to='attachments/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Attachment for message {self.message.id}"

class Student(models.Model):
    # college = models.ForeignKey('College', on_delete=models.CASCADE)
    first_name =  models.CharField(max_length=100, default='John')
    last_name = models.CharField(max_length=100, default='Doe')
    email = models.EmailField(default='example@example.com')
    contact_no = models.CharField(max_length=20, default='000-000-0000')
    qualification = models.TextField(default='N/A')
    skills = models.TextField(default='Not specified')

class ScreeningQuestion(models.Model):
    job = models.ForeignKey(Job, related_name='screening_questions', on_delete=models.CASCADE)
    question_text = models.TextField()
    correct_answer = models.TextField()

    def __str__(self):
        return self.question_text[:50]

class ScreeningAnswer(models.Model):
    application = models.ForeignKey(Application, related_name='screening_answers', on_delete=models.CASCADE)
    question = models.ForeignKey(ScreeningQuestion, related_name='answers', on_delete=models.CASCADE)
    answer_text = models.TextField()

    def __str__(self):
        return f"Answer for {self.question.question_text[:50]}"

class MembershipPlan(models.Model):
    PLAN_CHOICES = [
        ('standard', 'Standard'),
        ('gold', 'Gold'),
        ('diamond', 'Diamond'),
    ]

    name = models.CharField(max_length=20, choices=PLAN_CHOICES, unique=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    job_postings = models.PositiveIntegerField(default=0)
    featured_jobs = models.PositiveIntegerField(default=0)
    job_duration_days = models.PositiveIntegerField(default=30)

    def __str__(self):
        return self.get_name_display()

class UserSubscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    current_plan = models.ForeignKey(MembershipPlan, on_delete=models.SET_NULL, null=True, blank=True)
    renewal_date = models.DateField(default=timezone.now)
    active = models.BooleanField(default=True)
    plan = models.CharField(max_length=15, default='Standard')

    def cancel_subscription(self):
        self.active = False
        self.save()

    def renew_subscription(self):
        if self.current_plan:
            self.renewal_date = timezone.now() + timezone.timedelta(days=30)
            self.save()

    def __str__(self):
        return f"{self.user.username} - {self.current_plan.name if self.current_plan else 'No Plan'}"

class Job1(models.Model):
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
    card_number = models.CharField(max_length=20, blank=True, null=True, default='Not Provided') # Credit/Debit card number
    expiration_code = models.CharField(max_length=5, blank=True, null=True, default='MM/YY') # Expiration code (MM/YY)
    security_code = models.CharField(max_length=4, blank=True, null=True, default='000') # Security code
    country = models.CharField(max_length=100, blank=True, null=True, default='India') # Country
    postal_code = models.CharField(max_length=10, blank=True, null=True, default='000000') # Postal code
    gst = models.CharField(max_length=15, blank=True, null=True, default='Not Provided') # GST number
    promoting_job  =  models.BooleanField(default=False)
    first_name = models.CharField(max_length=255, null=False, default="John")
    last_name = models.CharField(max_length=255, null=False, default="Doe")

    def __str__(self):
        return self.job_title

class Application1(models.Model):
    job = models.ForeignKey('Job1', on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255, null=False, default="John")
    last_name = models.CharField(max_length=255, null=False, default="Doe")
    email = models.EmailField(null=False, default="unknown@example.com")
    phone_number = models.CharField(max_length=15, default="123-456-7890")
    resume = models.FileField(upload_to='resumes/')
    cover_letter = models.TextField(default="No cover letter provided")
    applied_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=50, default='pending')
    skills = models.CharField(max_length=1000, blank= False, null=False)

    def __str__(self):
        return f"{self.first_name} - {self.job.job_title}"

class College(models.Model):
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
        ('pending', 'Pending'),
        ('reviewed', 'Reviewed'),
        ('resolved', 'Resolved'),
    ]

    college = models.ForeignKey(College, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    mobile_number = models.CharField(max_length=15)
    course = models.CharField(max_length=128, default='N/A')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Visitor(models.Model):
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name='visitors')
    first_name = models.CharField(max_length=255, null=False, default="John")
    last_name = models.CharField(max_length=255, null=False, default="Doe")
    email = models.EmailField(null=False, default="unknown@example.com")
    mobile_number = models.CharField(max_length=15, default="123-456-7890")
    password = models.CharField(max_length=128)

class StudentEnquiry(models.Model):
    STATUS_CHOICES = [
        ('replied', 'Replied'),
        ('not-replied', 'Not-Replied'),
    ]

    college = models.ForeignKey(College, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    mobile_number = models.CharField(max_length=15)
    course = models.CharField(max_length=128, default='N/A')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not-replied')


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
    student = models.ForeignKey(Student, on_delete=models.CASCADE) 



    def time_left(self):
        """Returns the time left until the interview, or None if in the past"""
        time_diff = self.interview_date - timezone.now()
        if time_diff.total_seconds() > 0:
            return time_diff
        return None

    def __str__(self):
        return f"{self.candidate_name} - {self.role.name} - {self.status}"
    
class College_Message(models.Model):
    sender = models.ForeignKey(User, related_name='user_sender', on_delete=models.CASCADE)
    college_recipient = models.ForeignKey(College ,related_name='clg_recipient', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.sender.email} -> {self.college_recipient.email}"

    class Meta:
        ordering = ['timestamp']

class College_Attachment(models.Model):
    message = models.ForeignKey(College_Message, related_name='attachment', on_delete=models.CASCADE)
    file = models.FileField(upload_to='attachments/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Attachment for message {self.message.id}"
