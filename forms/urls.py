"""
URL configuration for the forms app.

Provides REST API endpoints for all form operations.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

# Create a router and register our viewsets
router = DefaultRouter()
router.register(r"files", views.FileUploadViewSet, basename="fileupload")
router.register(r"form-fields", views.FormFieldViewSet, basename="formfield")
router.register(r"kyc-forms", views.KYCFormViewSet, basename="kycform")
router.register(
    r"loan-applications", views.LoanApplicationFormViewSet, basename="loanapplication"
)
router.register(
    r"investment-declarations",
    views.InvestmentDeclarationFormViewSet,
    basename="investmentdeclaration",
)
router.register(r"custom-forms", views.CustomFormViewSet, basename="customform")
router.register(
    r"form-submissions", views.FormSubmissionDataViewSet, basename="formsubmission"
)
router.register(r"all-forms", views.AllFormsViewSet, basename="allforms")

app_name = "forms"

urlpatterns = [
    path("api/", include(router.urls)),
]
