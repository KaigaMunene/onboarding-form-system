# Dynamic Onboarding Form System

**Actserv Full Stack Developer Assessment**

A comprehensive, scalable onboarding form system for financial services firms, built with Django and Django REST Framework using a hybrid model architecture.

## 🎯 Project Overview

This system addresses the challenge of creating a flexible, future-proof onboarding platform that can handle:

- **Unknown and unbounded** number of form types
- **Variable field requirements** (2-3 fields to 20+ fields)
- **Multiple file uploads** per form
- **Custom validation rules** per form type
- **Admin notifications** for new submissions
- **Dynamic form creation** without code changes

## 🏗️ Architecture Highlights

### Hybrid Model Approach

- **BaseForm**: Abstract model with common functionality
- **Specific Models**: KYC, Loan Application, Investment Declaration
- **Dynamic Models**: CustomForm with configurable fields
- **File Management**: Secure upload system with validation

### Key Benefits

✅ **Scalable**: Handle unlimited form types  
✅ **Flexible**: Add forms without code changes  
✅ **Secure**: Multi-layer validation & file security  
✅ **Maintainable**: Clean separation of concerns  
✅ **Admin-Friendly**: Comprehensive Django admin interface

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Django 5.2+
- PostgreSQL (recommended) or SQLite for development

### Installation

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd onboarding-form-system
   ```

2. **Create virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Environment setup**

   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Database setup**

   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

6. **Run the server**
   ```bash
   python manage.py runserver
   ```

## 📋 Form Types

### 1. KYC Form (Know Your Customer)

**Purpose**: Identity verification and compliance

- Personal information (name, DOB, nationality)
- Contact details with validation
- Identity document upload and verification
- Address proof requirements

### 2. Loan Application Form

**Purpose**: Loan processing with financial validation

- Loan details (amount, purpose, term)
- Financial information (income, employment)
- Business logic validation (loan-to-income ratios)
- Supporting document uploads

### 3. Investment Declaration Form

**Purpose**: Investment planning and risk assessment

- Investment preferences and amounts
- Risk tolerance assessment
- Financial background verification
- Portfolio documentation

### 4. Custom Forms

**Purpose**: Admin-created dynamic forms

- Configurable field types and validation
- Flexible JSON data storage
- Deadline management
- Multiple submission control

## 🔧 API Endpoints

### Authentication Required

All endpoints require authentication. Use Django's built-in authentication or DRF token authentication.

### Core Endpoints

```
GET/POST   /forms/api/kyc-forms/              # KYC form operations
GET/POST   /forms/api/loan-applications/      # Loan application operations
GET/POST   /forms/api/investment-declarations/ # Investment form operations
GET/POST   /forms/api/custom-forms/           # Dynamic form operations
GET/POST   /forms/api/files/                  # File upload management
GET        /forms/api/all-forms/              # Unified form listing
```

### Form Actions

```
POST /forms/api/kyc-forms/{id}/submit/        # Submit form for review
POST /forms/api/kyc-forms/{id}/approve/       # Approve form (admin)
POST /forms/api/kyc-forms/{id}/reject/        # Reject form (admin)
POST /forms/api/kyc-forms/{id}/request_changes/ # Request changes (admin)
```

### Example API Usage

**Create a KYC Form:**

```json
POST /forms/api/kyc-forms/
{
    "title": "John Doe KYC Verification",
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "phone_number": "+1-555-123-4567",
    "date_of_birth": "1990-01-15",
    "nationality": "US",
    "address_line_1": "123 Main St",
    "city": "New York",
    "state_province": "NY",
    "postal_code": "10001",
    "country": "United States",
    "identity_document_type": "passport",
    "identity_document_number": "AB1234567",
    "identity_document_expiry": "2030-12-31"
}
```

**Upload Files:**

```bash
curl -X POST \
  -H "Authorization: Token your-token" \
  -F "file=@document.pdf" \
  -F "field_name=identity_document_front" \
  http://localhost:8000/forms/api/files/
```

## 🔒 Security Features

### File Upload Security

- **MIME type validation**: Prevents malicious file uploads
- **File size limits**: 10MB maximum per file
- **Allowed extensions**: PDF, DOC, DOCX, JPG, JPEG, PNG, TXT
- **Secure storage**: Date-organized file structure

### Data Validation

- **Phone number validation**: International format support
- **Financial validation**: Business-appropriate ranges
- **Document validation**: Format and expiry checks
- **Cross-field validation**: Business logic enforcement

### Access Control

- **User-based access**: Users see only their forms
- **Admin permissions**: Full access for staff users
- **UUID primary keys**: Prevent enumeration attacks

## 🎛️ Admin Interface

Access the Django admin at `/admin/` with superuser credentials.

### Admin Features

- **Form Review**: Approve, reject, or request changes
- **Dynamic Fields**: Create and configure form fields
- **File Management**: View and manage uploaded documents
- **User Management**: Track submissions by user
- **Bulk Actions**: Mass operations on forms
- **Custom Views**: Form-type specific interfaces

### Creating Dynamic Forms

1. Go to **Form Fields** in admin
2. Create fields with validation rules
3. Go to **Custom Forms**
4. Create form and associate fields
5. Users can now submit data to your custom form

## 📧 Notification System

### Admin Notifications

- **Trigger**: New form submissions
- **Method**: Email with HTML templates
- **Content**: Form details and direct admin links
- **Async Ready**: Celery integration placeholder

### User Notifications

- **Status Updates**: Approval, rejection, change requests
- **Email Templates**: Professional, branded emails
- **Tracking**: Notification history and delivery status

### Email Configuration

Add to your `.env` file:

```
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=noreply@yourcompany.com
```

## 🧪 Testing

### Run Tests

```bash
python manage.py test forms
```

### Test Coverage

- Model validation
- API endpoints
- File upload security
- Business logic validation
- Notification system

## 📁 Project Structure

```
onboarding-form-system/
├── forms/                          # Main forms app
│   ├── models.py                   # Base models and imports
│   ├── specific_models.py          # KYC, Loan, Investment models
│   ├── dynamic_models.py           # CustomForm and dynamic models
│   ├── validators.py               # Custom validation logic
│   ├── serializers.py              # DRF serializers
│   ├── views.py                    # API views
│   ├── admin.py                    # Django admin configuration
│   ├── notifications.py            # Email notification system
│   ├── urls.py                     # URL routing
│   └── templates/                  # Email templates
│       └── forms/emails/
├── onboarding_system/              # Django project settings
│   ├── settings/                   # Environment-specific settings
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   └── urls.py
├── requirements.txt                # Production dependencies
├── requirements-dev.txt            # Development dependencies
├── ARCHITECTURE.md                 # Detailed architecture documentation
└── README.md                       # This file
```

## 🔄 Development Workflow

### Adding New Form Types

1. Create model inheriting from `BaseForm`
2. Add to `specific_models.py`
3. Create serializer in `serializers.py`
4. Add ViewSet in `views.py`
5. Register in admin.py
6. Add URL routing
7. Run migrations

### Adding New Field Types

1. Add to `FieldType` choices in `models.py`
2. Update `FormFieldValidator` in `validators.py`
3. Update frontend form rendering (if applicable)

## 🚀 Deployment

### Environment Variables

```bash
# Required
SECRET_KEY=your-secret-key
DATABASE_URL=postgres://user:pass@host:port/dbname
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Email (optional but recommended)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=True
```

### Production Checklist

- [ ] Set `DEBUG=False`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Set up PostgreSQL database
- [ ] Configure email settings
- [ ] Set up file storage (AWS S3 recommended)
- [ ] Configure HTTPS
- [ ] Set up monitoring and logging
- [ ] Configure backup strategy

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

For questions or support regarding this assessment project, please contact the development team.

---

**Built with ❤️ for Actserv Full Stack Developer Assessment**
