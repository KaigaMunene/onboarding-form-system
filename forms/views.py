"""
API views for the forms app.

Provides REST API endpoints for:
- Form CRUD operations
- File upload handling
- Form submission and status management
"""

from django.db import models
from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response

from .models import CustomForm, FileUpload, FormField, FormSubmissionData
from .serializers import (
    CustomFormSerializer,
    FileUploadSerializer,
    FormFieldSerializer,
    FormSubmissionDataSerializer,
    FormSummarySerializer,
    InvestmentDeclarationFormSerializer,
    KYCFormSerializer,
    LoanApplicationFormSerializer,
)
from .specific_models import InvestmentDeclarationForm, KYCForm, LoanApplicationForm


class FileUploadViewSet(viewsets.ModelViewSet):
    """ViewSet for file uploads."""

    queryset = FileUpload.objects.all()
    serializer_class = FileUploadSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        """Filter files by current user if not admin."""
        if self.request.user.is_staff:
            return self.queryset
        # For regular users, they can only see files they uploaded
        # This would need to be refined based on form associations
        return self.queryset.filter(
            # Add logic to filter by user's forms
        )


class FormFieldViewSet(viewsets.ModelViewSet):
    """ViewSet for dynamic form fields (admin only)."""

    queryset = FormField.objects.all()
    serializer_class = FormFieldSerializer
    permission_classes = [permissions.IsAdminUser]


class BaseFormViewSet(viewsets.ModelViewSet):
    """Base ViewSet for all form types."""

    permission_classes = [permissions.AllowAny]  # Allow anonymous submissions

    def get_queryset(self):
        """Filter forms by current user if not admin."""
        if self.request.user.is_staff:
            return self.queryset
        elif self.request.user.is_authenticated:
            return self.queryset.filter(submitted_by=self.request.user)
        else:
            # For anonymous users, return empty queryset for security
            return self.queryset.none()

    def perform_create(self, serializer):
        """Set the submitted_by field to current user or create anonymous user."""
        if self.request.user.is_authenticated and not self.request.user.is_anonymous:
            serializer.save(submitted_by=self.request.user)
        else:
            # Create or get anonymous user for submissions
            from django.contrib.auth.models import User

            anonymous_user, created = User.objects.get_or_create(
                username="anonymous",
                defaults={"email": "anonymous@example.com", "is_active": False},
            )
            serializer.save(submitted_by=anonymous_user)

    @action(detail=True, methods=["post"])
    def submit(self, request, pk=None):
        """Submit a form for review."""
        form = self.get_object()

        if not form.is_editable:
            return Response(
                {"error": "Form cannot be edited in current status"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        form.submit()
        serializer = self.get_serializer(form)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAdminUser])
    def approve(self, request, pk=None):
        """Approve a form (admin only)."""
        form = self.get_object()
        form.status = "approved"
        form.reviewed_at = timezone.now()
        form.save()

        serializer = self.get_serializer(form)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAdminUser])
    def reject(self, request, pk=None):
        """Reject a form (admin only)."""
        form = self.get_object()
        form.status = "rejected"
        form.reviewed_at = timezone.now()
        form.admin_notes = request.data.get("admin_notes", form.admin_notes)
        form.save()

        serializer = self.get_serializer(form)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAdminUser])
    def request_changes(self, request, pk=None):
        """Request changes to a form (admin only)."""
        form = self.get_object()
        form.status = "requires_changes"
        form.reviewed_at = timezone.now()
        form.admin_notes = request.data.get("admin_notes", form.admin_notes)
        form.save()

        serializer = self.get_serializer(form)
        return Response(serializer.data)


class KYCFormViewSet(BaseFormViewSet):
    """ViewSet for KYC forms."""

    queryset = KYCForm.objects.all()
    serializer_class = KYCFormSerializer

    @action(detail=False, methods=["get"])
    def my_forms(self, request):
        """Get current user's KYC forms."""
        forms = self.get_queryset().filter(submitted_by=request.user)
        serializer = self.get_serializer(forms, many=True)
        return Response(serializer.data)


class LoanApplicationFormViewSet(BaseFormViewSet):
    """ViewSet for loan application forms."""

    queryset = LoanApplicationForm.objects.all()
    serializer_class = LoanApplicationFormSerializer

    @action(detail=False, methods=["get"])
    def by_status(self, request):
        """Filter loan applications by status."""
        status_param = request.query_params.get("status")
        if status_param:
            forms = self.get_queryset().filter(status=status_param)
        else:
            forms = self.get_queryset()

        serializer = self.get_serializer(forms, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def loan_amounts(self, request):
        """Get loan amount statistics."""
        queryset = self.get_queryset()

        stats = {
            "total_applications": queryset.count(),
            "total_requested_amount": sum(form.loan_amount for form in queryset),
            "average_loan_amount": queryset.aggregate(
                avg_amount=models.Avg("loan_amount")
            )["avg_amount"]
            or 0,
            "approved_applications": queryset.filter(status="approved").count(),
        }

        return Response(stats)


class InvestmentDeclarationFormViewSet(BaseFormViewSet):
    """ViewSet for investment declaration forms."""

    queryset = InvestmentDeclarationForm.objects.all()
    serializer_class = InvestmentDeclarationFormSerializer

    @action(detail=False, methods=["get"])
    def by_investment_type(self, request):
        """Filter investment forms by type."""
        investment_type = request.query_params.get("type")
        if investment_type:
            forms = self.get_queryset().filter(investment_type=investment_type)
        else:
            forms = self.get_queryset()

        serializer = self.get_serializer(forms, many=True)
        return Response(serializer.data)


class CustomFormViewSet(BaseFormViewSet):
    """ViewSet for custom forms."""

    queryset = CustomForm.objects.all()
    serializer_class = CustomFormSerializer

    @action(detail=True, methods=["get"])
    def fields(self, request, pk=None):
        """Get form fields configuration."""
        form = self.get_object()
        fields = form.fields.all().order_by("customformfield__order")
        serializer = FormFieldSerializer(fields, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def add_field(self, request, pk=None):
        """Add a field to the custom form (admin only)."""
        if not request.user.is_staff:
            return Response(
                {"error": "Admin access required"}, status=status.HTTP_403_FORBIDDEN
            )

        form = self.get_object()
        field_id = request.data.get("field_id")
        order = request.data.get("order", 0)

        try:
            field = FormField.objects.get(id=field_id)
            form.fields.add(field, through_defaults={"order": order})
            return Response({"message": "Field added successfully"})
        except FormField.DoesNotExist:
            return Response(
                {"error": "Field not found"}, status=status.HTTP_404_NOT_FOUND
            )


class FormSubmissionDataViewSet(viewsets.ModelViewSet):
    """ViewSet for custom form submission data."""

    queryset = FormSubmissionData.objects.all()
    serializer_class = FormSubmissionDataSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Filter submissions by current user if not admin."""
        if self.request.user.is_staff:
            return self.queryset
        return self.queryset.filter(custom_form__submitted_by=self.request.user)


class AllFormsViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet to get all forms across different types."""

    serializer_class = FormSummarySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Get all forms from different models."""
        # This is a simplified approach - in practice, you might want
        # to create a more sophisticated unified query
        forms = []

        # Get user's forms if not admin
        user_filter = (
            {} if self.request.user.is_staff else {"submitted_by": self.request.user}
        )

        # Add KYC forms
        kyc_forms = KYCForm.objects.filter(**user_filter).values(
            "id",
            "title",
            "status",
            "submitted_by__username",
            "created_at",
            "updated_at",
        )
        for form in kyc_forms:
            form["form_type"] = "KYC"
            form["submitted_by"] = form.pop("submitted_by__username")
            forms.append(form)

        # Add Loan forms
        loan_forms = LoanApplicationForm.objects.filter(**user_filter).values(
            "id",
            "title",
            "status",
            "submitted_by__username",
            "created_at",
            "updated_at",
        )
        for form in loan_forms:
            form["form_type"] = "Loan Application"
            form["submitted_by"] = form.pop("submitted_by__username")
            forms.append(form)

        # Add Investment forms
        investment_forms = InvestmentDeclarationForm.objects.filter(
            **user_filter
        ).values(
            "id",
            "title",
            "status",
            "submitted_by__username",
            "created_at",
            "updated_at",
        )
        for form in investment_forms:
            form["form_type"] = "Investment Declaration"
            form["submitted_by"] = form.pop("submitted_by__username")
            forms.append(form)

        # Add Custom forms
        custom_forms = CustomForm.objects.filter(**user_filter).values(
            "id",
            "title",
            "status",
            "submitted_by__username",
            "created_at",
            "updated_at",
        )
        for form in custom_forms:
            form["form_type"] = "Custom Form"
            form["submitted_by"] = form.pop("submitted_by__username")
            forms.append(form)

        # Sort by created_at descending
        forms.sort(key=lambda x: x["created_at"], reverse=True)

        return forms

    def list(self, request, *args, **kwargs):
        """List all forms with pagination."""
        queryset = self.get_queryset()

        # Apply search filter if provided
        search = request.query_params.get("search")
        if search:
            queryset = [
                form
                for form in queryset
                if search.lower() in form["title"].lower()
                or search.lower() in form["form_type"].lower()
            ]

        # Apply status filter if provided
        status_filter = request.query_params.get("status")
        if status_filter:
            queryset = [form for form in queryset if form["status"] == status_filter]

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
