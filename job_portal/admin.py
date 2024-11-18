from django.contrib import admin # type: ignore
from .models import  Achievements, Application, CandidateStatus_rejected, CandidateStatus_under_review, CompanyScreeningAnswer, CompanyScreeningQuestion,  Education,  Certification, College, CollegeEnquiry, Job, Company, CandidateStatus_selected, CandidateStatus_not_eligible, Publications, Resume, Project, Objective, Experience, Reference, Application1, Job1, StudentEnquiry, Student, Visitor, Interview, Messages, Messages1, Attachment, Attachment1, JobSeeker_Resume, JobSeeker_Objective, JobSeeker_Certification, JobSeeker_Education, JobSeeker_Experience, JobSeeker_Achievements, JobSeeker_Project, JobSeeker_Publications, JobSeeker_Reference, Membership, CollegeMembership, Advertisement, CollegeAdvertisement

admin.site.register(Job)
admin.site.register(Application)
admin.site.register(Company)
admin.site.register(CandidateStatus_selected)
admin.site.register(CandidateStatus_rejected)
admin.site.register(CandidateStatus_not_eligible)
admin.site.register(CandidateStatus_under_review)
admin.site.register(Resume)
admin.site.register(Project)
admin.site.register(Reference)
admin.site.register(Publications)
admin.site.register(Experience)
admin.site.register(Education)
admin.site.register(Achievements)
admin.site.register(Certification)
admin.site.register(Objective)
admin.site.register(College)
admin.site.register(CollegeEnquiry)
admin.site.register(Application1)
admin.site.register(Visitor)
admin.site.register(Job1)
admin.site.register(CompanyScreeningQuestion)
admin.site.register(CompanyScreeningAnswer)
admin.site.register(Student)
admin.site.register(StudentEnquiry)
admin.site.register(Interview)
admin.site.register(Messages)
admin.site.register(Messages1)
admin.site.register(Attachment)
admin.site.register(Attachment1)
admin.site.register(JobSeeker_Resume)
admin.site.register(JobSeeker_Objective)
admin.site.register(JobSeeker_Reference)
admin.site.register(JobSeeker_Achievements)
admin.site.register(JobSeeker_Certification)
admin.site.register(JobSeeker_Project)
admin.site.register(JobSeeker_Publications)
admin.site.register(JobSeeker_Education)
admin.site.register(JobSeeker_Experience)
admin.site.register(Membership)
admin.site.register(CollegeMembership)
admin.site.register(Advertisement)
admin.site.register(CollegeAdvertisement)







