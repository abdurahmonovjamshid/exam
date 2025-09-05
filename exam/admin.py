from django.contrib import admin
from .models import Exam, Question, Choice, Candidate, Attempt, Answer
from django.utils.html import format_html
from django.conf import settings

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 2


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("text", "exam", "qtype", "order")
    list_filter = ("exam", "qtype")
    search_fields = ("text",)
    inlines = [ChoiceInline]


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ("title", "duration_minutes", "shuffle_questions")
    search_fields = ("title",)


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "created_at")
    search_fields = ("full_name", "email")


class AnswerInline(admin.TabularInline):
    model = Answer
    readonly_fields = ("question", "choice", "text_answer", "is_correct")
    can_delete = False
    extra = 0


@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = (
        "candidate",
        "exam",
        "score",
        "started_at",
        "submitted_at",
        "exam_link",
    )
    list_filter = ("exam", "submitted_at")
    search_fields = ("candidate__full_name", "exam__title", "token")
    readonly_fields = ("token", "exam_link", "started_at", "submitted_at")

    def exam_link(self, obj):
        """Clickable exam link for candidate."""
        if not obj.token:
            return "-"
        base_url = getattr(settings, "SITE_URL", "http://127.0.0.1:8000")
        url = f"{base_url}/exam/{obj.token}/"
        return format_html('<a href="{}" target="_blank">{}</a>', url, url)

    exam_link.short_description = "Exam Link"


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ("attempt", "question", "choice", "text_answer", "is_correct")
    list_filter = ("is_correct", "question__exam")
    search_fields = ("attempt__candidate__full_name", "question__text")
