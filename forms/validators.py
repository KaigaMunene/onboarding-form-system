"""
Custom validators for the forms app.

This module provides:
- File validation (size, type, content)
- Form field validation
- Business logic validation
"""

import os
import re
from decimal import Decimal

import magic
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.utils.deconstruct import deconstructible


@deconstructible
class FileSizeValidator:
    """Validator for file size limits."""

    def __init__(self, max_size_mb=10):
        self.max_size_mb = max_size_mb
        self.max_size_bytes = max_size_mb * 1024 * 1024

    def __call__(self, file):
        if file.size > self.max_size_bytes:
            raise ValidationError(
                f"File size cannot exceed {self.max_size_mb}MB. "
                f"Current file size: {file.size / (1024 * 1024):.2f}MB"
            )

    def __eq__(self, other):
        return (
            isinstance(other, FileSizeValidator)
            and self.max_size_mb == other.max_size_mb
        )


@deconstructible
class FileTypeValidator:
    """Validator for file MIME types."""

    def __init__(self, allowed_types=None):
        self.allowed_types = allowed_types or [
            "application/pdf",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "image/jpeg",
            "image/png",
            "text/plain",
        ]

    def __call__(self, file):
        try:
            # Reset file pointer
            file.seek(0)

            # Read file content to detect MIME type
            file_content = file.read(1024)  # Read first 1KB
            file.seek(0)  # Reset pointer

            # Detect MIME type
            mime_type = magic.from_buffer(file_content, mime=True)

            if mime_type not in self.allowed_types:
                raise ValidationError(
                    f'File type "{mime_type}" is not allowed. '
                    f'Allowed types: {", ".join(self.allowed_types)}'
                )
        except Exception as e:
            raise ValidationError(f"Could not validate file type: {str(e)}")

    def __eq__(self, other):
        return (
            isinstance(other, FileTypeValidator)
            and self.allowed_types == other.allowed_types
        )


def validate_phone_number(value):
    """Validate phone number format."""
    # Simple phone number validation (can be enhanced)
    phone_pattern = re.compile(r"^\+?[\d\s\-\(\)]{10,15}$")
    if not phone_pattern.match(value):
        raise ValidationError(
            "Enter a valid phone number (10-15 digits, may include +, spaces, hyphens, parentheses)"
        )


def validate_postal_code(value):
    """Validate postal code format."""
    # Basic postal code validation (can be enhanced for specific countries)
    postal_pattern = re.compile(r"^[\w\s\-]{3,10}$")
    if not postal_pattern.match(value):
        raise ValidationError(
            "Enter a valid postal code (3-10 characters, letters, numbers, spaces, hyphens allowed)"
        )


def validate_identity_document_number(value):
    """Validate identity document number."""
    # Remove spaces and hyphens for validation
    clean_value = re.sub(r"[\s\-]", "", value)

    if len(clean_value) < 5:
        raise ValidationError(
            "Identity document number must be at least 5 characters long"
        )

    if len(clean_value) > 20:
        raise ValidationError("Identity document number cannot exceed 20 characters")

    # Check for valid characters (alphanumeric)
    if not re.match(r"^[A-Za-z0-9]+$", clean_value):
        raise ValidationError(
            "Identity document number can only contain letters and numbers"
        )


def validate_loan_amount(value):
    """Validate loan amount."""
    if value <= 0:
        raise ValidationError("Loan amount must be greater than zero")

    if value > Decimal("10000000"):  # 10 million limit
        raise ValidationError("Loan amount cannot exceed $10,000,000")

    # Check for reasonable minimum
    if value < Decimal("1000"):
        raise ValidationError("Loan amount must be at least $1,000")


def validate_investment_amount(value):
    """Validate investment amount."""
    if value <= 0:
        raise ValidationError("Investment amount must be greater than zero")

    if value > Decimal("100000000"):  # 100 million limit
        raise ValidationError("Investment amount cannot exceed $100,000,000")

    # Check for reasonable minimum
    if value < Decimal("100"):
        raise ValidationError("Investment amount must be at least $100")


def validate_annual_income(value):
    """Validate annual income."""
    if value < 0:
        raise ValidationError("Annual income cannot be negative")

    if value > Decimal("50000000"):  # 50 million limit
        raise ValidationError("Annual income seems unreasonably high")


def validate_net_worth(value):
    """Validate net worth."""
    # Net worth can be negative (debts exceed assets)
    if value < Decimal("-10000000"):  # -10 million limit
        raise ValidationError("Net worth seems unreasonably low")

    if value > Decimal("1000000000"):  # 1 billion limit
        raise ValidationError("Net worth seems unreasonably high")


def validate_employment_duration(value):
    """Validate employment duration in months."""
    if value < 0:
        raise ValidationError("Employment duration cannot be negative")

    if value > 600:  # 50 years
        raise ValidationError("Employment duration seems unreasonably long")


def validate_loan_term(value):
    """Validate loan term in months."""
    if value < 1:
        raise ValidationError("Loan term must be at least 1 month")

    if value > 360:  # 30 years
        raise ValidationError("Loan term cannot exceed 30 years (360 months)")


def validate_investment_duration(value):
    """Validate investment duration in months."""
    if value < 1:
        raise ValidationError("Investment duration must be at least 1 month")

    if value > 1200:  # 100 years
        raise ValidationError("Investment duration cannot exceed 100 years")


class FormFieldValidator:
    """Validator for dynamic form fields."""

    @staticmethod
    def validate_field_data(field, value):
        """
        Validate field data based on field configuration.

        Args:
            field: FormField instance
            value: The value to validate

        Raises:
            ValidationError: If validation fails
        """
        if field.is_required and (value is None or value == ""):
            raise ValidationError(f"{field.label} is required")

        if value is None or value == "":
            return  # Skip validation for empty optional fields

        # String length validation
        if field.field_type in ["text", "textarea", "email"]:
            if field.min_length and len(str(value)) < field.min_length:
                raise ValidationError(
                    f"{field.label} must be at least {field.min_length} characters long"
                )

            if field.max_length and len(str(value)) > field.max_length:
                raise ValidationError(
                    f"{field.label} cannot exceed {field.max_length} characters"
                )

        # Numeric validation
        if field.field_type == "number":
            try:
                numeric_value = Decimal(str(value))

                if field.min_value and numeric_value < field.min_value:
                    raise ValidationError(
                        f"{field.label} must be at least {field.min_value}"
                    )

                if field.max_value and numeric_value > field.max_value:
                    raise ValidationError(
                        f"{field.label} cannot exceed {field.max_value}"
                    )
            except (ValueError, TypeError):
                raise ValidationError(f"{field.label} must be a valid number")

        # Email validation
        if field.field_type == "email":
            from django.core.validators import validate_email

            try:
                validate_email(value)
            except ValidationError:
                raise ValidationError(f"{field.label} must be a valid email address")

        # Dropdown validation
        if field.field_type == "dropdown":
            if field.choices and value not in [
                choice["value"] for choice in field.choices
            ]:
                raise ValidationError(f"{field.label} contains an invalid choice")

        # Date validation
        if field.field_type == "date":
            from datetime import datetime

            try:
                if isinstance(value, str):
                    datetime.strptime(value, "%Y-%m-%d")
            except ValueError:
                raise ValidationError(
                    f"{field.label} must be a valid date (YYYY-MM-DD)"
                )


def validate_form_submission_data(custom_form, field_data):
    """
    Validate complete form submission data.

    Args:
        custom_form: CustomForm instance
        field_data: Dictionary of field data

    Raises:
        ValidationError: If validation fails
    """
    errors = {}

    # Get all form fields
    form_fields = custom_form.fields.all()

    for field in form_fields:
        field_value = field_data.get(field.name)

        try:
            FormFieldValidator.validate_field_data(field, field_value)
        except ValidationError as e:
            errors[field.name] = e.messages

    if errors:
        raise ValidationError(errors)
