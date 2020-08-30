from django import forms
from django.core.exceptions import ValidationError
from .models import validate_code


class ConfirmForm(forms.Form):
    code = forms.CharField(widget=forms.HiddenInput)


class RedeemCodeForm(forms.Form):
    code = forms.CharField(max_length=7, label="Enter Your Download Code Here")
    code_object = None

    def clean_code(self):
        """
        Custom clean method for the `code` field; checks that the code entered is valid.
        """
        submitted_code = self.cleaned_data['code']
        validated_code = validate_code(submitted_code)
        if validated_code is False:
            raise ValidationError("The code you entered is not valid, or has already been redeemed.")
        self.code_object = validated_code
        return submitted_code
