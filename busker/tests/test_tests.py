import os
from random import randint
import tempfile

from PIL import Image
from django.core.files import File
from django.test import TestCase
from django.test.client import RequestFactory
from django.urls import reverse

from busker.models import Artist, File as BuskerFile, DownloadCode, DownloadableWork, Batch, work_file_path, work_image_path, \
    validate_code, generate_code
from busker.util import get_client_ip, error_page


# TODO split into per-model TestCase classes, review setUp redundancies

# Create your tests here.
class BuskerTestCase(TestCase):

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
        self.work = DownloadableWork(artist=self.artist, title="Dancing Teeth", published=True, image=self.work_file)
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

    def test_work_image_path(self):
        """
        Tests the expected upload_to value when attaching an image to a DownloadableWork object.
        """
        # (File objects' upload_to method gets called with the base filename)
        img_base_name = os.path.split(self.img_file.name)[-1]
        expected_path = f"busker/downloadable_work_images/{self.work.id}/{img_base_name}"
        self.assertEquals(work_image_path(self.work, img_base_name),
                          expected_path,
                          "Image upload paths should use the format `busker/downloadable_work_images/[downloadable "
                          "work id]/[uploaded img file name]`")

    def test_work_file_path(self):
        """
        Tests the expected upload_to value when attaching a file to a BuskerFile object.
        """
        # (File objects' upload_to method gets called with the base filename)
        file_base_name = os.path.split(self.busker_file_attachment.name)[-1]
        expected_path = f"busker/files/{self.busker_file.id}/{file_base_name}"
        self.assertEquals(work_file_path(self.busker_file, file_base_name),
                          expected_path,
                          "BuskerFile upload paths should use the format `busker/files/[busker file object id]/["
                          "uploaded img file name]`")

    def test_validate_code(self):
        """
        Tests expected behavior of the models.validate_code() method.
        """
        code = self.batch.codes.first()
        # TODO test various conditions (code already used, work is not published)
        self.assertEqual(validate_code(code), code, f"validate_code should have returned the DownloadCode instance "
                                                    f"with an id of `{code.id}`")

        self.assertEqual(validate_code("This is definitely not a valid code"), False, f"validate_code should return "
                                                                                      f"boolean False when given an "
                                                                                      f"invalid code.")

    def test_generate_code(self):
        """
        Verifies that a sampling of codes returned by models.generate_code do not exist in the database.
        """
        for i in range(0, 100):
            code = generate_code()
            with self.assertRaises(DownloadCode.DoesNotExist):
                DownloadCode.objects.get(pk=code)

    def test_artist_str(self):
        self.assertEqual(self.artist.__str__(), self.artist.name, "Artist.__str__() should return the value of the "
                                                                  "name field.")

    def test_downloadable_work_str(self):
        self.assertEqual(self.work.__str__(), self.work.title, "DownloadableWork.__str__() should return the value of "
                                                               "the title field")

    def test_busker_file_str(self):
        self.assertEqual(self.busker_file.__str__(), os.path.basename(self.busker_file.file.name),
                         "BuskerFile.__str__() "
                         "should return the base "
                         "value of the file attached "
                         "to the 'file' field")

    def test_busker_filename(self):
        self.assertEqual(self.busker_file.filename, os.path.basename(self.busker_file.file.name),
                         "BuskerFile.filename() "
                         "should return the base "
                         "value of the file attached "
                         "to the 'file' field")

    def test_batch_str(self):
        expected_value = f"{self.batch.label} -- {self.batch.work.title} by {self.batch.work.artist.name}"
        self.assertEqual(self.batch.__str__(), expected_value, "Batch.__str__() should follow the pattern {label} -- "
                                                               "{work.title} by {work.artist.name}")

    def test_code_remaining_uses(self):
        used = randint(0, 10)
        code = DownloadCode.objects.create(batch=self.batch, max_uses=10, times_used=used)
        self.assertEqual(code.remaining_uses, 10 - used,
                         "DownloadCode.remaining_uses should return the value of max_uses minus times_used")
        code.delete()

    def test_code_redeem_uri(self):
        code = DownloadCode.objects.create(batch=self.batch)
        self.assertEqual(code.redeem_uri, reverse('busker:redeem', kwargs={'download_code': code.id}))
        code.delete()
