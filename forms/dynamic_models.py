"""
Dynamic form models for configurable forms.

This module contains:
- FormField: Dynamic field configuration
- CustomForm: Forms with configurable fields
- FormSubmissionData: Storage for dynamic form data
"""

import uuid

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class FormStatus(models.TextChoices):
    """Status choices for forms."""

    DRAFT = "draft", "Draft"
    SUBMITTED = "submitted", "Submitted"
    UNDER_REVIEW = "under_review", "Under Review"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"
    REQUIRES_CHANGES = "requires_changes", "Requires Changes"


class BaseForm(models.Model):
    """
    Abstract base model for all onboarding forms.

    Provides common functionality:
    - Unique identification
    - Status tracking
    - Timestamps
    - User association
    - Admin notifications
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    # User who submitted the form
    submitted_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="%(class)s_submissions"
    )

    # Status tracking
    status = models.CharField(
        max_length=20, choices=FormStatus.choices, default=FormStatus.DRAFT
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    # Admin notes
    admin_notes = models.TextField(blank=True)

    # Notification tracking
    admin_notified = models.BooleanField(default=False)
    notification_sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} - {self.submitted_by.username}"

    def submit(self):
        """Mark form as submitted and trigger admin notification."""
        self.status = FormStatus.SUBMITTED
        self.submitted_at = timezone.now()
        self.save()
        self.trigger_admin_notification()

    def trigger_admin_notification(self):
        """Trigger async notification to admin."""
        from .notifications import send_admin_notification

        try:
            success = send_admin_notification(self)
            if success:
                self.admin_notified = True
                self.notification_sent_at = timezone.now()
                self.save(update_fields=["admin_notified", "notification_sent_at"])
        except Exception as e:
            # Log error but don't fail the form submission
            import logging

            logger = logging.getLogger(__name__)
            logger.error(
                f"Failed to send admin notification for form {self.id}: {str(e)}"
            )

    def get_form_type(self):
        """Return the form type for display purposes."""
        return self.__class__.__name__

    @property
    def is_editable(self):
        """Check if form can still be edited."""
        return self.status in [FormStatus.DRAFT, FormStatus.REQUIRES_CHANGES]


class FormField(models.Model):
    """
    Dynamic field configuration for forms.
    Allows admins to configure form fields without code changes.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    label = models.CharField(max_length=200)
    field_type = models.CharField(
        max_length=20,
        choices=[
            ("text", "Text"),
            ("number", "Number"),
            ("email", "Email"),
            ("date", "Date"),
            ("dropdown", "Dropdown"),
            ("checkbox", "Checkbox"),
            ("file_upload", "File Upload"),
            ("textarea", "Textarea"),
        ],
    )

    # Field configuration
    is_required = models.BooleanField(default=False)
    placeholder = models.CharField(max_length=200, blank=True)
    help_text = models.TextField(blank=True)

    # For dropdown fields
    choices = models.JSONField(default=list, blank=True)

    # Validation rules
    min_length = models.PositiveIntegerField(null=True, blank=True)
    max_length = models.PositiveIntegerField(null=True, blank=True)
    min_value = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    max_value = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )

    # Field ordering
    order = models.PositiveIntegerField(default=0)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "name"]

    def __str__(self):
        return f"{self.label} ({self.field_type})"


class CustomForm(BaseForm):
    """
    Custom form with dynamic field configuration.
    Allows admins to create forms without code changes.
    """

    # Dynamic field configuration
    fields = models.ManyToManyField(FormField, through="CustomFormField")

    # Form configuration
    allow_multiple_submissions = models.BooleanField(default=False)
    submission_deadline = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Custom Form"
        verbose_name_plural = "Custom Forms"


class CustomFormField(models.Model):
    """Through model for CustomForm and FormField relationship."""

    custom_form = models.ForeignKey(CustomForm, on_delete=models.CASCADE)
    form_field = models.ForeignKey(FormField, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]
        unique_together = ["custom_form", "form_field"]


class FormSubmissionData(models.Model):
    """
    Store dynamic form submission data.
    Used for CustomForm submissions with flexible field structure.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Link to the form submission
    custom_form = models.ForeignKey(CustomForm, on_delete=models.CASCADE)

    # Dynamic data storage
    field_data = models.JSONField(default=dict)

    # File uploads for this submission
    file_uploads = models.ManyToManyField("FileUpload", blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Submission for {self.custom_form.title}"
