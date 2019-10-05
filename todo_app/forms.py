from django import forms
from django.contrib.auth.models import User
from .models import Item
from django.utils import timezone
import datetime

class LoginForm(forms.Form):
    username = forms.CharField()
    password =  forms.CharField(widget=forms.PasswordInput)

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(label='Password',
                               widget=forms.PasswordInput)
    password2 = forms.CharField(label='Repeat password',
                                widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'first_name','last_name', 'email')

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Passwords don\'t match.')
        return cd['password2']

class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name','last_name','email')

class TaskCreateForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ('title','priority','date_due','description')
        widgets = {
            'date_due': forms.DateInput(format=('%m/%d/%Y'), attrs={'class':'form-control', 'placeholder':'Select a date', 'type':'date'}),
        }
        
    def clean_date_due(self):
        date = self.cleaned_data['date_due']
        if date < datetime.date.today():
            raise forms.ValidationError('Date cannot be in the past')
        return self.cleaned_data['date_due']

class TaskEditForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ('title','date_due','description','priority')
        widgets = {
            'date_due': forms.DateInput(format=('%m/%d/%Y'), attrs={'type':'date'}),
        }
        
    def clean_date_due(self):
        date = self.cleaned_data['date_due']
        if date < datetime.date.today():
            raise forms.ValidationError('Date cannot be in the past')
        return self.cleaned_data['date_due']
    

class EmailForm(forms.Form):
    email = forms.EmailField()
    comments = forms.CharField(required=False,widget=forms.Textarea) 
