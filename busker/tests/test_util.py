import logging
from uuid import uuid4

from django.test import TestCase
from django.test.client import RequestFactory
from django.urls import reverse
from django.utils.html import escape

from busker.models import DownloadCode
from busker.util import get_client_ip, error_page, log_activity


class UtilTestCase(TestCase):
    """
    Tests for the busker.util module
    """

    def setUp(self):
        self.factory = RequestFactory()

    def test_get_client_ip(self):
        request = self.factory.get(reverse('busker:redeem_form'), REMOTE_ADDR='123.145.167.189')
        self.assertEqual(get_client_ip(request), '123.145.167.189')

        request = self.factory.get(reverse('busker:redeem_form'), REMOTE_ADDR='127.0.0.1',
                                   HTTP_X_FORWARDED_FOR='123.145.167.189')
        self.assertEqual(get_client_ip(request), '123.145.167.189', "get_client_ip() should correctly handle the "
                                                                    "X_FORWARDED_FOR header")

    def test_error_page(self):
        test_status = 418
        test_title = "I'm a teapot"
        test_message = "may be short and stout"

        request = self.factory.get(reverse('busker:redeem', kwargs={'download_code': 'no_such_code'}))
        response = error_page(request, test_status, test_title, test_message)
        self.assertContains(response, escape(test_title), status_code=test_status)
        self.assertContains(response, test_message, status_code=test_status)

    def test_log_activity(self):
        request = self.factory.get(reverse('busker:redeem_form'), HTTP_USER_AGENT=__name__)
        logger = logging.getLogger(__name__)

        code = DownloadCode()

        with self.assertLogs() as cm:
            log_activity(logger, code, "This is a test log entry", request, logging.INFO)
