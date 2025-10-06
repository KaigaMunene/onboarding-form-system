"""
Notification system for form submissions.

This module provides:
- Email notifications to admins
- Async task handling (placeholder for Celery)
- Notification templates
"""

import logging

from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


def send_admin_notification(form_instance):
    """
    Send notification to admins when a form is submitted.

    Args:
        form_instance: The form instance that was submitted
    """
    try:
        # Get all admin users
        admin_users = User.objects.filter(is_staff=True, is_active=True)
        admin_emails = [user.email for user in admin_users if user.email]

        if not admin_emails:
            logger.warning("No admin emails found for notification")
            return False

        # Prepare email content
        subject = f"New Form Submission: {form_instance.get_form_type()}"

        context = {
            "form": form_instance,
            "form_type": form_instance.get_form_type(),
            "submitted_by": form_instance.submitted_by,
            "submission_date": form_instance.submitted_at or form_instance.created_at,
            "admin_url": f"/admin/forms/{form_instance._meta.model_name}/{form_instance.id}/change/",
        }

        # Render email templates
        html_message = render_to_string("forms/emails/admin_notification.html", context)
        plain_message = render_to_string("forms/emails/admin_notification.txt", context)

        # Send email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@example.com"),
            recipient_list=admin_emails,
            html_message=html_message,
            fail_silently=False,
        )

        logger.info(f"Admin notification sent for form {form_instance.id}")
        return True

    except Exception as e:
        logger.error(f"Failed to send admin notification: {str(e)}")
        return False


def send_user_notification(form_instance, notification_type="status_update"):
    """
    Send notification to user about form status changes.

    Args:
        form_instance: The form instance
        notification_type: Type of notification ('status_update', 'approved', 'rejected', etc.)
    """
    try:
        user_email = form_instance.submitted_by.email
        if not user_email:
            logger.warning(
                f"No email found for user {form_instance.submitted_by.username}"
            )
            return False

        # Prepare email content based on notification type
        subject_map = {
            "status_update": f"Form Status Update: {form_instance.title}",
            "approved": f"Form Approved: {form_instance.title}",
            "rejected": f"Form Rejected: {form_instance.title}",
            "requires_changes": f"Changes Required: {form_instance.title}",
        }

        subject = subject_map.get(
            notification_type, f"Form Update: {form_instance.title}"
        )

        context = {
            "form": form_instance,
            "user": form_instance.submitted_by,
            "notification_type": notification_type,
            "status": form_instance.get_status_display(),
            "admin_notes": form_instance.admin_notes,
        }

        # Render email templates
        html_message = render_to_string("forms/emails/user_notification.html", context)
        plain_message = render_to_string("forms/emails/user_notification.txt", context)

        # Send email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@example.com"),
            recipient_list=[user_email],
            html_message=html_message,
            fail_silently=False,
        )

        logger.info(f"User notification sent for form {form_instance.id}")
        return True

    except Exception as e:
        logger.error(f"Failed to send user notification: {str(e)}")
        return False


# Async task placeholders (for future Celery integration)
def send_admin_notification_async(form_id, form_model):
    """
    Async task to send admin notification.

    This is a placeholder for Celery task implementation.
    """
    # TODO: Implement with Celery
    # @shared_task
    # def send_admin_notification_async(form_id, form_model):
    #     model_class = apps.get_model('forms', form_model)
    #     form_instance = model_class.objects.get(id=form_id)
    #     return send_admin_notification(form_instance)
    pass


def send_user_notification_async(form_id, form_model, notification_type):
    """
    Async task to send user notification.

    This is a placeholder for Celery task implementation.
    """
    # TODO: Implement with Celery
    # @shared_task
    # def send_user_notification_async(form_id, form_model, notification_type):
    #     model_class = apps.get_model('forms', form_model)
    #     form_instance = model_class.objects.get(id=form_id)
    #     return send_user_notification(form_instance, notification_type)
    pass


# Email configuration check
def check_email_configuration():
    """
    Check if email is properly configured.

    Returns:
        bool: True if email is configured, False otherwise
    """
    required_settings = [
        "EMAIL_HOST",
        "EMAIL_PORT",
        "EMAIL_HOST_USER",
        "EMAIL_HOST_PASSWORD",
    ]

    for setting in required_settings:
        if not hasattr(settings, setting) or not getattr(settings, setting):
            logger.warning(f"Email setting {setting} is not configured")
            return False

    return True
