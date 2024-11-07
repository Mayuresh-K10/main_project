from django.urls import path
from . import views

urlpatterns = [
    path('start-proctoring-session/', views.StartProctoringSessionView.as_view(), name='start_proctoring_session'),
    path('end-proctoring-session/', views.EndProctoringSessionView.as_view(), name='end_proctoring_session'),
    path('record-proctoring-event/', views.RecordProctoringEventView.as_view(), name='record_proctoring_event'),
    path('count-questions/<int:exam_id>/', views.count_questions, name='count_questions'),
    path('event-types/', views.fetch_event_types, name='event-types'),
    path('section-types/', views.fetch_section_types, name='section-types'),
    path('status-types/', views.fetch_status_types, name='status-types'),
    path('session-status-types/', views.StatusTypeChoicesAPIView.as_view(), name='session-status-types'),
    path('submit-answer/', views.submit_answer, name='submit_answer'),
    path('mark-for-review/', views.mark_for_review, name='mark_for_review'),
    path('session-status/<int:session_id>/', views.get_session_status, name='get_session_status'),
    path('question/<int:session_id>/<int:question_no>/', views.get_question_details, name='get_question_details'),
    path('get-details/', views.get_details, name='get_details'),
    path('submit-all-answers/', views.submit_all_answers, name='submit_all_answers'),
    path('question/next/<int:session_id>/<int:current_question_no>/', views.get_next_question, name='get_next_question'),
    path('question/previous/<int:session_id>/<int:current_question_no>/', views.get_previous_question, name='get_previous_question'),
    path('submit-details/', views.submit_details, name='submit_details'),
    path('Student-notifications/', views.get_notifications, name='get_notifications'),
    path('Student-notifications/read/<int:notification_id>/', views.mark_as_read, name='mark_as_read'),
    path('Student-notifications/create/', views.create_notification, name='create_notification'),
    path('jobseeker-notifications/', views.get_notifications1, name='get_notifications1'),
    path('jobseeker-notifications/read/<int:notification_id>/', views.mark_as_read1, name='mark_as_read1'),
    path('jobseeker-notifications/create/', views.create_notification1, name='create_notification1'),
    path('College-notifications/', views.get_notifications2, name='get_notifications2'),
    path('College-notifications/read/<int:notification_id>/', views.mark_as_read2, name='mark_as_read2'),
    path('College-notifications/create/', views.create_notification2, name='create_notification2'),
    path('Company-notifications/', views.get_notifications3, name='get_notifications3'),
    path('Company-notifications/read/<int:notification_id>/', views.mark_as_read3, name='mark_as_read3'),
    path('Company-notifications/create/', views.create_notification3, name='create_notification3'),
]
 
 #k