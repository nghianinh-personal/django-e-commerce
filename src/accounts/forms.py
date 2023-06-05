from django.forms import ModelForm, CharField, PasswordInput, ValidationError
from .models import User


class UserForm(ModelForm):
    password = CharField(widget=PasswordInput())
    confirm_password = CharField(widget=PasswordInput())
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']

    def clean(self):
        cleaned_data = super(UserForm, self).clean()
        if cleaned_data.get('password') != cleaned_data.get('confirm_password'):
            raise ValidationError('Password dose not match')
