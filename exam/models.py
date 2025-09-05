# exams/models.py
import uuid
from django.db import models
from django.utils import timezone


class Candidate(models.Model):
    # Telegram-based or manual candidates
    telegram_id = models.CharField(max_length=64, null=True, blank=True, unique=True)
    full_name = models.CharField(max_length=150)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name


class Exam(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    duration_minutes = models.PositiveIntegerField(default=30)
    is_active = models.BooleanField(default=True)
    shuffle_questions = models.BooleanField(default=True)
    # If you want to allow a small number of focus/tab leaves before auto-submit
    max_focus_violations = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title

    @property
    def total_questions(self):
        return self.questions.count()


class Question(models.Model):
    MCQ = "MCQ"
    TRUE_FALSE = "TF"
    SHORT = "SHORT"

    TYPES = [
        (MCQ, "Multiple choice"),
        (TRUE_FALSE, "True/False"),
        (SHORT, "Short answer"),
    ]

    exam = models.ForeignKey(Exam, related_name="questions", on_delete=models.CASCADE)
    text = models.TextField()
    qtype = models.CharField(max_length=10, choices=TYPES, default=MCQ)
    # Optional ordering hint (we still shuffle per-attempt if enabled)
    order = models.PositiveIntegerField(default=0)

    image = models.ImageField(upload_to="question_images/", null=True, blank=True)

    def __str__(self):
        return f"[{self.exam.title}] {self.text[:60]}"


class Choice(models.Model):
    question = models.ForeignKey(Question, related_name="choices", on_delete=models.CASCADE)
    text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"Choice({self.question_id}): {self.text[:50]}"


import uuid
from django.db import models
from django.utils import timezone


class Attempt(models.Model):
    """
    One-time, shareable link via `token`.
    The first GET starts the attempt (sets started_at).
    """

    candidate = models.ForeignKey("Candidate", related_name="attempts", on_delete=models.CASCADE)
    exam = models.ForeignKey("Exam", related_name="attempts", on_delete=models.CASCADE)

    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    started_at = models.DateTimeField(null=True, blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True)

    # Persist the per-attempt question order (list of question IDs)
    question_order = models.JSONField(default=list, blank=True)

    # Stats
    score = models.FloatField(default=0.0)
    total_questions = models.PositiveIntegerField(default=0)
    focus_violations = models.PositiveIntegerField(default=0)

    # Diagnostics
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["token"]),
        ]
        unique_together = ("candidate", "exam")  # prevent duplicate attempts

    def __str__(self):
        return f"Attempt({self.exam.title} - {self.candidate.full_name})"

    @property
    def is_submitted(self):
        return self.submitted_at is not None

    @property
    def ends_at(self):
        """Return datetime when attempt ends (None if not started)."""
        if not self.started_at:
            return None
        return self.started_at + timezone.timedelta(minutes=self.exam.duration_minutes)

    @property
    def seconds_left(self):
        """Return how many seconds remain until exam ends."""
        if not self.started_at:
            return self.exam.duration_minutes * 60
        delta = self.ends_at - timezone.now()
        return max(0, int(delta.total_seconds()))

    def get_exam_url(self, base_url=None):
        """
        Generate direct URL to attempt exam page.
        `base_url` should be your SITE_URL from settings.
        """
        if base_url:
            return f"{base_url}/exam/{self.token}/"
        return f"/exam/{self.token}/"


class Answer(models.Model):
    attempt = models.ForeignKey(Attempt, related_name="answers", on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, null=True, blank=True, on_delete=models.SET_NULL)
    text_answer = models.TextField(blank=True)
    is_correct = models.BooleanField(default=False)
    answered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("attempt", "question")
