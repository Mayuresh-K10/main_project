# from django.db import models
# from django.contrib.auth.models import User
# from django.utils import timezone

# class Exam(models.Model):
#     name = models.CharField(max_length=200)
#     date = models.DateTimeField()

# class ProctoringSession(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
#     start_time = models.DateTimeField(default=timezone.now)
#     end_time = models.DateTimeField(null=True, blank=True)
#     duration = models.DurationField(default=timezone.timedelta(hours=3))
#     STATUS_CHOICES = [
#         ('ongoing', 'ongoing'),
#         ('completed', 'completed'),
#     ]
#     status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='ongoing')

# class ProctoringEvent(models.Model):
#     session = models.ForeignKey(ProctoringSession, on_delete=models.CASCADE)
#     event_type = models.CharField(max_length=100)
#     timestamp = models.DateTimeField(auto_now_add=True)
#     details = models.TextField(null=True, blank=True)

# class Question(models.Model):
#     exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='questions')
#     question_no = models.IntegerField(unique=True)
#     question_text = models.TextField(default="Default question text")
#     option1 = models.CharField(max_length=255)
#     option2 = models.CharField(max_length=255)
#     option3 = models.CharField(max_length=255)
#     option4 = models.CharField(max_length=255)
#     correct_option = models.CharField(max_length=255,default='option1')
#     section = models.CharField(max_length=50)
#     status = models.CharField(max_length=50)
#     duration = models.DurationField(default=timezone.timedelta(hours=3))

# class UserResponse(models.Model):
#     user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
#     question = models.ForeignKey(Question, on_delete=models.CASCADE)
#     response = models.TextField()
#     start_time = models.DateTimeField(default=timezone.now)
#     end_time = models.DateTimeField(null=True, blank=True)
#     session = models.ForeignKey(ProctoringSession, on_delete=models.CASCADE)
#     marked_for_review = models.BooleanField(default=False)
#     selected_option = models.CharField(max_length=255,default='option1')
#     response_time = models.DateTimeField(default=timezone.now)


# class UserScore(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
#     score = models.IntegerField(default=0)

# class ExamParticipant(models.Model):
#     name = models.CharField(max_length=255)
#     email = models.EmailField(unique=True)
#     phone_number = models.CharField(max_length=15)
#     exam_started = models.BooleanField(default=False)

#     # def __str__(self):
#     #     return self.name

# models.py
from django.db import models

from login.models import CompanyInCharge,UniversityInCharge

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
