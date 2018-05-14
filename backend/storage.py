"""
Adapted from
http://condopilot.com/blog/web/how-setup-gzip-compressor-and-aws-s3-django/
"""

from django.core.files.storage import get_storage_class
from storages.backends.s3boto import S3BotoStorage
from backend.settings import STATICFILES_LOCATION


class CachedS3BotoStorage(S3BotoStorage):
    """
    S3 storage backend that caches files locally (on the same server as the
    Django application), too (so we can see what static files have changed
    and whether a new compressed version needs to be created).
    """
    location = STATICFILES_LOCATION

    def __init__(self, *args, **kwargs):
        super(CachedS3BotoStorage, self).__init__(*args, **kwargs)
        self.local_storage = get_storage_class(
            "compressor.storage.CompressorFileStorage")()

    def save(self, name, content):
        """
        A workaround to save non-gzipped content locally.
        """
        non_gzipped_file_content = content.file
        name = super(CachedS3BotoStorage, self).save(name, content)
        content.file = non_gzipped_file_content
        self.local_storage._save(name, content)
        return name
