import random
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from django.utils import timezone
from .models import Attempt, Question, Choice, Answer


def exam_view(request, token):
    attempt = get_object_or_404(Attempt, token=token)
    exam = attempt.exam

    if attempt.submitted_at:
        return redirect("exam_result", token=token)

    if not attempt.started_at:
        attempt.started_at = timezone.now()
        qs = list(exam.questions.all().order_by("order", "id"))
        if exam.shuffle_questions:
            random.shuffle(qs)
        attempt.question_order = [q.id for q in qs]
        attempt.total_questions = len(qs)
        attempt.save()

    if attempt.ends_at and timezone.now() > attempt.ends_at:
        return redirect("exam_submit", token=token)

    qs_map = {q.id: q for q in exam.questions.prefetch_related("choices")}
    questions = [qs_map[qid] for qid in attempt.question_order if qid in qs_map]

    return render(request, "exams/exam_page.html", {
        "exam": exam,
        "attempt": attempt,
        "questions": questions,
    })


def exam_submit(request, token):
    attempt = get_object_or_404(Attempt, token=token)

    if attempt.submitted_at:
        return redirect("exam_result", token=token)

    if request.method != "POST":
        if attempt.ends_at and timezone.now() > attempt.ends_at:
            pass
        else:
            return HttpResponseForbidden("Invalid submission method.")

    attempt.answers.all().delete()

    correct_count = 0
    for qid in attempt.question_order:
        q = Question.objects.get(pk=qid)
        key = f"q-{q.id}"
        val = request.POST.get(key, "").strip()

        ans = Answer(attempt=attempt, question=q)

        if q.qtype in ["MCQ", "TF"]:
            try:
                choice = Choice.objects.get(pk=val, question=q)
                ans.choice = choice
                ans.is_correct = choice.is_correct
            except (Choice.DoesNotExist, ValueError):
                ans.is_correct = False
        elif q.qtype == "SHORT":
            ans.text_answer = val
            ans.is_correct = False

        ans.save()
        if ans.is_correct:
            correct_count += 1

    attempt.score = correct_count
    attempt.submitted_at = timezone.now()
    attempt.focus_violations = int(request.POST.get("focus_violations", 0))
    attempt.save()

    return redirect("exam_result", token=token)


def exam_result(request, token):
    attempt = get_object_or_404(Attempt, token=token)

    return render(request, "exams/exam_result.html", {
        "exam": attempt.exam,
        "attempt": attempt,
        "candidate": attempt.candidate,
        "answers": attempt.answers.select_related("question", "choice"),
        "score": attempt.score,
        "total": attempt.total_questions,
    })
