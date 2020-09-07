from django.dispatch import Signal

# TODO https://stackoverflow.com/a/18532655/3280582
code_post_redeem = Signal(providing_args=["request", "code"])
file_pre_download = Signal(providing_args=["request", "file"])
