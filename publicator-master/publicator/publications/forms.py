from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django import forms
from publications.models import Publication, Author, Edition, Category, Tags

User = get_user_model()


class AuthorForm(UserCreationForm):
    affiliation = forms.CharField(
        max_length=256,
        label="Аффилиация",
        required=True
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = [
            'username',
            'email',
            'first_name',
            'last_name',
            'password1',
            'password2',
            'affiliation'
        ]

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            Author.objects.create(
                user=user,
                affiliation=self.cleaned_data['affiliation']
            )
        return user


class UserEditForm(forms.ModelForm):
    affiliation = forms.CharField(
        max_length=256,
        label="Аффилиация",
        required=True
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = [
            'email',
            'first_name',
            'last_name',
            'affiliation'
        ]


class PublicationForm(forms.ModelForm):
    class Meta:
        fields = '__all__'
        widgets = {
            'pub_date': forms.DateInput(attrs={'type': 'date'}),
            'text': forms.Textarea
        }
        model = Publication


class EditionForm(forms.ModelForm):
    class Meta:
        fields = '__all__'
        widgets = {
            'pub_date': forms.DateInput(attrs={'type': 'date'}),
            'text': forms.Textarea
        }
        model = Edition


class CategoryForm(forms.ModelForm):
    class Meta:
        fields = '__all__'
        widgets = {
            'pub_date': forms.DateInput(attrs={'type': 'date'}),
            'text': forms.Textarea
        }
        model = Category


class ApplicationForm(forms.ModelForm):
    class Meta:
        exclude = ['application', 'is_published', 'pub_date']
        widgets = {
            'pub_date': forms.DateInput(attrs={'type': 'date'}),
            'text': forms.Textarea
        }
        model = Publication

class TagsForm(forms.ModelForm):
    class Meta:
        fields = '__all__'
        model = Tags
