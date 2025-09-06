from django import forms
from .models import Candidate

class CandidateRegistrationForm(forms.ModelForm):
    class Meta:
        model = Candidate
        fields = ["full_name", "phone", "region", "work_position", "hr_manager"]
