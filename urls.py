from django.urls import path
from .views import RedeemView, RedeemFormView, DownloadView

app_name = 'busker'
urlpatterns = [
    path('redeem/<str:download_code>/', RedeemView.as_view(), name='redeem'),
    path('', RedeemFormView.as_view(), name='redeem_form'),
    path('download/<str:file_id>/', DownloadView.as_view(), name='download')
]
