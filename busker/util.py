"""
Contains various utility functions used by the busker app.
"""
from logging import INFO
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone


def get_client_ip(request):
    """
    Attempts to get client IP address; Courtesy of yanchenko https://stackoverflow.com/a/4581997
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def log_activity(logger, obj, message, request, level=INFO):
    """
    Logs busker-related activity in a consistent format, with the following information separated by tabs:
    - date + time (in common log format)
    - message
    - object as string*
    - object ID
    - client IP address
    - client user agent

    *In the case of DownloadCode objects, the ID and object-as-string will be the same.
    """
    logger.log(
        level,
        f"[{timezone.now().strftime('%d/%b/%Y:%H:%M:%S')}]\t{message}\t{str(obj)}\t{obj.pk}\t"
        f"{get_client_ip(request)}\t{request.META['HTTP_USER_AGENT']}"
    )


def error_page(request, status, title, message):
    """
    Given an HTTP status code, page title, and error message, returns a rendered HttpResponse object.
    """
    context = {'status': status, 'title': title, 'message': message}
    return HttpResponse(render(request, 'busker/error.html', context=context), status=status)
