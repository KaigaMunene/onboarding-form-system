"""
Tests for the forms app.

This module contains basic tests to verify the hybrid model architecture works correctly.
"""

from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase

from .models import CustomForm, FileUpload, FormField, FormSubmissionData
from .specific_models import InvestmentDeclarationForm, KYCForm, LoanApplicationForm


class BaseFormTestCase(TestCase):
    """Test case for BaseForm functionality."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

    def test_form_creation_and_status(self):
        """Test basic form creation and status management."""
        kyc_form = KYCForm.objects.create(
            title="Test KYC Form",
            description="Test description",
            submitted_by=self.user,
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            phone_number="+1-555-123-4567",
            date_of_birth=date(1990, 1, 15),
            nationality="US",
            address_line_1="123 Main St",
            city="New York",
            state_province="NY",
            postal_code="10001",
            country="United States",
            identity_document_type="passport",
            identity_document_number="AB1234567",
            identity_document_expiry=date(2030, 12, 31),
        )

        # Test initial status
        self.assertEqual(kyc_form.status, "draft")
        self.assertTrue(kyc_form.is_editable)

        # Test form submission
        kyc_form.submit()
        self.assertEqual(kyc_form.status, "submitted")
        self.assertIsNotNone(kyc_form.submitted_at)
        self.assertFalse(kyc_form.is_editable)

        # Test form type
        self.assertEqual(kyc_form.get_form_type(), "KYCForm")


class KYCFormTestCase(TestCase):
    """Test case for KYC forms."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

    def test_kyc_form_validation(self):
        """Test KYC form field validation."""
        # Test valid KYC form
        kyc_form = KYCForm(
            title="Valid KYC Form",
            submitted_by=self.user,
            first_name="Jane",
            last_name="Smith",
            email="jane@example.com",
            phone_number="+1-555-987-6543",
            date_of_birth=date(1985, 5, 20),
            nationality="US",
            address_line_1="456 Oak Ave",
            city="Los Angeles",
            state_province="CA",
            postal_code="90210",
            country="United States",
            identity_document_type="drivers_license",
            identity_document_number="DL123456789",
            identity_document_expiry=date(2028, 8, 15),
        )

        # Should not raise validation error
        kyc_form.full_clean()
        kyc_form.save()

        self.assertEqual(kyc_form.first_name, "Jane")
        self.assertEqual(kyc_form.identity_document_type, "drivers_license")

    def test_invalid_phone_number(self):
        """Test phone number validation."""
        kyc_form = KYCForm(
            title="Invalid Phone KYC",
            submitted_by=self.user,
            first_name="Test",
            last_name="User",
            email="test@example.com",
            phone_number="invalid-phone",  # Invalid phone number
            date_of_birth=date(1990, 1, 1),
            nationality="US",
            address_line_1="123 Test St",
            city="Test City",
            state_province="TS",
            postal_code="12345",
            country="Test Country",
            identity_document_type="passport",
            identity_document_number="TEST123",
            identity_document_expiry=date(2030, 1, 1),
        )

        with self.assertRaises(ValidationError):
            kyc_form.full_clean()


class LoanApplicationFormTestCase(TestCase):
    """Test case for loan application forms."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="loanuser", email="loan@example.com", password="testpass123"
        )

    def test_loan_application_creation(self):
        """Test loan application form creation."""
        loan_form = LoanApplicationForm.objects.create(
            title="Personal Loan Application",
            submitted_by=self.user,
            loan_amount=Decimal("25000.00"),
            loan_purpose="personal",
            loan_term_months=36,
            annual_income=Decimal("75000.00"),
            employment_status="employed",
            employer_name="Test Company Inc.",
            employment_duration_months=24,
            existing_loans=False,
        )

        self.assertEqual(loan_form.loan_amount, Decimal("25000.00"))
        self.assertEqual(loan_form.loan_purpose, "personal")
        self.assertEqual(loan_form.employment_status, "employed")

    def test_loan_amount_validation(self):
        """Test loan amount validation."""
        # Test loan amount too high relative to income
        loan_form = LoanApplicationForm(
            title="High Loan Application",
            submitted_by=self.user,
            loan_amount=Decimal("500000.00"),  # 5x income limit
            loan_purpose="personal",
            loan_term_months=36,
            annual_income=Decimal("75000.00"),  # Would exceed 5x income
            employment_status="employed",
            employer_name="Test Company",
            employment_duration_months=24,
        )

        with self.assertRaises(ValidationError):
            loan_form.clean()

    def test_employment_validation(self):
        """Test employment status validation."""
        # Test employed status without employer name
        loan_form = LoanApplicationForm(
            title="Employment Test",
            submitted_by=self.user,
            loan_amount=Decimal("25000.00"),
            loan_purpose="personal",
            loan_term_months=36,
            annual_income=Decimal("75000.00"),
            employment_status="employed",
            employer_name="",  # Missing employer name for employed status
            employment_duration_months=24,
        )

        with self.assertRaises(ValidationError):
            loan_form.clean()


class InvestmentDeclarationFormTestCase(TestCase):
    """Test case for investment declaration forms."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="investor", email="investor@example.com", password="testpass123"
        )

    def test_investment_form_creation(self):
        """Test investment declaration form creation."""
        investment_form = InvestmentDeclarationForm.objects.create(
            title="Stock Investment Declaration",
            submitted_by=self.user,
            investment_type="stocks",
            investment_amount=Decimal("50000.00"),
            investment_duration_months=60,
            risk_tolerance="medium",
            net_worth=Decimal("250000.00"),
            liquid_assets=Decimal("100000.00"),
            investment_experience="intermediate",
        )

        self.assertEqual(investment_form.investment_type, "stocks")
        self.assertEqual(investment_form.risk_tolerance, "medium")
        self.assertEqual(investment_form.investment_experience, "intermediate")


class DynamicFormTestCase(TestCase):
    """Test case for dynamic forms."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="dynamicuser", email="dynamic@example.com", password="testpass123"
        )

        # Create form fields
        self.text_field = FormField.objects.create(
            name="full_name",
            label="Full Name",
            field_type="text",
            is_required=True,
            min_length=2,
            max_length=100,
            order=1,
        )

        self.email_field = FormField.objects.create(
            name="email_address",
            label="Email Address",
            field_type="email",
            is_required=True,
            order=2,
        )

        self.number_field = FormField.objects.create(
            name="age",
            label="Age",
            field_type="number",
            is_required=True,
            min_value=Decimal("18"),
            max_value=Decimal("120"),
            order=3,
        )

    def test_form_field_creation(self):
        """Test form field creation and configuration."""
        self.assertEqual(self.text_field.name, "full_name")
        self.assertEqual(self.text_field.field_type, "text")
        self.assertTrue(self.text_field.is_required)
        self.assertEqual(self.text_field.min_length, 2)

    def test_custom_form_creation(self):
        """Test custom form creation with dynamic fields."""
        custom_form = CustomForm.objects.create(
            title="Dynamic Registration Form",
            description="A form with configurable fields",
            submitted_by=self.user,
            allow_multiple_submissions=False,
        )

        # Add fields to the custom form
        custom_form.fields.add(self.text_field, through_defaults={"order": 1})
        custom_form.fields.add(self.email_field, through_defaults={"order": 2})
        custom_form.fields.add(self.number_field, through_defaults={"order": 3})

        self.assertEqual(custom_form.fields.count(), 3)
        self.assertFalse(custom_form.allow_multiple_submissions)

    def test_form_submission_data(self):
        """Test form submission data storage."""
        custom_form = CustomForm.objects.create(
            title="Test Submission Form", submitted_by=self.user
        )

        # Create submission data
        submission_data = FormSubmissionData.objects.create(
            custom_form=custom_form,
            field_data={
                "full_name": "John Doe",
                "email_address": "john@example.com",
                "age": 30,
            },
        )

        self.assertEqual(submission_data.field_data["full_name"], "John Doe")
        self.assertEqual(submission_data.field_data["age"], 30)
        self.assertEqual(submission_data.custom_form, custom_form)


class FileUploadTestCase(TestCase):
    """Test case for file uploads."""

    def test_file_upload_model(self):
        """Test file upload model creation."""
        # Note: This is a basic model test without actual file upload
        file_upload = FileUpload(
            original_filename="test_document.pdf",
            file_size=1024000,  # 1MB
            content_type="application/pdf",
            field_name="identity_document",
        )

        self.assertEqual(file_upload.original_filename, "test_document.pdf")
        self.assertEqual(file_upload.content_type, "application/pdf")
        self.assertAlmostEqual(file_upload.file_size_mb, 1.0, places=1)


class ValidationTestCase(TestCase):
    """Test case for custom validators."""

    def test_phone_number_validation(self):
        """Test phone number validator."""
        from .validators import validate_phone_number

        # Valid phone numbers
        valid_phones = [
            "+1-555-123-4567",
            "555-123-4567",
            "(555) 123-4567",
            "+44 20 7946 0958",
        ]

        for phone in valid_phones:
            try:
                validate_phone_number(phone)
            except ValidationError:
                self.fail(f"Valid phone number {phone} failed validation")

        # Invalid phone numbers
        invalid_phones = ["invalid", "123", "abc-def-ghij"]

        for phone in invalid_phones:
            with self.assertRaises(ValidationError):
                validate_phone_number(phone)

    def test_loan_amount_validation(self):
        """Test loan amount validator."""
        from .validators import validate_loan_amount

        # Valid loan amounts
        valid_amounts = [Decimal("1000"), Decimal("50000"), Decimal("500000")]

        for amount in valid_amounts:
            try:
                validate_loan_amount(amount)
            except ValidationError:
                self.fail(f"Valid loan amount {amount} failed validation")

        # Invalid loan amounts
        invalid_amounts = [
            Decimal("0"),
            Decimal("-1000"),
            Decimal("50000000"),  # Too high
        ]

        for amount in invalid_amounts:
            with self.assertRaises(ValidationError):
                validate_loan_amount(amount)
