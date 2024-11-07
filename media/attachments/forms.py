# from django import forms
# from .models import ExamParticipant, ProctoringEvent

# class StartProctoringSessionForm(forms.Form):
#     exam_id = forms.IntegerField()
#     duration = forms.DurationField(required=False, help_text="Duration of the session (e.g., '1:30:00' for 1 hour 30 minutes)")

# class EndProctoringSessionForm(forms.Form):
#     session_id = forms.IntegerField()

# class RecordProctoringEventForm(forms.ModelForm):
#     session_id = forms.IntegerField()

#     class Meta:
#         model = ProctoringEvent
#         fields = ['event_type', 'details', 'session_id']

# class SubmitAnswerForm(forms.Form):
#     session_id = forms.IntegerField()
#     question_no = forms.IntegerField()
#     selected_option = forms.CharField(max_length=255)
#     clear_response = forms.BooleanField(required=False)

# class MarkForReviewForm(forms.Form):
#     session_id = forms.IntegerField()
#     question_no = forms.IntegerField()
#     mark = forms.BooleanField()


# class SubmitAllAnswersForm(forms.Form):
#     session_id = forms.IntegerField()
#     answers = forms.JSONField()

# class ExamParticipantForm(forms.ModelForm):
#     class Meta:
#         model = ExamParticipant
#         fields = ['name', 'email', 'phone_number']

# forms.py
from django import forms
from .models import Membership,CollegeMembership,Advertisement,CollegeAdvertisement

class MembershipForm(forms.ModelForm):
    class Meta:
        model = Membership
        fields = ['name', 'email', 'mobile', 'course_to_purchase', 'quantity_of_leads', 'location_for_leads', 'intake_year']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Enter your name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Enter your email'}),
            'mobile': forms.TextInput(attrs={'placeholder': 'Enter your mobile number'}),
            'course_to_purchase': forms.TextInput(attrs={'placeholder': 'Enter course name'}),
            'quantity_of_leads': forms.NumberInput(attrs={'placeholder': 'Enter quantity'}),
            'location_for_leads': forms.TextInput(attrs={'placeholder': 'Enter location'}),
            'intake_year': forms.NumberInput(attrs={'placeholder': 'Enter intake year'}),
        }



class MembershipForm1(forms.ModelForm):
    class Meta:
        model = CollegeMembership
        fields = ['name', 'email', 'mobile', 'course_to_purchase', 'quantity_of_leads', 'location_for_leads', 'intake_year']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Enter your name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Enter your email'}),
            'mobile': forms.TextInput(attrs={'placeholder': 'Enter your mobile number'}),
            'course_to_purchase': forms.TextInput(attrs={'placeholder': 'Enter course name'}),
            'quantity_of_leads': forms.NumberInput(attrs={'placeholder': 'Enter quantity'}),
            'location_for_leads': forms.TextInput(attrs={'placeholder': 'Enter location'}),
            'intake_year': forms.NumberInput(attrs={'placeholder': 'Enter intake year'}),
        }


class AdvertisementForm(forms.ModelForm):
    class Meta:
        model = Advertisement
        fields = ['name', 'email', 'contact', 'advertisement_placement', 'time_duration', 'investment_cost', 'target_audience']


class AdvertisementForm1(forms.ModelForm):
    class Meta:
        model = CollegeAdvertisement
        fields = ['name', 'email', 'contact', 'advertisement_placement', 'time_duration', 'investment_cost', 'target_audience']
