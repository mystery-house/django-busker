from datetime import datetime
from django.http import HttpResponse, Http404
from django.shortcuts import render
from django.views.generic import View, TemplateView, FormView
import magic
from .forms import RedeemCodeForm, ConfirmForm
from .models import DownloadCode, File, validate_code


# TODO confirmation step that indicates how many uses a code has left / asks user if they're sure they want to use one


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
        code = DownloadCode.objects.get(id=form.cleaned_data['code'], batch__work__status=1)
        code.times_used = code.times_used + 1
        code.last_used_date = datetime.now()
        code.save()

        context = self.get_context_data()
        context['code'] = code
        return render(self.request, 'busker/file_list.html', context=context)


class DownloadView(View):  # TODO validate against a token set in the session
    def get(self, request, *args, **kwargs):
        file = File.objects.get(id=kwargs['file_id'])
        mime = magic.Magic(mime=True)

        response = HttpResponse(file.file, content_type=mime.from_file(file.file.path))
        response['Content-Disposition'] = f'attachment; filename="{file.file.name}"'
        response['Content-Length'] = file.file.size
        return response


class RedeemFormView(FormView):
    form_class = RedeemCodeForm
    template_name = 'busker/redeem_form.html'

    def form_valid(self, form):
        context = self.get_context_data()
        context['code'] = form.code_object
        # TODO: redirect to the redemption URL
