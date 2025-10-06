"""
Django admin configuration for the forms app.

Provides admin interfaces for:
- Form management and review
- Dynamic field configuration
- File upload management
"""

from django.contrib import admin

from .models import (
    CustomForm,
    CustomFormField,
    FileUpload,
    FormField,
    FormSubmissionData,
)
from .specific_models import InvestmentDeclarationForm, KYCForm, LoanApplicationForm


@admin.register(FileUpload)
class FileUploadAdmin(admin.ModelAdmin):
    """Admin interface for file uploads."""

    list_display = [
        "original_filename",
        "content_type",
        "file_size_display",
        "uploaded_at",
    ]
    list_filter = ["content_type", "uploaded_at"]
    search_fields = ["original_filename", "field_name"]
    readonly_fields = ["id", "file_size", "uploaded_at"]

    def file_size_display(self, obj):
        """Display file size in human-readable format."""
        return f"{obj.file_size_mb} MB"

    file_size_display.short_description = "File Size"


@admin.register(FormField)
class FormFieldAdmin(admin.ModelAdmin):
    """Admin interface for dynamic form fields."""

    list_display = ["label", "name", "field_type", "is_required", "order"]
    list_filter = ["field_type", "is_required"]
    search_fields = ["name", "label"]
    ordering = ["order", "name"]

    fieldsets = (
        ("Basic Information", {"fields": ("name", "label", "field_type", "order")}),
        ("Configuration", {"fields": ("is_required", "placeholder", "help_text")}),
        (
            "Choices (for dropdown fields)",
            {"fields": ("choices",), "classes": ("collapse",)},
        ),
        (
            "Validation Rules",
            {
                "fields": ("min_length", "max_length", "min_value", "max_value"),
                "classes": ("collapse",),
            },
        ),
    )


class CustomFormFieldInline(admin.TabularInline):
    """Inline admin for CustomForm fields."""

    model = CustomFormField
    extra = 1
    ordering = ["order"]


@admin.register(CustomForm)
class CustomFormAdmin(admin.ModelAdmin):
    """Admin interface for custom forms."""

    list_display = ["title", "submitted_by", "status", "created_at", "field_count"]
    list_filter = ["status", "allow_multiple_submissions", "created_at"]
    search_fields = ["title", "description", "submitted_by__username"]
    readonly_fields = ["id", "created_at", "updated_at", "submitted_at", "reviewed_at"]

    inlines = [CustomFormFieldInline]

    fieldsets = (
        ("Form Information", {"fields": ("title", "description", "submitted_by")}),
        ("Status & Tracking", {"fields": ("status", "admin_notes")}),
        (
            "Configuration",
            {"fields": ("allow_multiple_submissions", "submission_deadline")},
        ),
        (
            "Timestamps",
            {
                "fields": ("created_at", "updated_at", "submitted_at", "reviewed_at"),
                "classes": ("collapse",),
            },
        ),
        (
            "Notifications",
            {
                "fields": ("admin_notified", "notification_sent_at"),
                "classes": ("collapse",),
            },
        ),
    )

    def field_count(self, obj):
        """Display number of fields in the form."""
        return obj.fields.count()

    field_count.short_description = "Fields"


class BaseFormAdmin(admin.ModelAdmin):
    """Base admin class for all form types."""

    list_display = ["title", "submitted_by", "status", "created_at", "admin_notified"]
    list_filter = ["status", "admin_notified", "created_at"]
    search_fields = ["title", "description", "submitted_by__username"]
    readonly_fields = ["id", "created_at", "updated_at", "submitted_at", "reviewed_at"]

    actions = ["mark_as_approved", "mark_as_rejected", "mark_under_review"]

    def mark_as_approved(self, request, queryset):
        """Mark selected forms as approved."""
        updated = queryset.update(status="approved")
        self.message_user(request, f"{updated} forms marked as approved.")

    mark_as_approved.short_description = "Mark selected forms as approved"

    def mark_as_rejected(self, request, queryset):
        """Mark selected forms as rejected."""
        updated = queryset.update(status="rejected")
        self.message_user(request, f"{updated} forms marked as rejected.")

    mark_as_rejected.short_description = "Mark selected forms as rejected"

    def mark_under_review(self, request, queryset):
        """Mark selected forms as under review."""
        updated = queryset.update(status="under_review")
        self.message_user(request, f"{updated} forms marked as under review.")

    mark_under_review.short_description = "Mark selected forms as under review"

    fieldsets = (
        ("Form Information", {"fields": ("title", "description", "submitted_by")}),
        ("Status & Review", {"fields": ("status", "admin_notes")}),
        (
            "Timestamps",
            {
                "fields": ("created_at", "updated_at", "submitted_at", "reviewed_at"),
                "classes": ("collapse",),
            },
        ),
        (
            "Notifications",
            {
                "fields": ("admin_notified", "notification_sent_at"),
                "classes": ("collapse",),
            },
        ),
    )


@admin.register(KYCForm)
class KYCFormAdmin(BaseFormAdmin):
    """Admin interface for KYC forms."""

    list_display = BaseFormAdmin.list_display + ["first_name", "last_name", "email"]
    search_fields = BaseFormAdmin.search_fields + ["first_name", "last_name", "email"]

    fieldsets = BaseFormAdmin.fieldsets + (
        (
            "Personal Information",
            {
                "fields": (
                    "first_name",
                    "middle_name",
                    "last_name",
                    "date_of_birth",
                    "nationality",
                )
            },
        ),
        (
            "Contact Information",
            {
                "fields": (
                    "email",
                    "phone_number",
                    "address_line_1",
                    "address_line_2",
                    "city",
                    "state_province",
                    "postal_code",
                    "country",
                )
            },
        ),
        (
            "Identity Documents",
            {
                "fields": (
                    "identity_document_type",
                    "identity_document_number",
                    "identity_document_expiry",
                )
            },
        ),
        (
            "File Uploads",
            {
                "fields": (
                    "identity_document_front",
                    "identity_document_back",
                    "proof_of_address",
                ),
                "classes": ("collapse",),
            },
        ),
    )


@admin.register(LoanApplicationForm)
class LoanApplicationFormAdmin(BaseFormAdmin):
    """Admin interface for loan application forms."""

    list_display = BaseFormAdmin.list_display + [
        "loan_amount",
        "loan_purpose",
        "annual_income",
    ]
    list_filter = BaseFormAdmin.list_filter + ["loan_purpose", "employment_status"]

    fieldsets = BaseFormAdmin.fieldsets + (
        (
            "Loan Details",
            {"fields": ("loan_amount", "loan_purpose", "loan_term_months")},
        ),
        (
            "Financial Information",
            {
                "fields": (
                    "annual_income",
                    "employment_status",
                    "employer_name",
                    "employment_duration_months",
                )
            },
        ),
        (
            "Additional Information",
            {"fields": ("existing_loans", "existing_loan_amount")},
        ),
        (
            "File Uploads",
            {"fields": ("income_proof", "employment_letter"), "classes": ("collapse",)},
        ),
    )


@admin.register(InvestmentDeclarationForm)
class InvestmentDeclarationFormAdmin(BaseFormAdmin):
    """Admin interface for investment declaration forms."""

    list_display = BaseFormAdmin.list_display + [
        "investment_type",
        "investment_amount",
        "risk_tolerance",
    ]
    list_filter = BaseFormAdmin.list_filter + [
        "investment_type",
        "risk_tolerance",
        "investment_experience",
    ]

    fieldsets = BaseFormAdmin.fieldsets + (
        (
            "Investment Details",
            {
                "fields": (
                    "investment_type",
                    "investment_amount",
                    "investment_duration_months",
                )
            },
        ),
        ("Risk Assessment", {"fields": ("risk_tolerance",)}),
        (
            "Financial Background",
            {"fields": ("net_worth", "liquid_assets", "investment_experience")},
        ),
        (
            "File Uploads",
            {"fields": ("financial_statements",), "classes": ("collapse",)},
        ),
    )


@admin.register(FormSubmissionData)
class FormSubmissionDataAdmin(admin.ModelAdmin):
    """Admin interface for custom form submission data."""

    list_display = ["custom_form", "created_at", "field_count"]
    list_filter = ["created_at"]
    search_fields = ["custom_form__title"]
    readonly_fields = ["id", "created_at", "updated_at"]

    def field_count(self, obj):
        """Display number of fields with data."""
        return len(obj.field_data)

    field_count.short_description = "Fields with Data"

    fieldsets = (
        ("Submission Information", {"fields": ("custom_form",)}),
        ("Form Data", {"fields": ("field_data",)}),
        ("File Uploads", {"fields": ("file_uploads",)}),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )
