from django.dispatch import Signal

code_post_redeem = Signal(providing_args=["request", "code"])
file_pre_download = Signal(providing_args=["request", "file"])
