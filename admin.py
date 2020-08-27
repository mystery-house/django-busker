from django.contrib import admin
from .models import *

# TODO create admin models, make 'user' field read-only and default to currently logged-in user
# TODO on Artist admin page, display related works
# TODO on Works admin page, display related files and batches
# TODO on Batches page, display related download codes
# TODO create "download CSV" / "download excel" / "download QR codes" actions for the batches page


class BatchAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'private_note', 'work_status')

    def work_status(self, instance):
        """
        Admin list view callback to display the status of this batch's DownloadableWork
        """
        return instance.work.status


class DownloadCodeAdmin(admin.ModelAdmin):
    list_display = ('id', 'batch', 'max_uses', 'times_used', 'work_status')

    def work_status(self, instance):
        """
        Admin list view callback to display the status of this code's DownloadableWork
        """
        return instance.batch.work.status


admin.site.register(File)
admin.site.register(DownloadCode, DownloadCodeAdmin)
admin.site.register(DownloadableWork)
admin.site.register(Artist)
admin.site.register(Batch, BatchAdmin)
