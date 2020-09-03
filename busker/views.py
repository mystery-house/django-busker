from datetime import datetime
import logging
import os
from secrets import token_hex

from django.http import HttpResponse, Http404
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import View, FormView
import magic
from .forms import RedeemCodeForm, ConfirmForm
from .models import DownloadCode, File, validate_code
from .util import log_activity

# TODO custom 404 view using base.html for this app https://stackoverflow.com/a/35110595/3280582
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
        if not self.code:
            raise Http404(f"The code {kwargs['download_code']} has already been redeemed or is not valid.")
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
        code.times_used = code.times_used + 1
        code.last_used_date = datetime.now()
        code.save()
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
            # TODO: render 401 in template, improve message
            return HttpResponse("You don't have permission to do that.", status=401)

        file = File.objects.get(id=kwargs['file_id'])
        log_activity(logger, file, "File Downloaded", self.request)

        mime = magic.Magic(mime=True)
        filename = os.path.basename(file.file.path)
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