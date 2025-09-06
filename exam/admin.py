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


from django.urls import reverse
from django.utils.html import format_html

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ("title", "duration_minutes", "shuffle_questions", "registration_link")
    search_fields = ("title",)

    def registration_link(self, obj):
        url = reverse("register_exam", args=[obj.id])
        return format_html('<a href="{}" target="_blank">Open Link</a>', url)
    registration_link.short_description = "Registration Link"



@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ("full_name", "phone", "region", "work_position", "hr_manager", "created_at")
    search_fields = ("full_name", "region", "work_position")


class AnswerInline(admin.TabularInline):
    model = Answer
    readonly_fields = ("question", "choice", "text_answer", "is_correct")
    can_delete = False
    extra = 0


import openpyxl
from openpyxl.styles import PatternFill
from django.http import HttpResponse
from django.utils.html import format_html
from django.conf import settings

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

    actions = ["export_attempts_excel"]

    def exam_link(self, obj):
        if not obj.token:
            return "-"
        base_url = getattr(settings, "SITE_URL", "http://127.0.0.1:8000")
        url = f"{base_url}/exam/{obj.token}/"
        return format_html('<a href="{}" target="_blank">{}</a>', url, url)

    exam_link.short_description = "Exam Link"

    def export_attempts_excel(self, request, queryset):
        """
        Export selected attempts to Excel:
        - Candidate info
        - Exam info
        - Score
        - Each question as a column
        - Answer text, colored green if correct, red if wrong
        """
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Attempts"

        # Collect all unique questions across selected attempts
        all_questions = []
        for attempt in queryset:
            for q in attempt.exam.questions.all():
                if q not in all_questions:
                    all_questions.append(q)

        # Header row
        headers = ["Candidate", "Phone", "Region", "Work Position", "HR Manager",
                   "Exam", "Score", "Started At", "Submitted At"]
        headers += [q.text[:50] for q in all_questions]  # shorten question text
        ws.append(headers)

        # Colors
        green_fill = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")
        red_fill = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")

        # Data rows
        for attempt in queryset:
            row = [
                attempt.candidate.full_name,
                attempt.candidate.phone,
                attempt.candidate.region,
                attempt.candidate.work_position,
                attempt.candidate.hr_manager,
                attempt.exam.title,
                attempt.score,
                attempt.started_at,
                attempt.submitted_at,
            ]

            # Build answers map {question_id: Answer}
            answers_map = {a.question_id: a for a in attempt.answers.all()}

            for q in all_questions:
                ans = answers_map.get(q.id)
                if ans:
                    if ans.choice:
                        cell_value = ans.choice.text
                    else:
                        cell_value = ans.text_answer
                else:
                    cell_value = ""

                row.append(cell_value)

            ws.append(row)

            # Apply colors after row is appended
            excel_row = ws.max_row
            for idx, q in enumerate(all_questions, start=len(headers) - len(all_questions) + 1):
                ans = answers_map.get(q.id)
                cell = ws.cell(row=excel_row, column=idx + 1)
                if ans:
                    if ans.is_correct:
                        cell.fill = green_fill
                    else:
                        cell.fill = red_fill

        # Response
        response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response["Content-Disposition"] = 'attachment; filename="attempts.xlsx"'
        wb.save(response)
        return response

    export_attempts_excel.short_description = "Export selected attempts to Excel"



@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ("attempt", "question", "choice", "text_answer", "is_correct")
    list_filter = ("is_correct", "question__exam")
    search_fields = ("attempt__candidate__full_name", "question__text")
