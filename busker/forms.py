from django import forms
from django.core.exceptions import ValidationError
from .models import validate_code


class ConfirmForm(forms.Form):
    code = forms.CharField(widget=forms.HiddenInput)
    # Note that there is currently no cleaning/validation on the confirmation form; it's a hidden input field and under
    # normal conditions the form should not be reachable without a valid code. It is possible-but-unlikely that, in the
    # seconds between a user landing on the confirmation form and clicking the 'Confirm' button, somebody else could
    # redeem the final use of the code, or unpublish the work it's attached to, and in those situations it seems kindest
    # to let the current user proceed rather than yanking the rug out from under them. The DownloadView does not do any
    # checks as to the code redemption count or published flag of the work, so once they've gotten this far the current
    # user can just continue on their way.


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
