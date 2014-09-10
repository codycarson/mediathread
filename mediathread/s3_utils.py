from compressor.filters.css_default import CssAbsoluteFilter
from compressor.utils import staticfiles
from storages.backends.s3boto import S3BotoStorage
from django.core.files.storage import get_storage_class
from django.conf import settings


MediaRootS3BotoStorage = lambda: S3BotoStorage(
    bucket_name=settings.AWS_MEDIA_BUCKET_NAME
)


class CachedStaticRootS3BotoStorage(S3BotoStorage):
    """
    S3 storage backend that saves the files locally, too.
    """
    def __init__(self, acl=None, bucket=None, **settings):
        settings['reduced_redundancy'] = True
        bucket = settings.AWS_STATIC_BUCKET_NAME
        super(CachedStaticRootS3BotoStorage, self).__init__(acl, bucket, **settings)
        self.local_storage = get_storage_class(
            "compressor.storage.CompressorFileStorage")()

    def save(self, name, content):
        name = super(CachedStaticRootS3BotoStorage, self).save(name, content)
        self.local_storage._save(name, content)
        return name


class CustomCssAbsoluteFilter(CssAbsoluteFilter):
    def find(self, basename):
        # The line below is the original line.  I removed settings.DEBUG.
        # if settings.DEBUG and basename and staticfiles.finders:
        if basename and staticfiles.finders:
            return staticfiles.finders.find(basename)
