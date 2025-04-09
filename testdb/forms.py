from django import forms
from .models import LocalCriminals, Panishment, PunishmentType
import datetime

class LocalCriminalsForm(forms.ModelForm):
    arrest_time = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="Время ареста",
        initial=datetime.date.today,
    )
    
    class Meta:
        model = LocalCriminals
        fields = ["person_id", "fio", "article_num", "arrest_time"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.initial['arrest_time'] = datetime.date.today()

class PanishmentForm(forms.ModelForm):
    class Meta:
        model = Panishment
        fields = [
            'cs', 'person_id', 'fio', 'article_num', 
            'punishment_type', 'numerical_value', 'fi_flag'
        ]
        widgets = {
            'punishment_type': forms.Select(choices=PunishmentType.choices),
        }