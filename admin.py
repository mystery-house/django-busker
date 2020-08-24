from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(File)
admin.site.register(DownloadCode)
admin.site.register(DownloadableWork)
admin.site.register(Artist)
admin.site.register(Batch)