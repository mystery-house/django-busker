from django.contrib import admin
from .formatters import format_codes_csv
from .models import *

# TODO create admin models, make 'user' field read-only and default to currently logged-in user
# TODO on Artist admin page, display related works
# TODO on Works admin page, display related files and batches
# TODO on Batches page, display related download codes
# TODO make codes, batches, works filterable by artist and other related fields


class BatchAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'private_note', 'work_published')
    actions = ['download_as_csv',]

    def work_published(self, instance):
        """
        Admin list view callback to display the status of this batch's DownloadableWork
        """
        return instance.work.published
    work_published.boolean = True

    def download_as_csv(self, request, queryset):
        """
        Given the first selected batch, look up all of its codes and return as a CSV.
        TODO: Support for multiple selected batches, or return an error if more than one is selected
        """
        queryset = DownloadCode.objects.filter(batch__id__in=queryset.only('id'))
        return format_codes_csv(queryset)
    download_as_csv.short_description = "Export Download Codes for selected batches as CSV"


class DownloadableWorkAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'published')


class DownloadCodeAdmin(admin.ModelAdmin):
    list_display = ('id', 'batch', 'max_uses', 'times_used', 'work_published')
    actions = ['download_as_csv',]

    def work_published(self, instance):
        """
        Admin list view callback to display the status of this code's DownloadableWork
        """
        return instance.batch.work.published
    work_published.boolean = True

    def download_as_csv(self, request, queryset):
        """
        Given a queryset of selected DownloadCode objects, return them in a CSV file.
        """
        return format_codes_csv(queryset)
    download_as_csv.short_description = "Export Selected Download Codes as CSV"


admin.site.register(File)
admin.site.register(DownloadCode, DownloadCodeAdmin)
admin.site.register(DownloadableWork, DownloadableWorkAdmin)
admin.site.register(Artist)
admin.site.register(Batch, BatchAdmin)
