from django.dispatch import Signal


# TODO https://stackoverflow.com/a/18532655/3280582
#: The ``code_post_redeem`` signal expects two arguments:
#:  ``request`` (A :py:class:`~django.http.HttpRequest` object) and
#:  ``code`` (An instance of :py:class:`~models.DownloadCode`.)
code_post_redeem = Signal()
#: The ``file_pre_download`` signal expects two arguments:
#: ``request`` (A :py:class:`~django.http.HttpRequest` object) and
#: ``file`` (An instance of :py:class:`~models.File`.)
file_pre_download = Signal()
