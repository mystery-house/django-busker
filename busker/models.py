import os
import random
import string
from uuid import uuid4

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFit
from markdownfield.models import MarkdownField, RenderedMarkdownField
from markdownfield.validators import VALIDATOR_STANDARD

# TODO S3 storage


def validate_code(code):
    try:
        return DownloadCode.objects.get(pk__iexact=code, batch__work__published=True)  # TODO also filter by "max_uses equals 0 OR times_used < max_uses subquery"
    except DownloadCode.DoesNotExist as e:
        return False


def generate_code():
    """
    Utility function that safely generates a new unique 7-character alphanumeric download code object. 36 possible
    characters to the seventh power = 78.4 billion possible codes, which is probably going to be sufficient for any
    reasonable deployment of this app. (If you run out of codes I will be more than happy to accept a pull request
    increasing the code length.)
    """
    new_code = None
    while new_code is None:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=7))
        try:
            DownloadCode.objects.get(pk=code)
        except DownloadCode.DoesNotExist as e:
            new_code = code
    return new_code


def work_image_path(instance, filename):
    return f"busker/downloadable_work_images/{instance.id}/{filename}"


def work_file_path(instance, filename):
    return f"busker/files/{instance.id}/{filename}"


class BuskerModel(models.Model):
    """
    Base model with UUID primary key, optional user, and timestamps.
    """
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.PROTECT)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ('-created_date',)


class Artist(BuskerModel):
    """Artist model"""
    name = models.CharField(max_length=255)
    url = models.URLField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)


class DownloadableWork(BuskerModel):
    """
    Represents an asset that can be downloaded by redeeming a DownloadCode object.
    """
    title = models.CharField(max_length=255,
                             help_text="The title of the work.")
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    image = models.ImageField(null=True, blank=True, help_text="An optional image to be displayed on the code "
                                                               "redemption screen. (For example album art.)",
                              upload_to=work_image_path)
    thumbnail = ImageSpecField(source='image', processors=[ResizeToFit(400, 400)], format='JPEG',
                               options={'quality': 85})
    published = models.BooleanField(default=True,
                                    help_text="DownloadCodes will NOT work if their DownloadableWork is not published.")

    def __str__(self):
        return self.title

    class Meta:
        ordering = ('title', 'artist__name',)


class File(BuskerModel):
    """
    A file that may be attached to a DownloadableWork.
    """
    description = models.CharField(max_length=255,
                                   help_text="A brief description of the file (I.E., \"High-quality 320Kbps MP3\", etc.")
    file = models.FileField(upload_to=work_file_path)
    work = models.ForeignKey(DownloadableWork, on_delete=models.CASCADE)

    @property
    def filename(self):
        return os.path.basename(self.file.name)

    def __str__(self):
        return self.file.name


class Batch(BuskerModel):
    """
    Represents a batch of Download codes generated for a given DownloadableWork object.
    """
    label = models.CharField(max_length=255)
    work = models.ForeignKey(DownloadableWork, on_delete=models.CASCADE)
    private_note = models.TextField(null=True, blank=True, help_text="Optional note for private use; will not be "
                                                                     "displayed to end users.")
    public_message = MarkdownField(null=True, blank=True, validator=VALIDATOR_STANDARD,
                                   rendered_field='public_message_rendered',
                                   help_text="Optional markdown-formatted message that will be displayed on the "
                                             "download page.")
    public_message_rendered = RenderedMarkdownField()
    number_of_codes = models.IntegerField(help_text="The number of Download Codes to be generated with this batch. "
                                                    "(Additional codes may be added to the batch later.)",
                                          default="100")  # TODO place an upper limit?
    max_uses = models.IntegerField(help_text="The number of times this code can be used. (You may subsequently change "
                                             "this amount on individual codes, but this will be used as the initial "
                                             "value.) "
                                             "(0 = unlimited)",
                                   default=3)

    def __str__(self):
        return f"{self.label} -- {self.work.title} by {self.work.artist.name}"

    class Meta:
        verbose_name_plural = "Batches"
        ordering = ('-created_date', 'work__artist__name', 'work__title')


class DownloadCode(BuskerModel):
    """
    Represents an individual download code created for a DownloadableWork.
    """
    # TODO validate ID to ensure uppercase and 0-9 only?
    id = models.CharField(primary_key=True, max_length=7, default=generate_code)
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    max_uses = models.IntegerField(default=3, help_text="This is typically initially determined when a Batch is "
                                                        "originally created, but can be overridden.")
    times_used = models.IntegerField(default=0)
    last_used_date = models.DateTimeField(null=True, blank=True)

    @property
    def remaining_uses(self):
        """
        Indicates the number of uses remaining for a code.
        """
        return self.max_uses - self.times_used

    @property
    def redeem_uri(self):
        """
        The URI that can be used to redeem this code. (Unfortunately there is no convenient way to build
        an absolute URL without a request object.)
        """
        return reverse('busker:redeem', kwargs={'download_code': self.id} )

    def __str__(self):
        return self.id


@receiver(post_save, sender=Batch)
def batch_create(sender, instance, **kwargs):
    """
    post_save receiver for Batch objects; Generates the designated number of DownloadCode objects and attaches them the
    newly-created batch.
    """
    if kwargs['created']:
        for i in range(0, instance.number_of_codes):
            DownloadCode.objects.create(batch=instance, user=instance.user, max_uses=instance.max_uses)
