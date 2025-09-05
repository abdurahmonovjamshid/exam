import random
from django.core.management.base import BaseCommand
from exam.models import Exam, Question, Choice, Candidate


class Command(BaseCommand):
    help = "Generate a demo exam with sample questions and a test candidate"

    def handle(self, *args, **options):
        # Create Exam
        exam, created = Exam.objects.get_or_create(
            title="General Knowledge Demo Exam",
            defaults={"duration_minutes": 10, "shuffle_questions": True},
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"Created exam: {exam.title}"))
        else:
            self.stdout.write(self.style.WARNING(f"Exam already exists: {exam.title}"))

        # Sample Questions
        questions_data = [
            {
                "text": "What is the capital of France?",
                "qtype": "MCQ",
                "choices": [
                    ("Paris", True),
                    ("London", False),
                    ("Berlin", False),
                    ("Rome", False),
                ],
            },
            {
                "text": "2 + 2 = ?",
                "qtype": "MCQ",
                "choices": [
                    ("3", False),
                    ("4", True),
                    ("5", False),
                ],
            },
            {
                "text": "The Earth is flat.",
                "qtype": "TF",
                "choices": [
                    ("True", False),
                    ("False", True),
                ],
            },
            {
                "text": "Who wrote 'Hamlet'?",
                "qtype": "SHORT",
                "choices": [],
            },
        ]

        # Create Questions & Choices
        created_questions = []
        for idx, qd in enumerate(questions_data, start=1):
            q, q_created = Question.objects.get_or_create(
                exam=exam,
                text=qd["text"],
                defaults={"qtype": qd["qtype"], "order": idx},
            )
            if q_created:
                self.stdout.write(self.style.SUCCESS(f"  Added question: {q.text}"))
            else:
                self.stdout.write(self.style.WARNING(f"  Question already exists: {q.text}"))

            if qd["choices"]:
                for text, is_correct in qd["choices"]:
                    Choice.objects.get_or_create(
                        question=q,
                        text=text,
                        defaults={"is_correct": is_correct},
                    )
            created_questions.append(q)

        # Attach questions to exam
        exam.questions.set(created_questions)

        # Create a test candidate
        cand, c_created = Candidate.objects.get_or_create(
            email="demo@example.com",
            defaults={"full_name": "Demo Candidate"},
        )
        if c_created:
            self.stdout.write(self.style.SUCCESS(f"Created candidate: {cand.full_name}"))
        else:
            self.stdout.write(self.style.WARNING(f"Candidate already exists: {cand.full_name}"))

        self.stdout.write(self.style.SUCCESS("✅ Demo exam generation completed!"))
