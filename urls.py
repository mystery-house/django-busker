from django.urls import path
from .views import RedeemFormView, DownloadView

app_name = 'busker'
urlpatterns = [
    path('redeem/', RedeemFormView.as_view(), name='redeem'),
    path('download/<str:file_id>/<str:download_code>', DownloadView.as_view(), name='download')
]
