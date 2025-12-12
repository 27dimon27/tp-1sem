import os
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import transaction
from .models import Profile, Question, Answer, Tag

MAX_TAGS_COUNT = 5
MAX_AVATAR_SIZE = 2 * 1024 * 1024
ALLOWED_IMAGE_EXTENSIONS = ["jpg", "jpeg", "png", "gif"]


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Enter your login"}
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Enter your password"}
        )
    )


class SignupForm(UserCreationForm):
    password1 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Enter your password"}
        ),
    )
    password2 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Repeat your password"}
        ),
    )
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter your email (optional)",
            }
        ),
    )
    avatar = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={"class": "form-control"}),
        validators=[
            FileExtensionValidator(allowed_extensions=ALLOWED_IMAGE_EXTENSIONS),
        ],
    )

    def clean_avatar(self):
        avatar = self.cleaned_data.get("avatar")
        if avatar:
            if avatar.size > MAX_AVATAR_SIZE:
                raise ValidationError(
                    f"File size must be less than {MAX_AVATAR_SIZE // (1024 * 1024)}MB"
                )

            ext = os.path.splitext(avatar.name)[1][1:].lower()
            if ext not in ALLOWED_IMAGE_EXTENSIONS:
                raise ValidationError(
                    f"Allowed file extensions: {', '.join(ALLOWED_IMAGE_EXTENSIONS)}"
                )

        return avatar

    class Meta:
        model = User
        fields = ["username", "email"]
        widgets = {
            "username": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter your username"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.pop("autofocus", None)

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
            profile = Profile.objects.create(user=user)
            if self.cleaned_data.get("avatar"):
                profile.avatar = self.cleaned_data["avatar"]
                profile.save()
        return user


class AskForm(forms.ModelForm):
    tags = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter tags separated by commas",
            }
        ),
        help_text="Enter tags separated by commas",
    )

    class Meta:
        model = Question
        fields = ["title", "text"]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter your question title",
                }
            ),
            "text": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 8,
                    "placeholder": "Describe your question in detail",
                }
            ),
        }

    def clean_tags(self):
        tags_input = self.cleaned_data.get("tags", "")
        if not tags_input:
            return []

        tag_names = [tag.strip() for tag in tags_input.split(",") if tag.strip()]
        if not tag_names:
            return []

        if len(tag_names) > 5:
            raise ValidationError(f"You can add up to {MAX_TAGS_COUNT} tags")

        for tag_name in tag_names:
            if len(tag_name) > 50:
                raise ValidationError(
                    f"Tag '{tag_name}' is too long, max length is 50 characters"
                )

            if not tag_name.replace("_", "").replace("-", "").isalnum():
                raise ValidationError(
                    f"Tag '{tag_name}' contains invalid characters. Use letters, numbers, underscores and hyphens"
                )

        return tag_names

    @transaction.atomic
    def save(self, commit=True, author=None):
        question = super().save(commit=False)
        if author:
            question.author = author

        if commit:
            question.save()

            tag_names = self.cleaned_data["tags"]
            if tag_names:
                existing_tag_names = Tag.objects.filter(name__in=tag_names).values_list(
                    "name", flat=True
                )
                existing_tag_names = set(existing_tag_names)

                new_tags = [
                    Tag(name=name)
                    for name in tag_names
                    if name not in existing_tag_names
                ]
                Tag.objects.bulk_create(new_tags)

                tags = Tag.objects.filter(name__in=tag_names)
                question.tags.set(tags)

        return question


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ["text"]
        widgets = {
            "text": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 8,
                    "placeholder": "Type your answer here...",
                }
            ),
        }

    def clean_text(self):
        text = self.cleaned_data.get("text")
        if not text or len(text.strip()) == 0:
            raise ValidationError("Answer text cannot be empty")
        return text


class SettingsForm(forms.ModelForm):
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter your email (optional)",
            }
        ),
    )

    class Meta:
        model = User
        fields = ["email", "username"]
        widgets = {
            "username": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter your username"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields["email"].initial = self.instance.email

    def save(self, commit=True):
        user = super().save(commit=False)
        if self.cleaned_data.get("email"):
            user.email = self.cleaned_data["email"]

        if commit:
            user.save()
        return user


class ProfileForm(forms.ModelForm):
    avatar = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={"class": "form-control"}),
        validators=[
            FileExtensionValidator(allowed_extensions=ALLOWED_IMAGE_EXTENSIONS),
        ],
    )

    def clean_avatar(self):
        avatar = self.cleaned_data.get("avatar")
        if avatar:
            if avatar.size > MAX_AVATAR_SIZE:
                raise ValidationError(
                    f"File size must be less than {MAX_AVATAR_SIZE // (1024 * 1024)}MB"
                )

            ext = os.path.splitext(avatar.name)[1][1:].lower()
            if ext not in ALLOWED_IMAGE_EXTENSIONS:
                raise ValidationError(
                    f"Allowed file extensions: {', '.join(ALLOWED_IMAGE_EXTENSIONS)}"
                )

        return avatar

    class Meta:
        model = Profile
        fields = ["avatar"]
        widgets = {
            "avatar": forms.FileInput(attrs={"class": "form-control"}),
        }
