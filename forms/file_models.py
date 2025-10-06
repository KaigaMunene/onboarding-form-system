"""
File upload model for form attachments.
Supports multiple file uploads per form.
"""

import uuid

from django.core.validators import FileExtensionValidator
from django.db import models

from .validators import FileSizeValidator, FileTypeValidator


class FileUpload(models.Model):
    """
    File upload model for form attachments.
    Supports multiple file uploads per form.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # File details
    file = models.FileField(
        upload_to="form_uploads/%Y/%m/%d/",
        validators=[
            FileExtensionValidator(
                allowed_extensions=["pdf", "doc", "docx", "jpg", "jpeg", "png", "txt"]
            ),
            FileSizeValidator(max_size_mb=10),
            FileTypeValidator(),
        ],
    )
    original_filename = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField()  # in bytes
    content_type = models.CharField(max_length=100)

    # Associated field (optional - for specific field uploads)
    field_name = models.CharField(max_length=100, blank=True)

    # Timestamps
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self):
        return f"{self.original_filename}"

    @property
    def file_size_mb(self):
        """Return file size in MB."""
        return round(self.file_size / (1024 * 1024), 2)
