"""Contains functions for formatting Busker data for export
"""

from djqscsv import render_to_csv_response


CSV_DATE_FORMAT = '%Y-%m-%d'


def format_codes_csv(query_set):
    """Given a QuerySet of DownloadCode objects, format it as a CSV file.
    Returns an HttpResponse object containing a CSV file as an attachment.
    """
    header_map = {
        'id': 'download_code',
        'created_date': 'code_created_date',
        'batch__work__artist__name': 'artist',
        'batch__work__title': 'title',
        'max_uses': 'max_uses',
        'times_used': 'times_used',
        'last_used_date': 'last_used_date',
        'batch__label': 'batch_label',
        'batch__created_date': 'batch_created_date',
        'batch__private_note': 'batch_private_note',
        'batch__id': 'batch_id',
        'batch__work__artist__id': 'artist_id',
        'batch__work__id': 'work_id',
    }

    serializer_map = {
        'created_date': (lambda x: x.strftime(CSV_DATE_FORMAT)),
        'batch__created_date': (lambda x: x.strftime(CSV_DATE_FORMAT)),
        'last_used_date': (lambda x: x.strftime(CSV_DATE_FORMAT)),
    }

    return render_to_csv_response(
        query_set.values(
            'id', 'created_date', 'batch__work__artist__name',
            'batch__work__title', 'max_uses', 'times_used', 'last_used_date',
            'batch__label', 'batch__private_note', 'batch__created_date',
            'batch__id', 'batch__work__artist__id', 'batch__work__id'),
        field_header_map=header_map,
        field_serializer_map=serializer_map
    )
