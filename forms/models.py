"""
Models for the dynamic onboarding form system.

This module implements a hybrid approach with:
- BaseForm: Abstract model with common functionality
- Specific form models: KYC, Loan, Investment, etc.
- Dynamic field configuration system
"""

import uuid

from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils import timezone

from .dynamic_models import (
    BaseForm,
    CustomForm,
    CustomFormField,
    FormField,
    FormStatus,
    FormSubmissionData,
)

# Note: Specific models are imported separately to avoid circular imports
# Import all models to make them available
from .file_models import FileUpload
from .specific_models import InvestmentDeclarationForm, KYCForm, LoanApplicationForm

__all__ = [
    "FormStatus",
    "BaseForm",
    "FileUpload",
    "KYCForm",
    "LoanApplicationForm",
    "InvestmentDeclarationForm",
    "FormField",
    "CustomForm",
    "CustomFormField",
    "FormSubmissionData",
]
