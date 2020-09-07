from datetime import datetime
import logging
import os
from secrets import token_hex

from django.http import HttpResponse, Http404
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django.views.generic import View, FormView

import magic
from .forms import RedeemCodeForm, ConfirmForm
from .models import DownloadCode, File, validate_code
from .signals import code_post_redeem, file_pre_download
from .util import error_page, log_activity

logger = logging.getLogger(__name__)


class RedeemView(FormView):
    """
    Handles validating, confirming and redeeming a code provided via the URL
    """
    template_name = 'busker/confirm_form.html'
    form_class = ConfirmForm
    code = None

    def get(self, *args, **kwargs):
        """
        Validates the code provided as URL argument
        """
        self.code = validate_code(kwargs['download_code'])
        if not self.code:  # TODO instead of 404, use messages to display error and redirect to the redeem form view
            return error_page(self.request, 404, "Invalid Code",
                              f"The code {kwargs['download_code']} has already been redeemed or is not valid.")
        return self.render_to_response(self.get_context_data())

    def get_initial(self):
        initial = super().get_initial()
        initial['code'] = self.code
        return initial

    def get_context_data(self):
        context_data = super().get_context_data()
        context_data['code'] = self.code
        return context_data

    def form_valid(self, form):
        """
        Once the form has been submitted, increment the usage count and display the list of downloadable files.
        """
        code = DownloadCode.objects.get(id=form.cleaned_data['code'], batch__work__published=True)
        code.redeem(request=self.request)
        # Save a token in the session which will subsequently be used to validate download links:
        self.request.session['busker_download_token'] = token_hex(16)
        self.request.session.modified = True
        log_activity(logger, code, "Code Redeemed", self.request)
        context = self.get_context_data()
        context['code'] = code
        return render(self.request, 'busker/file_list.html', context=context)


class DownloadView(View):
    """
    Handles the actual downloading of files.
    """
    def get(self, request, *args, **kwargs):
        if 'busker_download_token' not in request.session \
                or request.GET.get('t') != request.session['busker_download_token']:
            return error_page(request, 401, "Unauthorized", "You do not have permission to access this resource.")

        try:
            file = File.objects.get(id=kwargs['file_id'])
        except File.DoesNotExist:
            return error_page(self.request, 404, "No Such File", "The file you requested does not exist.")
        log_activity(logger, file, "File Downloaded", self.request)

        mime = magic.Magic(mime=True)
        filename = os.path.basename(file.file.path)
        file_pre_download.send(sender=self.__class__, request=self.request, file=file)
        response = HttpResponse(file.file, content_type=mime.from_file(file.file.path))
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        response['Content-Length'] = file.file.size
        return response


class RedeemFormView(FormView):
    """
    Simple form for manual entry of a code. Does not validate anything on submission; validation happens in RedeemView
    """
    form_class = RedeemCodeForm
    template_name = 'busker/redeem_form.html'
    entered_code = None

    def form_valid(self, form):
        self.entered_code = form.cleaned_data['code']
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('busker:redeem', kwargs={'download_code': self.entered_code})
