from django.urls import path
from . import views

urlpatterns = [
    path("exam/<int:exam_id>/register/", views.register_for_exam, name="register_exam"),
    path("<uuid:token>/", views.exam_view, name="exam_view"),
    path("<uuid:token>/submit/", views.exam_submit, name="exam_submit"),
    path("<uuid:token>/result/", views.exam_result, name="exam_result"),
]
