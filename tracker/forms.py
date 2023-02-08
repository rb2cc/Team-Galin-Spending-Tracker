from django.core.validators import validate_email
from django.core.validators import RegexValidator
from django import forms

from .models import User
from django.contrib.auth.forms import UserChangeForm, UserCreationForm, PasswordResetForm


from .models import User, Expenditure, Category


class LogInForm(forms.Form):
    """Form enabling registered users to log in."""
    email = forms.CharField(label='', widget=forms.TextInput(attrs={'placeholder': 'Email'}))
    password = forms.CharField(label='', widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))


class SignUpForm(forms.ModelForm):
    """Form enabling unregistered users to sign up."""

    class Meta:
        """Form options."""

        model = User
        fields = ['first_name', 'last_name']

    first_name = forms.CharField(label='', widget=forms.TextInput(attrs={'placeholder': 'First Name'}))
    last_name = forms.CharField(label='', widget=forms.TextInput(attrs={'placeholder': 'Last Name'}))
    email = forms.CharField(label='', validators=[validate_email] , widget=forms.TextInput(attrs={'placeholder': 'Email'}))
    new_password = forms.CharField(
        label='',
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'}),
        validators=[RegexValidator(
            regex=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).*$',
            message='Password must contain an uppercase character, a lowercase character, a number.'
        )]
    )
    password_confirmation = forms.CharField(
        label='', widget=forms.PasswordInput(attrs={'placeholder': 'Password Comfirmation'}))

    def clean(self):
        """Clean the data and generate messages for any errors."""

        super().clean()
        new_password = self.cleaned_data.get('new_password')
        password_confirmation = self.cleaned_data.get('password_confirmation')
        if new_password != password_confirmation:
            self.add_error('password_confirmation', 'Confirmation does not match password.')

    def save(self):
        """Create a new user."""

        super().save(commit=False)
        user = User.objects.create_user(
            self.cleaned_data.get('email'),
            first_name=self.cleaned_data.get('first_name'),
            last_name=self.cleaned_data.get('last_name'),
            password=self.cleaned_data.get('new_password')
        )
        return user



class EditUserForm(UserChangeForm):

    email = forms.CharField(
        max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(
        max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(
        max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    # date_joined = forms.CharField(
    #     max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = None

    class Meta:
        """Form options."""

        model = User
        fields = ['email', 'first_name', 'last_name']

class ExpenditureForm(forms.ModelForm):
    """Form enabling users to create expenditures"""
    class Meta:
        """Form options"""
        model = Expenditure
        fields = ['title','expense','description', 'category', 'image']

    description = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%; height:10%'}))
    expense = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%; height:10%'}))
    title = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%; height:10%'}))
        
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("r")
        super(ExpenditureForm, self).__init__(*args, **kwargs)

        #initialises the category queryset so it only shows categories the user is subscribed to (fixes glitch)
        self.fields['category'].queryset = Category.objects.filter(users__id=self.request.user.id)
    # description = forms.CharField(label="Description", widget=forms.CharField(attrs={'size':100}))
    # field_order=['title', 'description', 'expense']

class UserPasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super(UserPasswordResetForm, self).__init__(*args, **kwargs)
    email = forms.EmailField(label='', widget=forms.EmailInput(attrs={'placeholder': 'Email',}))

class AddCategoryForm(forms.ModelForm):
    """Form enabling users to create custom categories"""
    class Meta:
        """Form options."""
        model = Category
        fields = ['name', 'week_limit']

    name = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%; height:10%'}))
    week_limit = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%; height:10%'}))


