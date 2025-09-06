import uuid
from django.db import models
from django.utils import timezone


class Candidate(models.Model):
    full_name = models.CharField("F.I.Sh", max_length=150)
    phone = models.CharField("Telefon", max_length=50)
    region = models.CharField("Hudud", max_length=100)
    work_position = models.CharField("Lavozim", max_length=100)

    HR_CHOICES = [
        ("Gulnoza", "Gulnoza"),
        ("Iroda", "Iroda"),
        ("Abdurahmon", "Abdurahmon"),
        ("Boshqa", "Boshqa"),  # boshqa degani
    ]
    hr_manager = models.CharField("HR menejer", max_length=50, choices=HR_CHOICES)

    created_at = models.DateTimeField("Ro‘yxatdan o‘tgan vaqt", auto_now_add=True)

    class Meta:
        verbose_name = "Nomzod"
        verbose_name_plural = "Nomzodlar"

    def __str__(self):
        return f"{self.full_name} ({self.phone})"


class Exam(models.Model):
    title = models.CharField("Imtihon nomi", max_length=200)
    description = models.TextField("Tavsif", blank=True)
    duration_minutes = models.PositiveIntegerField("Davomiyligi (daqiqada)", default=30)
    is_active = models.BooleanField("Faolmi?", default=True)
    shuffle_questions = models.BooleanField("Savollarni aralashtirish", default=True)
    max_focus_violations = models.PositiveIntegerField(
        "Maks. fokus buzilishlar soni", default=0
    )

    class Meta:
        verbose_name = "Imtihon"
        verbose_name_plural = "Imtihonlar"

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
        (MCQ, "Variantli"),
        (TRUE_FALSE, "To‘g‘ri/Yolg‘on"),
        (SHORT, "Qisqa javob"),
    ]

    exam = models.ForeignKey(
        Exam, verbose_name="Imtihon", related_name="questions", on_delete=models.CASCADE
    )
    text = models.TextField("Savol matni")
    qtype = models.CharField("Savol turi", max_length=10, choices=TYPES, default=MCQ)
    order = models.PositiveIntegerField("Tartib raqami", default=0)

    image = models.ImageField(
        "Rasm", upload_to="question_images/", null=True, blank=True
    )

    class Meta:
        verbose_name = "Savol"
        verbose_name_plural = "Savollar"

    def __str__(self):
        return f"[{self.exam.title}] {self.text[:60]}"


class Choice(models.Model):
    question = models.ForeignKey(
        Question, verbose_name="Savol", related_name="choices", on_delete=models.CASCADE
    )
    text = models.CharField("Variant matni", max_length=500)
    is_correct = models.BooleanField("To‘g‘ri javobmi?", default=False)

    class Meta:
        verbose_name = "Javob varianti"
        verbose_name_plural = "Javob variantlari"

    def __str__(self):
        return f"Variant({self.question_id}): {self.text[:50]}"


class Attempt(models.Model):
    candidate = models.ForeignKey(
        Candidate, verbose_name="Nomzod", related_name="attempts", on_delete=models.CASCADE
    )
    exam = models.ForeignKey(
        Exam, verbose_name="Imtihon", related_name="attempts", on_delete=models.CASCADE
    )

    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    started_at = models.DateTimeField("Boshlangan vaqt", null=True, blank=True)
    submitted_at = models.DateTimeField("Tugatgan vaqt", null=True, blank=True)

    question_order = models.JSONField("Savollar tartibi", default=list, blank=True)

    score = models.FloatField("Ball", default=0.0)
    total_questions = models.PositiveIntegerField("Savollar soni", default=0)
    focus_violations = models.PositiveIntegerField("Fokus buzilishlari", default=0)

    ip_address = models.GenericIPAddressField("IP manzil", null=True, blank=True)
    user_agent = models.TextField("Brauzer ma’lumoti", blank=True)

    class Meta:
        indexes = [models.Index(fields=["token"])]
        unique_together = ("candidate", "exam")
        verbose_name = "Urinish"
        verbose_name_plural = "Urinishlar"

    def __str__(self):
        return f"{self.exam.title} - {self.candidate.full_name}"

    @property
    def is_submitted(self):
        return self.submitted_at is not None

    @property
    def ends_at(self):
        if not self.started_at:
            return None
        return self.started_at + timezone.timedelta(minutes=self.exam.duration_minutes)

    @property
    def seconds_left(self):
        if not self.started_at:
            return self.exam.duration_minutes * 60
        delta = self.ends_at - timezone.now()
        return max(0, int(delta.total_seconds()))

    def get_exam_url(self, base_url=None):
        if base_url:
            return f"{base_url}/exam/{self.token}/"
        return f"/exam/{self.token}/"


class Answer(models.Model):
    attempt = models.ForeignKey(
        Attempt, verbose_name="Urinish", related_name="answers", on_delete=models.CASCADE
    )
    question = models.ForeignKey(Question, verbose_name="Savol", on_delete=models.CASCADE)
    choice = models.ForeignKey(
        Choice,
        verbose_name="Variant",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    text_answer = models.TextField("Matnli javob", blank=True)
    is_correct = models.BooleanField("To‘g‘rimi?", default=False)
    answered_at = models.DateTimeField("Javob vaqti", auto_now_add=True)

    class Meta:
        unique_together = ("attempt", "question")
        verbose_name = "Javob"
        verbose_name_plural = "Javoblar"

    def __str__(self):
        return f"Javob({self.question.text[:30]})"
