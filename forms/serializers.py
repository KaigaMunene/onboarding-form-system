"""
Django REST Framework serializers for the forms app.

Provides serialization for:
- All form types (KYC, Loan, Investment, Custom)
- File uploads
- Dynamic form fields
"""

from rest_framework import serializers

from .models import CustomForm, FileUpload, FormField, FormSubmissionData
from .specific_models import InvestmentDeclarationForm, KYCForm, LoanApplicationForm


class FileUploadSerializer(serializers.ModelSerializer):
    """Serializer for file uploads."""

    file_size_mb = serializers.ReadOnlyField()

    class Meta:
        model = FileUpload
        fields = [
            "id",
            "file",
            "original_filename",
            "file_size",
            "file_size_mb",
            "content_type",
            "field_name",
            "uploaded_at",
        ]
        read_only_fields = ["id", "file_size", "content_type", "uploaded_at"]

    def create(self, validated_data):
        """Create file upload with metadata."""
        file_obj = validated_data["file"]
        validated_data["original_filename"] = file_obj.name
        validated_data["file_size"] = file_obj.size
        validated_data["content_type"] = file_obj.content_type
        return super().create(validated_data)


class FormFieldSerializer(serializers.ModelSerializer):
    """Serializer for dynamic form fields."""

    class Meta:
        model = FormField
        fields = [
            "id",
            "name",
            "label",
            "field_type",
            "is_required",
            "placeholder",
            "help_text",
            "choices",
            "min_length",
            "max_length",
            "min_value",
            "max_value",
            "order",
        ]


class BaseFormSerializer(serializers.ModelSerializer):
    """Base serializer for all form types."""

    submitted_by = serializers.StringRelatedField(read_only=True)
    form_type = serializers.CharField(source="get_form_type", read_only=True)
    is_editable = serializers.ReadOnlyField()

    class Meta:
        fields = [
            "id",
            "title",
            "description",
            "submitted_by",
            "status",
            "created_at",
            "updated_at",
            "submitted_at",
            "reviewed_at",
            "admin_notes",
            "form_type",
            "is_editable",
        ]
        read_only_fields = [
            "id",
            "submitted_by",
            "created_at",
            "updated_at",
            "submitted_at",
            "reviewed_at",
            "form_type",
            "is_editable",
        ]

    def create(self, validated_data):
        """Create form with current user as submitter."""
        # Don't override submitted_by if it's already set by the view
        if "submitted_by" not in validated_data:
            validated_data["submitted_by"] = self.context["request"].user
        return super().create(validated_data)


class KYCFormSerializer(BaseFormSerializer):
    """Serializer for KYC forms."""

    identity_document_front = FileUploadSerializer(read_only=True)
    identity_document_back = FileUploadSerializer(read_only=True)
    proof_of_address = FileUploadSerializer(read_only=True)

    # Write-only fields for file upload IDs
    identity_document_front_id = serializers.UUIDField(write_only=True, required=False)
    identity_document_back_id = serializers.UUIDField(write_only=True, required=False)
    proof_of_address_id = serializers.UUIDField(write_only=True, required=False)

    class Meta(BaseFormSerializer.Meta):
        model = KYCForm
        fields = BaseFormSerializer.Meta.fields + [
            "first_name",
            "last_name",
            "middle_name",
            "date_of_birth",
            "nationality",
            "email",
            "phone_number",
            "address_line_1",
            "address_line_2",
            "city",
            "state_province",
            "postal_code",
            "country",
            "identity_document_type",
            "identity_document_number",
            "identity_document_expiry",
            "identity_document_front",
            "identity_document_back",
            "proof_of_address",
            "identity_document_front_id",
            "identity_document_back_id",
            "proof_of_address_id",
        ]

    def create(self, validated_data):
        """Create KYC form with file associations."""
        # Extract file IDs
        front_id = validated_data.pop("identity_document_front_id", None)
        back_id = validated_data.pop("identity_document_back_id", None)
        address_id = validated_data.pop("proof_of_address_id", None)

        # Create the form
        kyc_form = super().create(validated_data)

        # Associate files
        if front_id:
            kyc_form.identity_document_front_id = front_id
        if back_id:
            kyc_form.identity_document_back_id = back_id
        if address_id:
            kyc_form.proof_of_address_id = address_id

        kyc_form.save()
        return kyc_form


class LoanApplicationFormSerializer(BaseFormSerializer):
    """Serializer for loan application forms."""

    income_proof = FileUploadSerializer(read_only=True)
    employment_letter = FileUploadSerializer(read_only=True)

    # Write-only fields for file upload IDs
    income_proof_id = serializers.UUIDField(write_only=True, required=False)
    employment_letter_id = serializers.UUIDField(write_only=True, required=False)

    class Meta(BaseFormSerializer.Meta):
        model = LoanApplicationForm
        fields = BaseFormSerializer.Meta.fields + [
            "loan_amount",
            "loan_purpose",
            "loan_term_months",
            "annual_income",
            "employment_status",
            "employer_name",
            "employment_duration_months",
            "existing_loans",
            "existing_loan_amount",
            "income_proof",
            "employment_letter",
            "income_proof_id",
            "employment_letter_id",
        ]

    def create(self, validated_data):
        """Create loan application with file associations."""
        # Extract file IDs
        income_id = validated_data.pop("income_proof_id", None)
        employment_id = validated_data.pop("employment_letter_id", None)

        # Create the form
        loan_form = super().create(validated_data)

        # Associate files
        if income_id:
            loan_form.income_proof_id = income_id
        if employment_id:
            loan_form.employment_letter_id = employment_id

        loan_form.save()
        return loan_form


class InvestmentDeclarationFormSerializer(BaseFormSerializer):
    """Serializer for investment declaration forms."""

    financial_statements = FileUploadSerializer(read_only=True)

    # Write-only field for file upload ID
    financial_statements_id = serializers.UUIDField(write_only=True, required=False)

    class Meta(BaseFormSerializer.Meta):
        model = InvestmentDeclarationForm
        fields = BaseFormSerializer.Meta.fields + [
            "investment_type",
            "investment_amount",
            "investment_duration_months",
            "risk_tolerance",
            "net_worth",
            "liquid_assets",
            "investment_experience",
            "financial_statements",
            "financial_statements_id",
        ]

    def create(self, validated_data):
        """Create investment declaration with file associations."""
        # Extract file ID
        statements_id = validated_data.pop("financial_statements_id", None)

        # Create the form
        investment_form = super().create(validated_data)

        # Associate file
        if statements_id:
            investment_form.financial_statements_id = statements_id

        investment_form.save()
        return investment_form


class CustomFormSerializer(BaseFormSerializer):
    """Serializer for custom forms."""

    fields = FormFieldSerializer(many=True, read_only=True)
    field_count = serializers.SerializerMethodField()

    class Meta(BaseFormSerializer.Meta):
        model = CustomForm
        fields = BaseFormSerializer.Meta.fields + [
            "fields",
            "field_count",
            "allow_multiple_submissions",
            "submission_deadline",
        ]

    def get_field_count(self, obj):
        """Get the number of fields in the form."""
        return obj.fields.count()


class FormSubmissionDataSerializer(serializers.ModelSerializer):
    """Serializer for custom form submission data."""

    custom_form = CustomFormSerializer(read_only=True)
    custom_form_id = serializers.UUIDField(write_only=True)
    file_uploads = FileUploadSerializer(many=True, read_only=True)
    file_upload_ids = serializers.ListField(
        child=serializers.UUIDField(), write_only=True, required=False
    )

    class Meta:
        model = FormSubmissionData
        fields = [
            "id",
            "custom_form",
            "custom_form_id",
            "field_data",
            "file_uploads",
            "file_upload_ids",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def create(self, validated_data):
        """Create form submission with file associations."""
        file_ids = validated_data.pop("file_upload_ids", [])

        # Create the submission
        submission = super().create(validated_data)

        # Associate files
        if file_ids:
            submission.file_uploads.set(file_ids)

        return submission


# Summary serializers for list views
class FormSummarySerializer(serializers.Serializer):
    """Summary serializer for form listings."""

    id = serializers.UUIDField()
    title = serializers.CharField()
    form_type = serializers.CharField()
    status = serializers.CharField()
    submitted_by = serializers.StringRelatedField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
