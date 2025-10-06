"""
Specific form models that inherit from BaseForm.

This module contains:
- KYCForm: Know Your Customer verification
- LoanApplicationForm: Loan applications with financial data
- InvestmentDeclarationForm: Investment planning forms
- CustomForm: Dynamic forms with configurable fields
"""

from django.core.exceptions import ValidationError
from django.db import models

from .dynamic_models import BaseForm
from .file_models import FileUpload
from .validators import (
    validate_annual_income,
    validate_employment_duration,
    validate_identity_document_number,
    validate_investment_amount,
    validate_investment_duration,
    validate_loan_amount,
    validate_loan_term,
    validate_net_worth,
    validate_phone_number,
    validate_postal_code,
)


class KYCForm(BaseForm):
    """Know Your Customer form for identity verification."""

    # Personal Information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    date_of_birth = models.DateField()
    nationality = models.CharField(max_length=100)

    # Contact Information
    email = models.EmailField()
    phone_number = models.CharField(max_length=20, validators=[validate_phone_number])
    address_line_1 = models.CharField(max_length=200)
    address_line_2 = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=100)
    state_province = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20, validators=[validate_postal_code])
    country = models.CharField(max_length=100)

    # Identity Documents
    identity_document_type = models.CharField(
        max_length=50,
        choices=[
            ("passport", "Passport"),
            ("national_id", "National ID"),
            ("drivers_license", "Driver's License"),
        ],
    )
    identity_document_number = models.CharField(
        max_length=100, validators=[validate_identity_document_number]
    )
    identity_document_expiry = models.DateField()

    # File uploads
    identity_document_front = models.ForeignKey(
        FileUpload,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="kyc_id_front",
    )
    identity_document_back = models.ForeignKey(
        FileUpload,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="kyc_id_back",
    )
    proof_of_address = models.ForeignKey(
        FileUpload,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="kyc_address_proof",
    )

    class Meta:
        verbose_name = "KYC Form"
        verbose_name_plural = "KYC Forms"
        # Prevent duplicate KYC forms for same person
        unique_together = [
            ["first_name", "last_name", "email", "identity_document_number"]
        ]


class LoanApplicationForm(BaseForm):
    """Loan application form with financial information."""

    # Loan Details
    loan_amount = models.DecimalField(
        max_digits=12, decimal_places=2, validators=[validate_loan_amount]
    )
    loan_purpose = models.CharField(
        max_length=100,
        choices=[
            ("personal", "Personal"),
            ("business", "Business"),
            ("education", "Education"),
            ("home", "Home Purchase"),
            ("vehicle", "Vehicle"),
            ("other", "Other"),
        ],
    )
    loan_term_months = models.PositiveIntegerField(validators=[validate_loan_term])

    # Financial Information
    annual_income = models.DecimalField(
        max_digits=12, decimal_places=2, validators=[validate_annual_income]
    )
    employment_status = models.CharField(
        max_length=50,
        choices=[
            ("employed", "Employed"),
            ("self_employed", "Self Employed"),
            ("unemployed", "Unemployed"),
            ("retired", "Retired"),
            ("student", "Student"),
        ],
    )
    employer_name = models.CharField(max_length=200, blank=True)
    employment_duration_months = models.PositiveIntegerField(
        null=True, blank=True, validators=[validate_employment_duration]
    )

    # Additional Information
    existing_loans = models.BooleanField(default=False)
    existing_loan_amount = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )

    # File uploads
    income_proof = models.ForeignKey(
        FileUpload,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="loan_income_proof",
    )
    employment_letter = models.ForeignKey(
        FileUpload,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="loan_employment_letter",
    )

    class Meta:
        verbose_name = "Loan Application"
        verbose_name_plural = "Loan Applications"

    def clean(self):
        """Custom validation for loan applications."""
        super().clean()

        # Validate loan amount based on income
        if self.loan_amount and self.annual_income:
            if self.loan_amount > self.annual_income * 5:
                raise ValidationError("Loan amount cannot exceed 5 times annual income")

        # Validate employment details for employed applicants
        if self.employment_status == "employed" and not self.employer_name:
            raise ValidationError("Employer name is required for employed applicants")


class InvestmentDeclarationForm(BaseForm):
    """Investment declaration form for financial planning."""

    # Investment Details
    investment_type = models.CharField(
        max_length=100,
        choices=[
            ("stocks", "Stocks"),
            ("bonds", "Bonds"),
            ("mutual_funds", "Mutual Funds"),
            ("real_estate", "Real Estate"),
            ("cryptocurrency", "Cryptocurrency"),
            ("other", "Other"),
        ],
    )
    investment_amount = models.DecimalField(
        max_digits=12, decimal_places=2, validators=[validate_investment_amount]
    )
    investment_duration_months = models.PositiveIntegerField(
        validators=[validate_investment_duration]
    )

    # Risk Assessment
    risk_tolerance = models.CharField(
        max_length=20,
        choices=[
            ("low", "Low Risk"),
            ("medium", "Medium Risk"),
            ("high", "High Risk"),
        ],
    )

    # Financial Background
    net_worth = models.DecimalField(
        max_digits=12, decimal_places=2, validators=[validate_net_worth]
    )
    liquid_assets = models.DecimalField(
        max_digits=12, decimal_places=2, validators=[validate_investment_amount]
    )
    investment_experience = models.CharField(
        max_length=20,
        choices=[
            ("beginner", "Beginner"),
            ("intermediate", "Intermediate"),
            ("advanced", "Advanced"),
        ],
    )

    # File uploads
    financial_statements = models.ForeignKey(
        FileUpload,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="investment_financial_statements",
    )

    class Meta:
        verbose_name = "Investment Declaration"
        verbose_name_plural = "Investment Declarations"
