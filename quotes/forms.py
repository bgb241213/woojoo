from django import forms
from .models import QuoteRequest
import datetime


class QuoteRequestForm(forms.ModelForm):
    class Meta:
        model = QuoteRequest
        fields = [
            'company_name', 'name', 'phone', 'email', 'business_number',
            'start_date', 'end_date', 'delivery_address', 'budget', 'message',
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date':   forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_start_date(self):
        start_date = self.cleaned_data.get('start_date')
        if start_date and start_date < datetime.date.today():
            raise forms.ValidationError('시작일은 오늘 이후여야 합니다.')
        return start_date

    def clean(self):
        cleaned = super().clean()
        start_date = cleaned.get('start_date')
        end_date = cleaned.get('end_date')
        if start_date and end_date and end_date < start_date:
            self.add_error('end_date', '종료일은 시작일 이후여야 합니다.')
        return cleaned
