import json
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Avg, Count
from .models import Test, Question, Choice, Student, Attempt, Answer
from .translation import uz_latin_to_cyrillic


# ─── O'QUVCHI VIEWS ───────────────────────────────────────────

def home(request):
    tests = Test.objects.filter(is_active=True)
    return render(request, 'quiz/home.html', {'tests': tests})


def student_enter(request, test_id):
    test = get_object_or_404(Test, id=test_id, is_active=True)
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        phone = request.POST.get('phone', '').strip()
        if not name or not phone:
            return render(request, 'quiz/enter.html', {'test': test, 'error': "Ism va telefon raqam kiritilishi shart."})
        student, _ = Student.objects.get_or_create(phone=phone, defaults={'name': name})
        student.name = name
        student.save()
        attempt = Attempt.objects.create(student=student, test=test, total=test.questions.count())
        return redirect('quiz:take', attempt_id=attempt.id)
    return render(request, 'quiz/enter.html', {'test': test})


def take_test(request, attempt_id):
    attempt = get_object_or_404(Attempt, id=attempt_id)
    if attempt.finished_at:
        return redirect('quiz:result', attempt_id=attempt.id)
    questions = list(attempt.test.questions.prefetch_related('choices'))
    return render(request, 'quiz/take.html', {
        'attempt': attempt,
        'questions': questions,
    })


def submit_test(request, attempt_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)
    attempt = get_object_or_404(Attempt, id=attempt_id)
    if attempt.finished_at:
        return JsonResponse({'redirect': f'/result/{attempt_id}/'})

    data = json.loads(request.body)
    time_spent = data.get('time_spent', 0)
    answers_data = data.get('answers', {})

    score = 0
    for question in attempt.test.questions.prefetch_related('choices'):
        chosen_id = answers_data.get(str(question.id))
        chosen = None
        is_correct = False
        if chosen_id:
            try:
                chosen = Choice.objects.get(id=int(chosen_id), question=question)
                is_correct = chosen.is_correct
                if is_correct:
                    score += 1
            except Choice.DoesNotExist:
                pass
        Answer.objects.create(attempt=attempt, question=question, chosen=chosen, is_correct=is_correct)

    attempt.score = score
    attempt.finished_at = timezone.now()
    attempt.time_spent_seconds = int(time_spent)
    attempt.save()
    return JsonResponse({'redirect': f'/result/{attempt_id}/'})


def result_view(request, attempt_id):
    attempt = get_object_or_404(Attempt, id=attempt_id)
    answers = attempt.answers.select_related('question', 'chosen').prefetch_related('question__choices')
    score = attempt.score
    if score > 8:
        price = 4_300_000
    elif score > 6:
        price = 4_370_000
    else:
        price = 4_500_000
    return render(request, 'quiz/result.html', {'attempt': attempt, 'answers': answers, 'price': price})


# ─── O'QITUVCHI VIEWS ─────────────────────────────────────────

def teacher_login(request):
    if request.user.is_authenticated:
        return redirect('quiz:dashboard')
    error = None
    if request.method == 'POST':
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user:
            login(request, user)
            return redirect('quiz:dashboard')
        error = "Noto'g'ri login yoki parol."
    return render(request, 'quiz/teacher_login.html', {'error': error})


def teacher_logout(request):
    logout(request)
    return redirect('quiz:home')


@login_required(login_url='/teacher/login/')
def dashboard(request):
    tests = Test.objects.annotate(attempt_count=Count('attempts')).order_by('-created_at')
    return render(request, 'quiz/dashboard.html', {'tests': tests})


@login_required(login_url='/teacher/login/')
def create_test(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        desc = request.POST.get('description', '').strip()
        duration = int(request.POST.get('duration', 30))
        test = Test.objects.create(
            title=title, title_uz_cyr=uz_latin_to_cyrillic(title),
            description=desc, description_uz_cyr=uz_latin_to_cyrillic(desc),
            duration_minutes=duration,
        )
        return redirect('quiz:edit_test', test_id=test.id)
    return render(request, 'quiz/create_test.html')


@login_required(login_url='/teacher/login/')
def edit_test(request, test_id):
    test = get_object_or_404(Test, id=test_id)
    questions = test.questions.prefetch_related('choices')
    return render(request, 'quiz/edit_test.html', {'test': test, 'questions': questions})


@login_required(login_url='/teacher/login/')
def add_question(request, test_id):
    test = get_object_or_404(Test, id=test_id)
    if request.method == 'POST':
        qtext = request.POST.get('question_text', '').strip()
        if qtext:
            order = test.questions.count() + 1
            q = Question.objects.create(
                test=test, text=qtext, text_uz_cyr=uz_latin_to_cyrillic(qtext), order=order
            )
            for i in range(1, 5):
                ctext = request.POST.get(f'choice_{i}', '').strip()
                is_correct = request.POST.get('correct') == str(i)
                if ctext:
                    Choice.objects.create(question=q, text=ctext, text_uz_cyr=uz_latin_to_cyrillic(ctext), is_correct=is_correct)
    return redirect('quiz:edit_test', test_id=test.id)


@login_required(login_url='/teacher/login/')
def delete_question(request, question_id):
    q = get_object_or_404(Question, id=question_id)
    test_id = q.test.id
    q.delete()
    return redirect('quiz:edit_test', test_id=test_id)


@login_required(login_url='/teacher/login/')
def toggle_test(request, test_id):
    test = get_object_or_404(Test, id=test_id)
    test.is_active = not test.is_active
    test.save()
    return redirect('quiz:dashboard')


@login_required(login_url='/teacher/login/')
def delete_test(request, test_id):
    test = get_object_or_404(Test, id=test_id)
    test.delete()
    return redirect('quiz:dashboard')


@login_required(login_url='/teacher/login/')
def retranslate_test(request, test_id):
    test = get_object_or_404(Test, id=test_id)
    test.title_uz_cyr = uz_latin_to_cyrillic(test.title)
    test.description_uz_cyr = uz_latin_to_cyrillic(test.description)
    test.save()
    for q in test.questions.prefetch_related('choices'):
        q.text_uz_cyr = uz_latin_to_cyrillic(q.text)
        q.save()
        for c in q.choices.all():
            c.text_uz_cyr = uz_latin_to_cyrillic(c.text)
            c.save()
    return redirect('quiz:edit_test', test_id=test.id)


@login_required(login_url='/teacher/login/')
def retranslate_all(request):
    for test in Test.objects.prefetch_related('questions__choices'):
        test.title_uz_cyr = uz_latin_to_cyrillic(test.title)
        test.description_uz_cyr = uz_latin_to_cyrillic(test.description)
        test.save()
        for q in test.questions.all():
            q.text_uz_cyr = uz_latin_to_cyrillic(q.text)
            q.save()
            for c in q.choices.all():
                c.text_uz_cyr = uz_latin_to_cyrillic(c.text)
                c.save()
    return redirect('quiz:dashboard')


@login_required(login_url='/teacher/login/')
def test_results(request, test_id):
    test = get_object_or_404(Test, id=test_id)
    attempts = test.attempts.filter(finished_at__isnull=False).select_related('student').order_by('-finished_at')
    avg = attempts.aggregate(avg=Avg('score'))['avg'] or 0
    return render(request, 'quiz/test_results.html', {
        'test': test, 'attempts': attempts, 'avg': round(avg, 1)
    })
