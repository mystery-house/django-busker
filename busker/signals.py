from django.dispatch import Signal

# TODO review README signal documentation / determine ramifications of request object possibly being 'None'
code_post_redeem = Signal(providing_args=["request", "code"])
file_pre_download = Signal(providing_args=["request", "file"])
