import random
import string

from uuid import uuid4
from django.contrib.auth.models import User
from django.db import models


def validate_code(code):
    try:
        return DownloadCode.objects.get(pk=code, batch__work__status=1)  # TODO validate on redemption count and/or date
    except DownloadCode.DoesNotExist as e:
        return False


def generate_code():
    """
    Utility function that safely generates a new unique 7-character alphanumeric download code object 36 possible
    characters to the seventh power 7 = 78.4 billion possible codes, which is probably going to be sufficient for any
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


class BuskerModel(models.Model):
    """
    Base model with UUID, optional user, and timestamps
    """
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.PROTECT)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Artist(BuskerModel):
    """Artist model"""
    name = models.CharField(max_length=255)
    url = models.URLField(null=True, blank=True)

    def __str__(self):
        return self.name


class DownloadableWork(BuskerModel):
    STATUS_CHOICES = ((1, "Published"), (0, "Draft"))
    title = models.CharField(max_length=255,
                             help_text="The title of the work.")
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    status = models.IntegerField(choices=STATUS_CHOICES, default=1,
                                 help_text="Draft items will not be available for download.")

    def __str__(self):
        return self.title


class File(BuskerModel):
    """
    A file that may be attached to a DownloadableWork
    """
    description = models.CharField(max_length=255,
                                   help_text="A brief description of the file (I.E., \"High-quality 320Kbps MP3\", etc.")
    file = models.FileField()  # TODO per-user destination path, S3 backend
    work = models.ForeignKey(DownloadableWork, on_delete=models.CASCADE)
    # TODO sort order?


class Batch(BuskerModel):
    """
    Represents a batch of Download codes generated for a given DownloadableWork object.
    """
    label = models.CharField(max_length=255)
    work = models.ForeignKey(DownloadableWork, on_delete=models.CASCADE)
    note = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.label} -- {self.work.title} by {self.work.artist.name}"


class DownloadCode(BuskerModel):
    """
    Represents an individual download code created for a DownloadableWork
    """
    id = models.CharField(primary_key=True, max_length=7, default=generate_code)
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    last_used_date = models.DateTimeField(null=True, blank=True)
    times_used = models.IntegerField(default=0)
    max_uses = models.IntegerField(default=3, help_text="The maximum number of times the code can be used. (0 = "
                                                        "Unlimited)")
    days_valid = models.IntegerField(default=0,
                                     help_text="The number of days the code will remain usable after its last use "
                                               "(0 = Never expires)")

    def __str__(self):
        return self.id

    @staticmethod
    def new(**kwargs):
        new_code = None
        while new_code is None:
            try:
                kwargs['code'] = generate_code()
                new_code = DownloadCode.objects.create(kwargs)
            except Exception as e:
                print(e)
        return new_code

