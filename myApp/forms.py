from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import CustomUser


# class RegistrationForm(UserCreationForm):
#     email = forms.EmailField(required = True)

#     class Meta:
#         model = User
#         fields = ("username", "email", "password1", "password2")
    
#     def save(self, commit = True):
#         user = super(RegistrationForm, self).save(commit=False)
#         user.email = self.cleaned_data['email']

#         if commit:
#             user.save()

#         return user

class RegistrationForm(UserCreationForm):

    class Meta:
        model = CustomUser
        fields = ('firstName', 'lastName', 'username', 'email', 'password1', 'password2')

    def save(self, commit = True):
        user = super(RegistrationForm, self).save(commit = False)
        user.email = self.cleaned_data['email']
        user.firstName = self.cleaned_data['firstName']
        user.lastName = self.cleaned_data['lastName']
        user.isClient = True
        user.isDriver = False

        if commit:
            user.save()
            # Rider.objects.create(rider = user)

        return user    

class RiderUpdateForm(forms.ModelForm):

    username = forms.CharField(max_length=30, required=True)
    firstName = forms.CharField(max_length=30, required=True)
    lastName = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)

    class Meta:
            model = CustomUser
            fields = ('username', 'firstName', 'lastName', 'email')
