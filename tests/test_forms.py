import os
import tempfile

from PIL import Image
from django.core.files import File
from django.test import TestCase

from busker.forms import RedeemCodeForm
from busker.models import Artist, File as BuskerFile, DownloadableWork, Batch
from busker.models import DownloadCode


class RedeemCodeFormTest(TestCase):

    def setUp(self):
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

    def tearDown(self):
        os.unlink(self.img_file.name)
        os.unlink(self.img2_file.name)

    def test_valid_code(self):
        code = DownloadCode.objects.first()
        data = {
            'code': code.id
        }
        form = RedeemCodeForm(data)
        self.assertTrue(form.is_valid())

    def test_invalid_code(self):
        data = {
            'code': 'no_such_code'
        }
        form = RedeemCodeForm(data)
        self.assertFalse(form.is_valid())

    def test_used_code(self):
        """
        Test that a valid code with no remaining uses does not validate
        """
        code = DownloadCode.objects.create(batch=self.batch, max_uses=1, times_used=1)
        data = {
            'code': code.id
        }
        form = RedeemCodeForm(data)
        self.assertFalse(form.is_valid())

    def test_unlimited_code(self):
        """
        Test that times_used > max_uses validates when max_uses is 0
        """
        code = DownloadCode.objects.create(batch=self.batch, max_uses=0, times_used=500)
        data = {
            'code': code.id
        }
        form = RedeemCodeForm(data)
        self.assertTrue(form.is_valid())

    def test_unpublished_work(self):
        """
        Test that a valid code with remaining uses does not validate if the work it's related to is NOT published
        """
        code = DownloadCode.objects.first()
        self.work.published = False
        self.work.save()

        data = {
            'code': code.id
        }
        form = RedeemCodeForm(data)
        self.assertFalse(form.is_valid())
        self.work.published = True
        self.work.save()  # TODO is it necessary to reset this
