# import json
# from django.shortcuts import get_object_or_404 # type: ignore
# from django.http import JsonResponse # type: ignore
# from django.utils import timezone # type: ignore
# # from django.contrib.auth.decorators import login_required # type: ignore
# from django.views.decorators.csrf import csrf_exempt # type: ignore
# from django.views.decorators.http import require_POST, require_GET # type: ignore
# from .models import ProctoringEvent, ProctoringSession, Exam, Question, UserResponse, UserScore
# from .forms import ExamParticipantForm, MarkForReviewForm, StartProctoringSessionForm, EndProctoringSessionForm, RecordProctoringEventForm, SubmitAllAnswersForm, SubmitAnswerForm
# from django.contrib.auth import authenticate, login as auth_login # type: ignore
# from django.core.mail import send_mail # type: ignore
# from django.conf import settings # type: ignore
# from rest_framework.views import APIView

# def api_response(success, data=None, error=None, details=None, status=200):
#     try:
#         response = {'success': success}
#         if data:
#             response['data'] = data
#         if error:
#             response['error'] = error
#         if details:
#             response['details'] = details
#         return JsonResponse(response, status=status)
#     except Exception as e:
#         return JsonResponse({'success': False, 'error': str(e)}, status=500)

# @csrf_exempt
# @require_POST
# def custom_login(request):
#     try:
#         username = request.POST.get('username')
#         password = request.POST.get('password')

#         if not username or not password:
#             return api_response(success=False, error='Username and password are required', status=400)

#         user = authenticate(request, username=username, password=password)

#         if user:
#             auth_login(request, user)
#             return api_response(success=True, data={'message': 'Login successful'})

#         return api_response(success=False, error='Invalid credentials', status=400)

#     except Exception as e:
#         return api_response(success=False, error='An error occurred during login',
#                             details=str(e), status=500)

# # @login_required
# @require_POST
# @csrf_exempt
# def start_proctoring_session(request):
#     try:
#         form = StartProctoringSessionForm(request.POST)

#         if not form.is_valid():
#             return api_response(success=False, error='Invalid data', status=400)

#         exam_id = form.cleaned_data['exam_id']
#         exam = get_object_or_404(Exam, id=exam_id)

#         if ProctoringSession.objects.filter(user=request.user, exam=exam).exists():
#             return api_response(success=False, error='Proctoring session for this exam already exists', status=400)

#         session = ProctoringSession.objects.create(
#             user=request.user,
#             exam=exam,
#             start_time=timezone.now(),
#             status='ongoing'
#         )

#         user_email = request.user.email
#         try:
#             send_mail(
#                 "Proctoring Event Notification",
#                 "Session started",
#                 settings.EMAIL_HOST_USER,
#                 [user_email]
#             )
#         except Exception as email_error:
#             return api_response(success=True, data={'session_id': session.id},
#                                 error='Failed to send email notification',
#                                 details=str(email_error), status=500)

#         return api_response(success=True, data={'session_id': session.id})

#     except Exception as e:
#         return api_response(success=False, error='An error occurred while starting the session',
#                             details=str(e), status=500)

# # @login_required
# @require_POST
# @csrf_exempt
# def end_proctoring_session(request):
#     try:
#         form = EndProctoringSessionForm(request.POST)

#         if not form.is_valid():
#             return api_response(success=False, error='Invalid data', status=400)

#         session_id = form.cleaned_data['session_id']
#         session = get_object_or_404(ProctoringSession, id=session_id)

#         session.end_time = timezone.now()
#         session.status = 'completed'
#         session.save()

#         user_email = request.user.email
#         try:
#             send_mail(
#                 "Proctoring Event Notification",
#                 "Session ended",
#                 settings.EMAIL_HOST_USER,
#                 [user_email]
#             )
#         except Exception as email_error:
#             return api_response(success=True, data={'status': 'completed'},
#                                 error=f'Failed to send email to {user_email}',
#                                 details=str(email_error), status=500)

#         return api_response(success=True, data={'status': 'completed'})

#     except Exception as e:
#         return api_response(success=False, error='An error occurred while ending the session',
#                             details=str(e), status=500)

# # @login_required
# @require_POST
# @csrf_exempt
# def record_proctoring_event(request):
#     try:
#         form = RecordProctoringEventForm(request.POST)

#         if not form.is_valid():
#             return api_response(success=False, error='Invalid data', status=400)

#         session_id = form.cleaned_data['session_id']
#         session = get_object_or_404(ProctoringSession, id=session_id)

#         if ProctoringEvent.objects.filter(session=session).exists():
#             return api_response(success=False, error='Event for this session already recorded', status=400)

#         event = form.save(commit=False)
#         event.session = session
#         event.save()

#         user_email = request.user.email
#         try:
#             send_mail(
#                 "Proctoring Event Notification",
#                 "Event recorded",
#                 settings.EMAIL_HOST_USER,
#                 [user_email]
#             )
#         except Exception as email_error:
#             return api_response(success=True, data={'status': 'event recorded'},
#                                 error='Failed to send email notification',
#                                 details=str(email_error), status=500)

#         return api_response(success=True, data={'status': 'event recorded'})

#     except Exception as e:
#         return api_response(success=False, error='An error occurred while recording the event',
#                                 details=str(e), status=500)

# @csrf_exempt
# @require_POST
# # @login_required
# def submit_answer(request):
#     try:
#         form = SubmitAnswerForm(request.POST)
#         if not form.is_valid():
#             return api_response(success=False, error='Invalid data', status=400)

#         session_id = form.cleaned_data['session_id']
#         session = get_object_or_404(ProctoringSession.objects.only('id', 'exam'), id=session_id)

#         question_no = form.cleaned_data['question_no']
#         selected_option = form.cleaned_data['selected_option']
#         clear_response = form.cleaned_data['clear_response']

#         question = get_object_or_404(Question.objects.only('id', 'status', 'correct_option'), exam=session.exam, question_no=question_no)

#         user_response = UserResponse.objects.filter(user=request.user, question=question, session=session).first()

#         if clear_response:
#             if user_response:
#                 if user_response.selected_option == question.correct_option:
#                     user_score, _ = UserScore.objects.get_or_create(user=request.user, exam=session.exam)
#                     if user_score.score > 0:
#                         user_score.score -= 1
#                         user_score.save(update_fields=['score'])

#                 user_response.delete()
#             return api_response(success=True, data={'message': 'Response cleared and score updated.'})

#         if user_response:
#             return api_response(success=False, error='Answer already submitted', status=400)

#         UserResponse.objects.create(
#             user=request.user,
#             question=question,
#             session=session,
#             selected_option=selected_option,
#             response_time=timezone.now()
#         )

#         if question.status != 'Answered':
#             question.status = 'Answered'
#             question.save(update_fields=['status'])

#         if selected_option == question.correct_option:
#             user_score, _ = UserScore.objects.get_or_create(user=request.user, exam=session.exam)
#             user_score.score += 1
#             user_score.save(update_fields=['score'])

#         return api_response(success=True, data={'message': 'Answer submitted successfully'})

#     except Exception as e:
#         return api_response(success=False, error='An error occurred while submitting the answer', details=str(e), status=500)


# # @login_required
# def get_session_status(request, session_id):
#     try:
#         session = get_object_or_404(ProctoringSession, id=session_id)

#         questions = session.exam.questions
#         total_questions = questions.count()
#         answered_questions = questions.filter(status="Answered").count()
#         not_answered_questions = questions.filter(status="Not Answered").count()
#         not_visited_questions = questions.filter(status="Not Visited").count()
#         marked_for_review = questions.filter(status="Mark for Review").count()

#         remaining_time = session.duration - (timezone.now() - session.start_time)

#         status = {
#             'answered_questions': answered_questions,
#             'not_answered_questions': not_answered_questions,
#             'marked_for_review': marked_for_review,
#             'not_visited_questions': not_visited_questions,
#             'remaining_time': remaining_time.total_seconds(),
#             'total_questions': total_questions,
#         }

#         return api_response(status, status=200)

#     except Exception as e:
#         return api_response({'error': 'An error occurred while fetching session status',
#                              'details': str(e)}, status=500)


# # @login_required
# @require_GET
# def get_question_details(request, session_id, question_no):
#     try:
#         session = get_object_or_404(ProctoringSession, id=session_id)
#         question = get_object_or_404(Question, exam=session.exam, question_no=question_no)

#         response_data = {
#             'question_no': question.question_no,
#             'question_text': question.question_text,
#             'option1': question.option1,
#             'option2': question.option2,
#             'option3': question.option3,
#             'option4': question.option4,
#             'status': question.status,
#             'section': question.section,
#         }

#         return api_response(success=True, data=response_data)

#     except Exception as e:
#         return api_response(
#             success=False,
#             error='An error occurred while fetching the question details',
#             details=str(e),
#             status=500
#         )

# def count_questions(request, exam_id):
#     try:
#         exam = Exam.objects.filter(id=exam_id).only('id', 'name').first()
#         if not exam:
#             return api_response(success=False, error='Exam ID not found', status=404)

#         question_count = Question.objects.filter(exam=exam).count()

#         if not question_count:
#             return api_response(success=False, error='No Questions found for this Exam', data={'exam_name': exam.name}, status=404)

#         return api_response(success=True, data={'question_count': question_count, 'exam_name': exam.name})

#     except Exception as e:
#         return api_response(success=False, error='An error occurred while counting questions', details=str(e), status=500)

# @csrf_exempt
# # @login_required
# @require_POST
# def mark_for_review(request):
#     try:
#         form = MarkForReviewForm(json.loads(request.body))
#         if not form.is_valid():
#             return api_response(success=False, error='Invalid data', status=400)

#         session_id = form.cleaned_data['session_id']
#         question_no = form.cleaned_data['question_no']
#         mark = form.cleaned_data['mark']

#         session = get_object_or_404(ProctoringSession.objects.only('id', 'exam'), id=session_id)
#         question = get_object_or_404(Question.objects.only('id', 'status'), exam=session.exam, question_no=question_no)

#         new_status = 'Mark for Review' if mark else 'Not Answered'
#         if question.status != new_status:
#             question.status = new_status
#             question.save(update_fields=['status'])

#         message = 'Question marked for review' if mark else 'Mark for review removed'
#         return api_response(success=True, data={'status': message})

#     except Exception as e:
#         return api_response(success=False, error='An error occurred while marking the question for review', details=str(e), status=500)

# def fetch_event_types(request):
#     try:
#         if request.method == 'GET':
#             event_types = ProctoringEvent.objects.filter(event_type__isnull=False).exclude(event_type='').values_list('event_type', flat=True).distinct()
#             return api_response({'event_types': list(event_types)})
#         else:
#             return api_response({'status': 'error', 'message': 'Invalid request method'}, status=400)
#     except Exception as e:
#         return api_response({'status': 'error', 'message': str(e)}, status=500)

# def fetch_section_types(request):
#     try:
#         if request.method == 'GET':
#             section_types = Question.objects.filter(section__isnull=False).exclude(section='').values_list('section', flat=True).distinct()
#             return api_response({'section_types': list(section_types)})
#         else:
#             return api_response({'status': 'error', 'message': 'Invalid request method'}, status=400)
#     except Exception as e:
#         return api_response({'status': 'error', 'message': str(e)}, status=500)

# def fetch_status_types(request):
#     try:
#         if request.method == 'GET':
#             status_types = Question.objects.filter(status__isnull=False).exclude(status='').values_list('status', flat=True).distinct()
#             return api_response({'status_types': list(status_types)})
#         else:
#             return api_response({'status': 'error', 'message': 'Invalid request method'}, status=400)
#     except Exception as e:
#         return api_response({'status': 'error', 'message': str(e)}, status=500)

# class StatusTypeChoicesAPIView(APIView):
#     def get(self, request, fmt=None):
#         try:
#             session_type_choices = {key: value for key, value in ProctoringSession.STATUS_CHOICES}
#             return api_response({'choices': session_type_choices}, status=200)
#         except Exception as e:
#             return api_response({'status': 'error', 'message': str(e)}, status=500)

# def fetch_user_score(user, exam_id):
#     try:
#         user_score = UserScore.objects.select_related('exam').get(user=user, exam_id=exam_id)
#         return user_score.score
#     except UserScore.DoesNotExist:
#         return api_response({'status': 'error', 'message': 'User score not found.'}, status=404)
#     except Exception as e:
#         return api_response({'status': 'error', 'message': str(e)}, status=500)

# # @login_required
# @require_GET
# def get_user_score(request, exam_id):
#     user = request.user

#     try:
#         score = fetch_user_score(user, exam_id)
#         exam_name = Exam.objects.get(id=exam_id).name

#         response_data = {
#             'user': user.username,
#             'exam': exam_name,
#             'score': score
#         }
#         return api_response(success=True, data=response_data)
#     except UserScore.DoesNotExist:
#         return api_response(success=False, error='User score not found.', status=404)
#     except Exam.DoesNotExist:
#         return api_response(success=False, error='Exam not found.', status=404)
#     except Exception as e:
#         return api_response(success=False, error='An error occurred while fetching user score', details=str(e), status=500)

# @csrf_exempt
# def get_details(request):
#     if request.method == 'POST':
#         try:
#             data = json.loads(request.body)
#             session_id = data.get('session_id')

#             session = get_object_or_404(ProctoringSession, id=session_id)
#             exam = session.exam
#             exam_id = exam.id

#             score = fetch_user_score(request.user, exam_id)

#             answered_questions = exam.questions.filter(status="Answered").count()
#             not_answered_questions = exam.questions.filter(status="Not Answered").count()
#             not_visited_questions = exam.questions.filter(status="Not Visited").count()
#             marked_for_review = exam.questions.filter(status="Mark for Review").count()

#             details = {
#                 'Name': data.get('name'),
#                 'Phone': data.get('mobile_no'),
#                 'Email': data.get('email'),
#                 'Score': score,
#                 'answered_questions': answered_questions,
#                 'not_answered_questions': not_answered_questions,
#                 'marked_for_review': marked_for_review,
#                 'not_visited_questions': not_visited_questions,
#             }

#             return api_response({'Quiz Summary': details}, status=200)

#         except json.JSONDecodeError:
#             return api_response({'error': 'Invalid JSON'}, status=400)
#         except Exception as e:
#             return api_response({'error': 'An error occurred', 'details': str(e)}, status=500)
#     else:
#         return api_response({'error': 'Method not allowed'}, status=405)

# @csrf_exempt
# @require_POST
# def submit_all_answers(request):
#     try:
#         form = SubmitAllAnswersForm(json.loads(request.body))
#         if form.is_valid():
#             session_id = form.cleaned_data['session_id']
#             answers = form.cleaned_data['answers']

#             session = get_object_or_404(ProctoringSession, id=session_id)
#             user_score, _ = UserScore.objects.get_or_create(user=request.user, exam=session.exam)

#             question_map = {q.question_no: q for q in session.exam.questions.all()}
#             current_time = timezone.now()

#             for answer in answers:
#                 question_no = answer['question_no']
#                 selected_option = answer['selected_option']
#                 question = question_map.get(question_no)

#                 if question:
#                     _, created = UserResponse.objects.get_or_create(
#                         user=request.user,
#                         question=question,
#                         session=session,
#                         defaults={'selected_option': selected_option, 'response_time': current_time}
#                     )
#                     if created and selected_option == question.correct_option:
#                         user_score.score += 1

#                     question.status = 'Answered'
#                     question.save()

#             user_score.save()
#             return api_response({'success': True, 'message': 'Go to details page'}, status=200)
#         else:
#             return api_response({'success': False, 'error': 'Invalid data', 'details': form.errors}, status=400)
#     except Exception as e:
#         return api_response({'success': False, 'error': 'An error occurred while submitting all answers', 'details': str(e)}, status=500)

# # @login_required
# @require_GET
# def get_next_question(request, session_id, current_question_no):
#     try:
#         session = get_object_or_404(ProctoringSession, id=session_id)
#         next_question = (
#             Question.objects.filter(exam=session.exam, question_no__gt=current_question_no)
#             .order_by('question_no')
#             .values('question_no', 'question_text', 'option1', 'option2', 'option3', 'option4', 'status', 'section')
#             .first()
#         )

#         if not next_question:
#             return JsonResponse({'success': False, 'error': 'No next question available'}, status=404)

#         return api_response(next_question, status=200)
#     except Exception as e:
#         return api_response({'success': False, 'error': 'An error occurred while fetching the next question', 'details': str(e)}, status=500)

# # @login_required
# @require_GET
# def get_previous_question(request, session_id, current_question_no):
#     try:
#         session = get_object_or_404(ProctoringSession, id=session_id)
#         previous_question = (
#             Question.objects.filter(exam=session.exam, question_no__lt=current_question_no)
#             .order_by('-question_no')
#             .values('question_no', 'question_text', 'option1', 'option2', 'option3', 'option4', 'status', 'section')
#             .first()
#         )

#         if not previous_question:
#             return api_response({'success': False, 'error': 'No previous question available'}, status=404)

#         return api_response(previous_question, status=200)
#     except Exception as e:
#         return api_response({'success': False, 'error': 'An error occurred while fetching the previous question', 'details': str(e)}, status=500)

# @csrf_exempt
# def submit_details(request):
#     try:
#         if request.method == 'POST':
#             form = ExamParticipantForm(request.POST)
#             if not form.is_valid():
#                 return api_response({'status': 'error', 'errors': form.errors})

#             participant = form.save(commit=False)
#             participant.exam_started = True
#             participant.save()

#             return api_response({
#                 'status': 'success',
#                 'message': 'Exam details submitted successfully',
#                 'participant_id': participant.id,
#                 'exam_started': participant.exam_started
#             })

#         return api_response({'status': 'error', 'message': 'Invalid request method'}, status=400)

#     except Exception as e:
#         return api_response({'status': 'error', 'message': str(e)}, status=500)

from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Messages, Attachment, new_user, JobSeeker, CompanyInCharge, UniversityInCharge, Messages1, Attachment1

@csrf_exempt
def search_all(request):
    if request.method != "GET":
        return JsonResponse({'status': 'false', 'message': 'Invalid request method'}, status=405)

    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({'error': 'Token is missing or in an invalid format'}, status=400)
        
        token = auth_header.split(' ')[1]
        sender_email = request.GET.get('sender_email')

        sender = None
        if new_user.objects.filter(email=sender_email, token=token).exists():
            sender = new_user.objects.get(email=sender_email, token=token)
        elif JobSeeker.objects.filter(email=sender_email, token=token).exists():
            sender = JobSeeker.objects.get(email=sender_email, token=token)
        elif CompanyInCharge.objects.filter(official_email=sender_email, token=token).exists():
            sender = CompanyInCharge.objects.get(official_email=sender_email, token=token)

        if not sender:
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

        contact_list = list(student_contacts) + list(jobseeker_contacts) + list(company_contacts)

        return JsonResponse({
            'status': 'success',
            'contacts': contact_list if contact_list else []
        }, status=200)

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@csrf_exempt
def getMessages(request):
    if request.method != "GET":
        return JsonResponse({'status': 'false', 'message': 'Invalid request method'}, status=405)

    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return JsonResponse({'status': 'false', 'message': 'Token is missing or in an invalid format'}, status=400)

    token = auth_header.split(' ')[1]
    sender_email = request.GET.get('sender_email')
    recipient_email = request.GET.get('recipient_email')

    if not sender_email or not recipient_email:
        return JsonResponse({'status': 'false', 'message': 'Required fields missing'}, status=400)

    try:
        sender = None
        sender_field = None
        if new_user.objects.filter(token=token, email=sender_email).exists():
            sender = new_user.objects.get(token=token, email=sender_email)
            sender_field = 'student'
        elif JobSeeker.objects.filter(token=token, email=sender_email).exists():
            sender = JobSeeker.objects.get(token=token, email=sender_email)
            sender_field = 'candidate'
        elif CompanyInCharge.objects.filter(token=token, official_email=sender_email).exists():
            sender = CompanyInCharge.objects.get(token=token, official_email=sender_email)
            sender_field = 'company'

        if not sender:
            return JsonResponse({'status': 'false', 'message': 'Sender email does not match the token'}, status=403)

        recipient = None
        recipient_field = None
        if new_user.objects.filter(email=recipient_email).exists():
            recipient = new_user.objects.get(email=recipient_email)
            recipient_field = 'student'
        elif JobSeeker.objects.filter(email=recipient_email).exists():
            recipient = JobSeeker.objects.get(email=recipient_email)
            recipient_field = 'candidate'
        elif CompanyInCharge.objects.filter(official_email=recipient_email).exists():
            recipient = CompanyInCharge.objects.get(official_email=recipient_email)
            recipient_field = 'company'

        if not recipient:
            return JsonResponse({'status': 'false', 'message': 'Recipient not found'}, status=404)

        messages = Messages.objects.filter(
            **{sender_field: sender, recipient_field: recipient}
        ).prefetch_related('attachments')

        messages_data = [
            {
                'message_id': message.id,
                'sender_email': sender_email, 
                'recipient_email': recipient_email,
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
            for message in messages
        ]

        messages.filter(is_read=False).update(is_read=True)

        if not messages_data:
            return JsonResponse({'status': 'false', 'message': 'No messages found'}, status=404)

        return JsonResponse({'status': 'success', 'messages': messages_data}, status=200)

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@csrf_exempt
def sendMessage(request):
    if request.method != 'POST':
        return JsonResponse({
            "status": "false",
            "message": "Invalid request method"
        }, status=405)

    sender_email = request.POST.get('sender_email')
    recipient_email = request.POST.get('recipient_email')
    content = request.POST.get('content')

    if not all([sender_email, recipient_email, content]):
        return JsonResponse({
            "status": "false",
            "message": "Required fields are missing"
        }, status=400)

    sender, sender_model = None, None
    if new_user.objects.filter(email=sender_email).exists():
        sender = new_user.objects.get(email=sender_email)
        sender_model = "student"
    elif JobSeeker.objects.filter(email=sender_email).exists():
        sender = JobSeeker.objects.get(email=sender_email)
        sender_model = "candidate"
    elif CompanyInCharge.objects.filter(official_email=sender_email).exists():
        sender = CompanyInCharge.objects.get(official_email=sender_email)
        sender_model = "company"

    recipient, recipient_model = None, None
    if new_user.objects.filter(email=recipient_email).exists():
        recipient = new_user.objects.get(email=recipient_email)
        recipient_model = "student"
    elif JobSeeker.objects.filter(email=recipient_email).exists():
        recipient = JobSeeker.objects.get(email=recipient_email)
        recipient_model = "candidate"
    elif CompanyInCharge.objects.filter(official_email=recipient_email).exists():
        recipient = CompanyInCharge.objects.get(official_email=recipient_email)
        recipient_model = "company"

    if not sender or not recipient:
        return JsonResponse({
            "status": "false",
            "message": "Sender or recipient not found"
        }, status=404)

    message_data = {
        'content': content,
        'student': sender if sender_model == "student" else recipient if recipient_model == "student" else None,
        'candidate': sender if sender_model == "candidate" else recipient if recipient_model == "candidate" else None,
        'company': sender if sender_model == "company" else recipient if recipient_model == "company" else None
    }

    message = Messages.objects.create(**message_data)

    for attachment in request.FILES.getlist('attachments'):
        Attachment.objects.create(message=message, file=attachment)

    return JsonResponse({
        "status": "success",
        "message": "Message sent successfully"
    }, status=201)


@csrf_exempt
def all_inbox(request):
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
        user_type = None
        if new_user.objects.filter(email=email, token=token).exists():
            user = new_user.objects.get(email=email, token=token)
            user_type = 'student'
        elif JobSeeker.objects.filter(email=email, token=token).exists():
            user = JobSeeker.objects.get(email=email, token=token)
            user_type = 'candidate'
        elif CompanyInCharge.objects.filter(official_email=email, token=token).exists():
            user = CompanyInCharge.objects.get(official_email=email, token=token)
            user_type = 'company'
        else:
            return JsonResponse({'status': 'false', 'message': 'Invalid token or email'}, status=403)

        if user_type == 'student':
            messages_query = Messages.objects.filter(student=user).order_by('-timestamp')
        elif user_type == 'candidate':
            messages_query = Messages.objects.filter(candidate=user).order_by('-timestamp')
        elif user_type == 'company':
            messages_query = Messages.objects.filter(company=user).order_by('-timestamp')

        if filter_value in ['read', 'unread']:
            is_read = filter_value == 'read'
            messages_query = messages_query.filter(is_read=is_read)

        message_list = []
        for message in messages_query:
            recipient_email = None

            if message.company and message.company.official_email != email:
                recipient_email = message.company.official_email
            elif message.student and message.student.email != email:
                recipient_email = message.student.email
            elif message.candidate and message.candidate.email != email:
                recipient_email = message.candidate.email

            message_data = {
                'id': message.id,
                'sender_email': email,
                'recipient_email': recipient_email,
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
            message_list.append(message_data)

        return JsonResponse({'status': 'success', 'messages': message_list}, status=200)

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
##

@csrf_exempt
def searchs_all(request):
    if request.method != "GET":
        return JsonResponse({'status': 'false', 'message': 'Invalid request method'}, status=405)

    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({'error': 'Token is missing or in an invalid format'}, status=400)
        
        token = auth_header.split(' ')[1]
        sender_email = request.GET.get('sender_email')

        sender = None
        if new_user.objects.filter(email=sender_email, token=token).exists():
            sender = new_user.objects.get(email=sender_email, token=token)
        elif JobSeeker.objects.filter(email=sender_email, token=token).exists():
            sender = JobSeeker.objects.get(email=sender_email, token=token)
        elif UniversityInCharge.objects.filter(official_email=sender_email, token=token).exists():
            sender = UniversityInCharge.objects.get(official_email=sender_email, token=token)

        if not sender:
            return JsonResponse({'status': 'false', 'message': 'Sender email does not match the token'}, status=403)

        query = request.GET.get('q', '').strip()

        student_contacts = new_user.objects.all().values('id', 'firstname', 'lastname', 'email')
        jobseeker_contacts = JobSeeker.objects.all().values('id', 'first_name', 'last_name', 'email')
        college_contacts = UniversityInCharge.objects.all().values('id', 'university_name', 'official_email')

        if query:
            student_contacts = student_contacts.filter(
                Q(firstname__icontains=query) |
                Q(email__icontains=query)
            )
            jobseeker_contacts = jobseeker_contacts.filter(
                Q(first_name__icontains=query) |
                Q(email__icontains=query)
            )
            college_contacts = college_contacts.filter(
                Q(university_name__icontains=query) |
                Q(official_email__icontains=query)
            )

        contact_list = list(student_contacts) + list(jobseeker_contacts) + list(college_contacts)

        return JsonResponse({
            'status': 'success',
            'contacts': contact_list if contact_list else []
        }, status=200)

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@csrf_exempt
def send_message(request):
    if request.method != 'POST':
        return JsonResponse({
            "status": "false",
            "message": "Invalid request method"
        }, status=405)

    sender_email = request.POST.get('sender_email')
    recipient_email = request.POST.get('recipient_email')
    content = request.POST.get('content')

    if not all([sender_email, recipient_email, content]):
        return JsonResponse({
            "status": "false",
            "message": "Required fields are missing"
        }, status=400)

    sender, sender_model = None, None
    if new_user.objects.filter(email=sender_email).exists():
        sender = new_user.objects.get(email=sender_email)
        sender_model = "student"
    elif JobSeeker.objects.filter(email=sender_email).exists():
        sender = JobSeeker.objects.get(email=sender_email)
        sender_model = "candidate"
    elif UniversityInCharge.objects.filter(official_email=sender_email).exists():
        sender = UniversityInCharge.objects.get(official_email=sender_email)
        sender_model = "college"

    recipient, recipient_model = None, None
    if new_user.objects.filter(email=recipient_email).exists():
        recipient = new_user.objects.get(email=recipient_email)
        recipient_model = "student"
    elif JobSeeker.objects.filter(email=recipient_email).exists():
        recipient = JobSeeker.objects.get(email=recipient_email)
        recipient_model = "candidate"
    elif UniversityInCharge.objects.filter(official_email=recipient_email).exists():
        recipient = UniversityInCharge.objects.get(official_email=recipient_email)
        recipient_model = "college"

    if not sender or not recipient:
        return JsonResponse({
            "status": "false",
            "message": "Sender or recipient not found"
        }, status=404)

    message_data = {
        'content': content,
        'student': sender if sender_model == "student" else recipient if recipient_model == "student" else None,
        'candidate': sender if sender_model == "candidate" else recipient if recipient_model == "candidate" else None,
        'college': sender if sender_model == "college" else recipient if recipient_model == "college" else None
    }

    message = Messages1.objects.create(**message_data)

    for attachment in request.FILES.getlist('attachments'):
        Attachment1.objects.create(message=message, file=attachment)

    return JsonResponse({
        "status": "success",
        "message": "Message sent successfully"
    }, status=201)


@csrf_exempt
def get_messages(request):
    if request.method != "GET":
        return JsonResponse({'status': 'false', 'message': 'Invalid request method'}, status=405)

    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return JsonResponse({'status': 'false', 'message': 'Token is missing or in an invalid format'}, status=400)

    token = auth_header.split(' ')[1]
    sender_email = request.GET.get('sender_email')
    recipient_email = request.GET.get('recipient_email')

    if not sender_email or not recipient_email:
        return JsonResponse({'status': 'false', 'message': 'Required fields missing'}, status=400)

    try:
        sender = None
        sender_field = None
        if new_user.objects.filter(token=token, email=sender_email).exists():
            sender = new_user.objects.get(token=token, email=sender_email)
            sender_field = 'student'
        elif JobSeeker.objects.filter(token=token, email=sender_email).exists():
            sender = JobSeeker.objects.get(token=token, email=sender_email)
            sender_field = 'candidate'
        elif UniversityInCharge.objects.filter(token=token, official_email=sender_email).exists():
            sender = UniversityInCharge.objects.get(token=token, official_email=sender_email)
            sender_field = 'college'

        if not sender:
            return JsonResponse({'status': 'false', 'message': 'Sender email does not match the token'}, status=403)

        recipient = None
        recipient_field = None
        if new_user.objects.filter(email=recipient_email).exists():
            recipient = new_user.objects.get(email=recipient_email)
            recipient_field = 'student'
        elif JobSeeker.objects.filter(email=recipient_email).exists():
            recipient = JobSeeker.objects.get(email=recipient_email)
            recipient_field = 'candidate'
        elif UniversityInCharge.objects.filter(official_email=recipient_email).exists():
            recipient = UniversityInCharge.objects.get(official_email=recipient_email)
            recipient_field = 'college'

        if not recipient:
            return JsonResponse({'status': 'false', 'message': 'Recipient not found'}, status=404)

        messages = Messages1.objects.filter(
            Q(**{sender_field: sender}) & Q(**{recipient_field: recipient})
        ).prefetch_related('attachments')

        messages_data = [
            {
                'message_id': message.id,
                'sender_email': sender_email, 
                'recipient_email': recipient_email,
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
            for message in messages
        ]

        messages.filter(is_read=False).update(is_read=True)

        if not messages_data:
            return JsonResponse({'status': 'false', 'message': 'No messages found'}, status=404)

        return JsonResponse({'status': 'success', 'messages': messages_data}, status=200)

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500) 
    
@csrf_exempt
def my_inbox(request):
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
        user_type = None
        if new_user.objects.filter(email=email, token=token).exists():
            user = new_user.objects.get(email=email, token=token)
            user_type = 'student'
        elif JobSeeker.objects.filter(email=email, token=token).exists():
            user = JobSeeker.objects.get(email=email, token=token)
            user_type = 'candidate'
        elif UniversityInCharge.objects.filter(official_email=email, token=token).exists():
            user = UniversityInCharge.objects.get(official_email=email, token=token)
            user_type = 'college'
        else:
            return JsonResponse({'status': 'false', 'message': 'Invalid token or email'}, status=403)

        if user_type == 'student':
            messages_query = Messages1.objects.filter(student=user).order_by('-timestamp')
        elif user_type == 'candidate':
            messages_query = Messages1.objects.filter(candidate=user).order_by('-timestamp')
        elif user_type == 'college':
            messages_query = Messages1.objects.filter(college=user).order_by('-timestamp')

        if filter_value in ['read', 'unread']:
            is_read = filter_value == 'read'
            messages_query = messages_query.filter(is_read=is_read)

        message_list = []
        for message in messages_query:
            recipient_email = None

            if message.college and message.college.official_email != email:
                recipient_email = message.college.official_email
            elif message.student and message.student.email != email:
                recipient_email = message.student.email
            elif message.candidate and message.candidate.email != email:
                recipient_email = message.candidate.email

            message_data = {
                'id': message.id,
                'sender_email': email,
                'recipient_email': recipient_email,
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
            message_list.append(message_data)

        return JsonResponse({'status': 'success', 'messages': message_list}, status=200)

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


