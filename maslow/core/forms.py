from django import forms
from .models import Goal


class GoalInitialForm(forms.Form):
    """Initial goal input form"""
    original_goal = forms.CharField(
        max_length=500,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'เช่น อยากวิ่ง, อยากอ่านหนังสือ, อยากตื่นเช้า...',
            'autofocus': True,
        }),
        label='เป้าหมายของคุณคืออะไร?'
    )


class WhyLadderForm(forms.Form):
    """Form for Why Ladder responses"""
    answer = forms.CharField(
        max_length=500,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'พิมพ์คำตอบของคุณ...',
            'autofocus': True,
        }),
        label=''
    )


class BaselineForm(forms.Form):
    """Form for collecting baseline data"""
    baseline_value = forms.IntegerField(
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control form-control-lg text-center',
            'placeholder': '0',
            'style': 'max-width: 150px;'
        }),
        label='ตอนนี้คุณทำได้เท่าไหร่?'
    )
    baseline_unit = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'นาที, ชั่วโมง, ครั้ง, หน้า...',
            'style': 'max-width: 150px;'
        }),
        label='หน่วย'
    )


class GoalLevelForm(forms.Form):
    """Form for selecting goal level"""
    LEVEL_CHOICES = [
        ('safe', 'Safe Goal'),
        ('growth', 'Growth Goal'),
        ('stretch', 'Stretch Goal'),
    ]
    
    goal_level = forms.ChoiceField(
        choices=LEVEL_CHOICES,
        widget=forms.RadioSelect(attrs={
            'class': 'btn-check'
        }),
        initial='growth'
    )


class ProgressForm(forms.Form):
    """Form for updating progress"""
    progress = forms.IntegerField(
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control text-center',
            'placeholder': '0'
        }),
        label='ทำได้เท่าไหร่แล้ว?'
    )
