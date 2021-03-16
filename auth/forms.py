import logging

from django import forms


logger = logging.getLogger(__name__)
logger.debug('Logger in auth/forms.py loaded')


class LoginForm(forms.Form):
    login = forms.CharField(label='login',
                            required=True,
                            widget=forms.TextInput(attrs={'class': 'text_input form_element',
                                                                         'placeholder': 'login'}))
    password = forms.CharField(label='password',
                               required=True,
                               widget=forms.PasswordInput(attrs={'class': 'text_input form_element',
                                                                 'placeholder': 'password'}))
    license = forms.BooleanField(label='license',
                                 required=True,
                                 help_text='Засим подтверждаю, что подтверждаю поправки и поплевки')

    def clean_login(self):
        logger.debug('Cleaning login')
        cleaned_login = self.cleaned_data['login']
        if cleaned_login == 'login':
            raise forms.ValidationError('Enter correct login')
        return cleaned_login


logger.debug('File auth/forms.py loaded')
