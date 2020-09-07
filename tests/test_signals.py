import os
import tempfile
from secrets import token_hex

from PIL import Image
from django.core.files import File
from django.test import TestCase
from django.test.client import RequestFactory
from django.urls import reverse

from busker.models import Artist, File as BuskerFile, DownloadableWork, Batch
from busker.models import DownloadCode
from busker.signals import code_post_redeem, file_pre_download


class TestSignals(TestCase):

    def setUp(self):
        self.factory = RequestFactory()

        # Create a couple of images to use for the downloadable work and BuskerFile objects
        self.img = Image.new("RGB", (1200, 1200), "#990000")
        self.img_file = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
        self.img_basename = os.path.split(self.img_file.name)[-1]
        self.img.save(self.img_file, format="JPEG")

        self.img2 = Image.new("RGB", (5000, 5000), "#336699")
        self.img2_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        self.img2_basename = os.path.split(self.img2_file.name)[-1]
        self.img2.save(self.img2_file, format="PNG")

        self.artist = Artist.objects.create(name="Conrad Poohs", url="https://magicians.band")
        self.work_file = File(self.img_file)
        self.work = DownloadableWork(artist=self.artist, title="Dancing Teeth", published=True,
                                     image=self.work_file)
        self.work.image.save(name=self.img_basename, content=self.img_file)
        self.work.save()

        self.busker_file_attachment = File(self.img2_file)
        self.busker_file = BuskerFile(work=self.work, description="", file=self.busker_file_attachment)
        self.busker_file.file.save(name=self.img2_basename, content=self.img2_file)
        self.busker_file.save()
        self.batch = Batch.objects.create(
            work=self.work,
            label="Conrad Poohs Test Batch",
            private_note="Batch for unit testing",
            public_message="#Thank You\nThis is a message with *markdown* **formatting**.",
            number_of_codes=10
        )

        self.unpub_work = DownloadableWork.objects.create(title="Unpublished", artist=self.artist, published=False)
        self.unpub_batch = Batch.objects.create(label="unpublished",
                                                work=self.unpub_work,
                                                number_of_codes=1,
                                                public_message='test')

        self.unpub_code = DownloadCode.objects.get(batch=self.unpub_batch)
        self.used_code = DownloadCode.objects.create(batch=self.batch, max_uses=1, times_used=1)

    def tearDown(self):
        os.unlink(self.img_file.name)
        os.unlink(self.img2_file.name)

    def test_code_redeem(self):
        """
        Tests that the code_post_redeem signal is sent
        """
        code = DownloadCode.objects.create(batch=self.batch)

        self.code_redeem_signal_received = False

        def redeem_handler(sender, **kwargs):
            self.code_redeem_signal_received = True
        code_post_redeem.connect(redeem_handler)
        code.redeem()
        self.assertTrue(self.code_redeem_signal_received)

    def test_file_downloaded(self):
        """
        Tests that the file_pre_download signal is sent
        """
        session = self.client.session
        token = token_hex(16)
        session['busker_download_token'] = token
        session.save()

        self.file_download_signal_received = False

        def download_handler(sender, **kwargs):
            self.file_download_signal_received = True
        file_pre_download.connect(download_handler)

        self.client.get(reverse('busker:download', kwargs={'file_id': self.busker_file.id}) + f'?t={token}')
        self.assertTrue(self.file_download_signal_received)


