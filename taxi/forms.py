from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.exceptions import ValidationError

from taxi.models import Car
from taxi.validators import validate_license_number


class CarForm(forms.ModelForm):
    drivers = forms.ModelMultipleChoiceField(
        queryset=get_user_model().objects.all(),
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = Car
        fields = "__all__"


class DriverBaseForm(forms.ModelForm):
    license_number = forms.CharField(
        validators=[validate_license_number],
        help_text=(
            "License number must be exactly 8 characters long. "
            "License number must start with 3 letters. "
            "License number must end with 4 digits."
        )
    )

    class Meta:
        model = get_user_model()
        fields = (
            "username",
            "license_number",
            "first_name",
            "last_name",
            "email",
        )


class DriverCreateForm(UserCreationForm, DriverBaseForm):
    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = DriverBaseForm.Meta.fields + ("password1", "password2")


class DriverUpdateForm(UserChangeForm, DriverBaseForm):
    current_password = forms.CharField(
        widget=forms.PasswordInput,
        label="Current Password",
        help_text="Enter your current password to confirm changes."
    )

    def __init__(self, *args, **kwargs):
        super(DriverUpdateForm, self).__init__(*args, **kwargs)
        if "password" in self.fields:
            del self.fields["password"]

    def clean_current_password(self):
        current_password = self.cleaned_data.get("current_password")
        if not self.instance.check_password(current_password):
            raise ValidationError("Current password is incorrect.")
        return current_password

    class Meta(UserChangeForm.Meta):
        model = get_user_model()
        fields = DriverBaseForm.Meta.fields


class DriverLicenseUpdateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(DriverLicenseUpdateForm, self).__init__(*args, **kwargs)
        self.fields["license_number"] = DriverBaseForm.base_fields[
            "license_number"
        ]

    class Meta:
        model = get_user_model()
        fields = ("license_number",)
