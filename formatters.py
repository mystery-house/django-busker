"""
Contains functions for formatting Busker data for export
"""

from djqscsv import render_to_csv_response


def format_codes_csv(query_set):
    """
    Given a QuerySet of DownloadCode objects, format it as a CSV file. Returns an HttpResponse object containing a
    CSV file as an attachment.
    TODO: Would be nice to be able to include the URI and/or full URL, remaining_uses per code
    """
    header_map = {
        'id': 'download_code',
        'batch__work__artist__name': 'artist',
        'batch__work__title': 'title',
        # 'max_uses': 'max_uses',
        # 'times_used': 'times_used',
        # 'last_used_date': 'last_used_date',
        'batch__id': 'batch_id',
        'batch__work__artist__id': 'artist_id',
        'batch__work__id': 'work_id',
    }

    return render_to_csv_response(query_set.values('id', 'batch__work__artist__name', 'batch__work__title', 'max_uses',
                                                   'times_used', 'last_used_date', 'batch__id',
                                                   'batch__work__artist__id', 'batch__work__id'),
                                  field_header_map=header_map)
