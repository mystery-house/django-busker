import os
import tempfile

from PIL import Image
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User
from django.core.files import File
from django.test import TestCase
from django.urls import reverse

from busker.admin import BatchAdmin, DownloadCodeAdmin
from busker.models import Artist, File as BuskerFile, DownloadCode, DownloadableWork, Batch


class BatchAdminTestCase(TestCase):

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
        user = User.objects.create_superuser(
            username='test',
            password='test',
        )
        self.client.force_login(user)

    def test_batch_admin_work_published(self):
        batch_admin = BatchAdmin(model=Batch, admin_site=AdminSite())
        # Test True
        self.assertTrue(batch_admin.work_published(instance=self.batch))

        # Test False
        work = DownloadableWork.objects.create(title="Unpublished Work Title", published=False, artist=self.artist)
        batch_2 = Batch.objects.create(work=work, label="test", public_message="")
        self.assertFalse(batch_admin.work_published(instance=batch_2))

    def test_batch_admin_download_as_csv(self):
        """
        Tests that the 'Download CSV' batch admin option returns CSV data.
        TODO: Would be good to test the actual data
        """
        to_download = Batch.objects.values_list('pk', flat=True)
        data = {
            'action': 'download_as_csv',
            '_selected_action': to_download
        }
        url = reverse('admin:busker_batch_changelist')
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get('Content-type'), 'text/csv')
        self.assertEqual(response.get('Content-Disposition'), 'attachment; filename=downloadcode_export.csv;')


class DownloadCodeAdminTestCase(TestCase):

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
        user = User.objects.create_superuser(
            username='test',
            password='test',
        )
        self.client.force_login(user)

    def test_code_admin_work_published(self):
        code_admin = DownloadCodeAdmin(model=DownloadCode, admin_site=AdminSite())
        # Test Code for published work
        code = DownloadCode.objects.filter(batch=self.batch, batch__work__published=True).first()
        self.assertTrue(code_admin.work_published(instance=code))

        # Test Code  for unpublished work
        work = DownloadableWork.objects.create(title="Unpublished", artist=self.artist, published=False)
        unpub_batch = Batch.objects.create(work=work, label="Unpublished test", public_message="")
        code2 = DownloadCode.objects.create(batch=unpub_batch)
        self.assertFalse(code_admin.work_published(instance=code2))

    def test_code_admin_download_as_csv(self):
        """
        Tests that the 'Download CSV' batch admin option returns CSV data.
        TODO: Would be good to test the actual data
        """
        to_download = DownloadCode.objects.values_list('pk', flat=True)
        data = {
            'action': 'download_as_csv',
            '_selected_action': to_download
        }
        url = reverse('admin:busker_downloadcode_changelist')
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get('Content-type'), 'text/csv')
        self.assertEqual(response.get('Content-Disposition'), 'attachment; filename=downloadcode_export.csv;')


