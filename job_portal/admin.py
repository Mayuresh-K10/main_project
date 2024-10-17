from django.contrib import admin # type: ignore
from .models import  Achievements, Application, CandidateStatus_rejected, CandidateStatus_under_review, Certification, College, CollegeEnquiry, Job, Company, CandidateStatus_selected, CandidateStatus_not_eligible, MembershipPlan, Publications, Resume, Project, Objective, Experience, Education, Reference, Application1, Job1, ScreeningAnswer, StudentEnquiry, UserSubscription, ScreeningQuestion, Student, Attachment, Message, Visitor, Interview

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
admin.site.register(MembershipPlan)
admin.site.register(College)
admin.site.register(CollegeEnquiry)
admin.site.register(Application1)
admin.site.register(Visitor)
admin.site.register(Job1)
admin.site.register(UserSubscription)
admin.site.register(ScreeningQuestion)
admin.site.register(ScreeningAnswer)
admin.site.register(Message)
admin.site.register(Attachment)
admin.site.register(Student)
admin.site.register(StudentEnquiry)
admin.site.register(Interview)








