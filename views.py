from datetime import datetime
from django.http import HttpResponse, Http404
from django.shortcuts import render
from django.views.generic import View, TemplateView, FormView
import magic
from .forms import RedeemCodeForm
from .models import DownloadCode, File


# TODO confirmation step that indicates how many uses a code has left / asks user if they're sure they want to use one


# Create your views here.
class RedeemView(TemplateView):
    """
    Handles validating and redeeming a code provided via the URL
    """
    template_name = 'busker/redeem.html'

    def get_context_data(self):
        context_data = super().get_context_data()
        code = self.request.GET.get('code', None)
        if not code:
            raise Http404(f"No code was provided.")

        try:
            download_code = DownloadCode.objects.get(id=code)
            # TODO ^ switch to objects.filter and include date/remaining count as filter criteria
        except DownloadCode.DoesNotExist as e:
            raise Http404(f"The code \"{code}\" does not exist or has already been redeemed.")
            # TODO friendlier error message including contact info

        # We found a code. Add it to the context
        context_data['code'] = download_code
        return context_data


class DownloadView(View):
    def get(self, request, *args, **kwargs):
        code = DownloadCode.objects.get(id=kwargs['download_code'])
        code.times_used = code.times_used + 1
        code.last_used_date = datetime.now()
        code.save()

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
        return render(self.request, 'busker/redeem.html', context=context)
