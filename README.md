# Bulk Shipping Label Creation Platform - Backend

Production-ready Django + DRF backend for bulk shipping label creation.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Features](#features)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Address Validation Strategy](#address-validation-strategy)
- [Shipping Rate Calculation](#shipping-rate-calculation)
- [CSV Format](#csv-format)
- [Database Schema](#database-schema)
- [Logging](#logging)
- [Testing](#testing)
- [Deployment](#deployment)
- [Assumptions & Design Decisions](#assumptions--design-decisions)

---

## Overview

This backend provides REST APIs for a bulk shipping label creation platform that allows users to:

1. Upload CSV files containing shipment data
2. Automatically validate addresses with fallback providers
3. Review and edit shipment details
4. Select shipping services with automatic tier assignment
5. Bulk update addresses, packages, and shipping services
6. Purchase and lock shipment sessions

All business logic lives on the server side, with comprehensive validation, error handling, and production-ready logging.

---

## Architecture

### Layered Architecture

```
┌─────────────────────────────────────┐
│         REST API Layer              │
│      (Views & Serializers)          │
├─────────────────────────────────────┤
│       Services Layer                │
│  - CSV Parser                       │
│  - Address Validator (w/ Fallback)  │
│  - Shipping Calculator              │
├─────────────────────────────────────┤
│         Models Layer                │
│  (Domain Models & Business Logic)   │
├─────────────────────────────────────┤
│         Database (SQLite)           │
└─────────────────────────────────────┘
```

### Key Components

**Models** (`shipping/models.py`)
- `UploadSession`: Container for batch uploads
- `Shipment`: Individual shipment record
- `Address`: Ship From/To addresses with validation metadata
- `Package`: Package dimensions and weight
- `ShippingServiceSelection`: Shipping service and pricing
- `SavedAddress`: Reusable ship-from addresses
- `SavedPackage`: Reusable package presets

**Services** (`shipping/services/`)
- `CSVParserService`: Parses 2-header CSV files
- `AddressValidatorService`: Validates addresses with fallback mechanism
- `ShippingCalculatorService`: Calculates rates based on weight tiers

**Views** (`shipping/views.py`)
- RESTful ViewSets for all models
- Custom actions for CSV upload, bulk operations, purchase

---

## Tech Stack

- **Python** 3.x
- **Django** 5.0.1
- **Django REST Framework** 3.14.0
- **SQLite** (database)
- **pandas** (CSV parsing)
- **requests/httpx** (API calls)
- **python-json-logger** (structured logging)

---

## Features

### ✅ Step 1: CSV Upload & Parsing

- Upload CSV files with 2-header row format (23 columns)
- Parse and persist shipment data to database
- Gracefully handle missing/incomplete data
- Automatic address validation after upload
- Validation failures marked as warnings (non-blocking)

### ✅ Step 2: Review & Edit

- Fetch all shipments for a session
- Edit individual shipment addresses/packages
- Re-validate addresses on every edit
- Delete individual or bulk shipments
- Bulk update ship-from address from saved presets
- Bulk update package from saved presets
- CRUD APIs for saved addresses and packages

### ✅ Step 3: Shipping Service Selection

- Automatic tier assignment based on weight:
  - 0-4 oz → Tier 1
  - 4-8 oz → Tier 2
  - 8-12 oz → Tier 3
  - 12-16 oz → Tier 4
  - 16+ oz → Tier 5
- Ground shipping only if weight < 16 oz
- Fractional weights round up
- Manual service override supported
- Bulk shipping service updates
- Running total calculation per session

### ✅ Step 4: Purchase (Simulation)

- Confirm purchase with label size and terms acceptance
- Lock session to prevent further edits
- Validation: no errors, at least one shipment
- Return success summary

### ✅ Address Validation with Fallback

- Primary provider: USPS (configurable)
- Fallback provider: Google Maps (configurable)
- Additional providers: Smarty Streets, Lob
- Automatic fallback on primary failure
- Rate limit handling
- Stores validation metadata per address
- Validation failures don't block workflow

### ✅ Production Features

- Comprehensive structured logging (JSON format)
- Transaction management for data integrity
- Custom exception handling with clear error responses
- Session locking to prevent edits after purchase
- Proper HTTP status codes
- Database indexes for performance
- Field-level validation

---

## Installation

### Prerequisites

- Python 3.8+ installed
- pip package manager

### Setup Steps

1. **Create virtual environment**

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. **Create environment file**

```bash
cp .env.example .env
```

Edit `.env` with your API keys (optional for basic validation):

```env
SECRET_KEY=your-secret-key-here
DEBUG=True

# Address Validation (optional - uses basic validation if not set)
PRIMARY_ADDRESS_VALIDATOR=usps
USPS_API_KEY=your-usps-api-key
GOOGLE_MAPS_API_KEY=your-google-api-key
```

4. **Run migrations**

```bash
python manage.py makemigrations
python manage.py migrate
```

5. **Load sample data**

```bash
python manage.py load_sample_data
```

This creates demo saved addresses and packages.

6. **Create superuser (optional)**

```bash
python manage.py createsuperuser
```

---

## Configuration

### Environment Variables

See `.env.example` for all available settings.

**Key Settings:**

- `SECRET_KEY`: Django secret key (change in production!)
- `DEBUG`: Debug mode (False in production)
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts
- `PRIMARY_ADDRESS_VALIDATOR`: usps, google, smarty, or lob
- `FALLBACK_ADDRESS_VALIDATOR`: Secondary provider for fallback
- API keys for each validation provider
- `LOG_LEVEL`: INFO, DEBUG, WARNING, ERROR
- `CORS_ALLOWED_ORIGINS`: Frontend URLs for CORS

### Address Validation Providers

Configure in `shipping_backend/settings.py` under `ADDRESS_VALIDATION`.

**Without API Keys:**
- System falls back to basic validation (required fields, ZIP format)
- Still functional, but no address normalization

**With API Keys:**
- Full address validation and normalization
- Automatic fallback between providers

---

## Running the Application

### Development Server

```bash
python manage.py runserver
```

Server runs at: `http://localhost:8000`

**Key URLs:**

- **Swagger UI (API Docs)**: `http://localhost:8000/api/docs/` - Interactive API documentation
- **ReDoc**: `http://localhost:8000/api/redoc/` - Beautiful API documentation
- **API Root**: `http://localhost:8000/api/` - API endpoints
- **Django Admin**: `http://localhost:8000/admin/` - Admin interface

### API Documentation Interface

The API includes **Swagger UI** for interactive documentation:

1. Visit [http://localhost:8000/api/docs/](http://localhost:8000/api/docs/)
2. Browse all available endpoints
3. Click "Try it out" on any endpoint
4. Test API calls directly from your browser
5. See request/response examples with schemas

**Benefits:**
- No need for Postman or curl
- All endpoints documented automatically
- See request/response formats
- Try API calls interactively
- Download OpenAPI schema

---

## API Documentation

### Interactive API Documentation

The API is fully documented using **OpenAPI 3.0 (Swagger)** specification.

**Live Documentation (when server is running):**

- **Swagger UI**: [http://localhost:8000/api/docs/](http://localhost:8000/api/docs/)
  - Interactive API explorer
  - Try out API calls directly from browser
  - See request/response examples
  - Download OpenAPI schema

- **ReDoc**: [http://localhost:8000/api/redoc/](http://localhost:8000/api/redoc/)
  - Beautiful, responsive documentation
  - Better for reading and sharing
  - Mobile-friendly

- **OpenAPI Schema**: [http://localhost:8000/api/schema/](http://localhost:8000/api/schema/)
  - Raw OpenAPI 3.0 schema (YAML)
  - Import into Postman, Insomnia, etc.

**Production URLs (after deployment):**
- Swagger UI: `https://your-app.koyeb.app/api/docs/`
- ReDoc: `https://your-app.koyeb.app/api/redoc/`

### Base URL

```
Development: http://localhost:8000/api/
Production:  https://your-app.koyeb.app/api/
```

### Core Endpoints

#### Upload Sessions

```
GET    /api/sessions/                      - List all sessions
POST   /api/sessions/                      - Create new session
GET    /api/sessions/{id}/                 - Get session details
PUT    /api/sessions/{id}/                 - Update session
DELETE /api/sessions/{id}/                 - Delete session
POST   /api/sessions/{id}/upload_csv/      - Upload CSV file
POST   /api/sessions/{id}/purchase/        - Confirm purchase
GET    /api/sessions/{id}/summary/         - Get session summary
```

#### Shipments

```
GET    /api/shipments/                     - List shipments (filter by ?session={id})
POST   /api/shipments/                     - Create shipment
GET    /api/shipments/{id}/                - Get shipment details
PUT    /api/shipments/{id}/                - Update shipment
DELETE /api/shipments/{id}/                - Delete shipment
POST   /api/shipments/bulk_delete/         - Bulk delete
POST   /api/shipments/bulk_update_address/ - Bulk update ship-from
POST   /api/shipments/bulk_update_package/ - Bulk update package
POST   /api/shipments/bulk_update_service/ - Bulk update service
```

#### Saved Addresses & Packages

```
GET    /api/saved-addresses/               - List saved addresses
POST   /api/saved-addresses/               - Create saved address
GET    /api/saved-packages/                - List saved packages
POST   /api/saved-packages/                - Create saved package
```

**For complete, interactive documentation, visit [http://localhost:8000/api/docs/](http://localhost:8000/api/docs/) when the server is running.**

### Example API Calls

**1. Create Upload Session**

```bash
curl -X POST http://localhost:8000/api/sessions/ \
  -H "Content-Type: application/json" \
  -d '{}'
```

**2. Upload CSV**

```bash
curl -X POST http://localhost:8000/api/sessions/{session_id}/upload_csv/ \
  -F "file=@shipments.csv"
```

**3. Get Session Summary**

```bash
curl http://localhost:8000/api/sessions/{session_id}/summary/
```

**4. Purchase Session**

```bash
curl -X POST http://localhost:8000/api/sessions/{session_id}/purchase/ \
  -H "Content-Type: application/json" \
  -d '{
    "label_size": "4x6",
    "terms_accepted": true
  }'
```

**5. Bulk Update Ship-From Address**

```bash
curl -X POST http://localhost:8000/api/shipments/bulk_update_address/ \
  -H "Content-Type: application/json" \
  -d '{
    "shipment_ids": ["uuid1", "uuid2"],
    "saved_address_id": "saved-address-uuid"
  }'
```

---

## Address Validation Strategy

### Multi-Provider Fallback Architecture

```
┌─────────────────────┐
│  Primary Provider   │
│      (USPS)         │
└──────────┬──────────┘
           │
           ▼
    Success? ──Yes──> Mark Valid
           │
          No
           │
           ▼
┌─────────────────────┐
│ Fallback Provider   │
│   (Google Maps)     │
└──────────┬──────────┘
           │
           ▼
    Success? ──Yes──> Mark Fallback Valid
           │
          No
           │
           ▼
    Mark Invalid (Warning)
```

### Validation Flow

1. **Store Original Input**: Save user-entered address
2. **Primary Validation**: Call primary provider (e.g., USPS)
3. **On Failure**: Automatically try fallback provider
4. **Store Metadata**: Log which provider was used
5. **Update Status**: `valid`, `fallback_valid`, or `invalid`
6. **Non-Blocking**: Validation failures are warnings, not errors

### Provider Configuration

Set in `.env`:

```env
PRIMARY_ADDRESS_VALIDATOR=usps
FALLBACK_ADDRESS_VALIDATOR=google

USPS_API_KEY=your-key
GOOGLE_MAPS_API_KEY=your-key
```

### Supported Providers

- **USPS**: US Postal Service Web Tools
- **Google**: Google Address Validation API
- **Smarty Streets**: SmartyStreets US Street Address API
- **Lob**: Lob Address Verification API

**Note**: Current implementation includes mock validation. Integrate real APIs by updating [shipping/services/address_validator.py](shipping/services/address_validator.py).

---

## Shipping Rate Calculation

### Weight-Based Tier Assignment

| Weight Range | Tier   | Priority Mail | Ground Shipping |
|--------------|--------|---------------|-----------------|
| 0-4 oz       | Tier 1 | $4.50         | $3.50           |
| 4-8 oz       | Tier 2 | $5.75         | $4.25           |
| 8-12 oz      | Tier 3 | $7.00         | $5.00           |
| 12-16 oz     | Tier 4 | $8.25         | $5.75           |
| 16+ oz       | Tier 5 | $9.50         | N/A             |

### Business Rules

1. **Auto-Assignment**: Default service assigned on shipment creation
2. **Ground Restriction**: Only available if weight < 16 oz
3. **Weight Rounding**: Fractional weights round up
4. **Missing Weight**: Defaults to Priority Mail Tier 1
5. **Manual Override**: Users can manually change service type
6. **Recalculation**: Service recalculated when package weight changes

### Implementation

See [shipping/services/shipping_calculator.py](shipping/services/shipping_calculator.py)

Pricing table defined in [shipping/constants.py](shipping/constants.py)

---

## CSV Format

### Expected Structure

- **Row 1**: Header labels (human-readable, ignored by parser)
- **Row 2**: Field names (used for mapping, ignored)
- **Row 3+**: Data rows

### Columns (23 Total)

1. Ship From Name *
2. Ship From Company
3. Ship From Street1 *
4. Ship From Street2
5. Ship From City *
6. Ship From State *
7. Ship From ZIP *
8. Ship From Phone
9. Ship From Email
10. Ship To Name *
11. Ship To Company
12. Ship To Street1 *
13. Ship To Street2
14. Ship To City *
15. Ship To State *
16. Ship To ZIP *
17. Ship To Phone
18. Ship To Email
19. Package Length *
20. Package Width *
21. Package Height *
22. Package Weight (oz) *
23. Reference Number

\* = Required field

### Example CSV

See [Template.csv](Template.csv) for a sample template.

```csv
Ship From Name,Ship From Company,...,Package Weight,Reference
Name,Company,...,Weight,Ref
John Doe,ACME Inc,...,8.5,ORD-001
Jane Smith,XYZ Corp,...,3.2,ORD-002
```

### Parsing Logic

- Empty rows are skipped
- Missing required fields result in `error` status
- Invalid numeric values default to 1.0 with warnings
- All errors/warnings stored in shipment's `validation_messages`

---

## Database Schema

See [DATABASE_DESIGN.md](DATABASE_DESIGN.md) for complete schema documentation.

### Entity Relationships

```
UploadSession (1) ──< (N) Shipment
Shipment (1) ──< (2) Address [ship_from, ship_to]
Shipment (1) ── (1) Package
Shipment (1) ── (1) ShippingServiceSelection

SavedAddress (independent)
SavedPackage (independent)
```

### Database Configuration

The application supports both SQLite (development) and PostgreSQL (production):

**Development (SQLite):**
```env
DB_ENGINE=sqlite
```

**Production (PostgreSQL):**
```env
DB_ENGINE=postgresql
DB_NAME=defaultdb
DB_USER=avnadmin
DB_PASSWORD=your-password
DB_HOST=your-database-host.com
DB_PORT=21388
DB_SSLMODE=require
```

Currently configured with **Aiven PostgreSQL** for production deployment.

### Key Tables

- **upload_sessions**: Batch upload workflows
- **shipments**: Individual shipment records
- **addresses**: Ship from/to addresses with validation metadata
- **packages**: Package dimensions and weight
- **shipping_service_selections**: Service and pricing
- **saved_addresses**: Reusable ship-from addresses
- **saved_packages**: Reusable package presets

---

## Logging

### Structured JSON Logging

All logs written in JSON format for production parsing.

**Log File**: `logs/shipping_platform.log`

**Log Rotation**: 10 MB per file, 5 backups

### Log Levels

- **INFO**: Normal operations (CSV upload, validation, purchase)
- **WARNING**: Non-critical issues (fallback used, missing data)
- **ERROR**: Failures (validation errors, API failures)
- **DEBUG**: Detailed debugging info

### Example Log Entry

```json
{
  "timestamp": "2026-01-31T10:30:00.000Z",
  "level": "INFO",
  "name": "shipping.services.csv_parser",
  "message": "CSV parsing completed for session abc-123",
  "session_id": "abc-123",
  "shipments_created": 50
}
```

### Viewing Logs

```bash
# Tail logs in real-time
tail -f logs/shipping_platform.log

# View formatted logs (requires jq)
tail -f logs/shipping_platform.log | jq .
```

---

## Testing

### Manual Testing via Admin

1. Access Django admin: `http://localhost:8000/admin/`
2. View/edit all models
3. Check validation metadata

### Manual Testing via API

Use DRF browsable API or tools like Postman, curl, httpie.

### Automated Tests (Future)

Create tests in `shipping/tests/`:

```bash
python manage.py test shipping
```

---

## Deployment

This application is ready for production deployment with multiple options.

### Recommended: Koyeb Deployment

Deploy your backend to **Koyeb** (serverless platform) with PostgreSQL database.

**Quick Setup:**

1. Push code to GitHub/GitLab
2. Connect to Koyeb
3. Configure environment variables
4. Deploy automatically

**Complete Guide:** See [KOYEB_DEPLOYMENT.md](KOYEB_DEPLOYMENT.md)

**Database:** Aiven PostgreSQL (already configured)

### Alternative: Docker Deployment

Deploy using Docker containers with PostgreSQL and Nginx.

**Quick Start:**
```bash
docker-compose up -d
```

**Includes:**
- PostgreSQL database container
- Django backend with Gunicorn
- Nginx reverse proxy

**Complete Guide:** See [DEPLOYMENT.md](DEPLOYMENT.md) for Docker setup

### Alternative: VPS Deployment

Deploy to a traditional VPS (AWS EC2, DigitalOcean, etc.)

**Requirements:**
- Ubuntu 20.04+ or similar
- PostgreSQL 14+
- Nginx
- Systemd service

**Complete Guide:** See [DEPLOYMENT.md](DEPLOYMENT.md) for VPS setup

### Alternative: Platform Deployment

Deploy to Heroku, Railway, or Render.

**Requirements:**
- Procfile (included)
- runtime.txt (included)
- Set environment variables on platform

**Complete Guide:** See [DEPLOYMENT.md](DEPLOYMENT.md)

### Production Checklist

Before deploying:

- [ ] Set `DEBUG=False`
- [ ] Generate strong `SECRET_KEY`
- [ ] Configure `ALLOWED_HOSTS` with your domain
- [ ] Set `DB_ENGINE=postgresql`
- [ ] Configure PostgreSQL connection (Aiven credentials)
- [ ] Set `DB_SSLMODE=require` for cloud databases
- [ ] Configure `CORS_ALLOWED_ORIGINS` with frontend URL (Vercel)
- [ ] Set production API keys (USPS, Google Maps, etc.)
- [ ] Run `python manage.py migrate`
- [ ] Run `python manage.py collectstatic`
- [ ] Configure monitoring and logging
- [ ] Test all API endpoints

### Deployment Files

All necessary deployment files are included:

- `Dockerfile` - Container image definition
- `docker-compose.yml` - Multi-container orchestration
- `nginx.conf` - Nginx reverse proxy config
- `Procfile` - Platform deployment (Heroku/Railway)
- `runtime.txt` - Python version specification
- `.dockerignore` - Excludes unnecessary files
- `deploy.sh` - Automated deployment script
- `.env.production.example` - Production environment template

### Frontend Integration

The backend is configured to work with a Vercel-deployed frontend:

1. Backend deploys to Koyeb: `https://your-app-koyeb.app`
2. Frontend deploys to Vercel: `https://your-app.vercel.app`
3. Update `CORS_ALLOWED_ORIGINS` in backend with Vercel URL
4. Update `VITE_API_BASE_URL` in Vercel with Koyeb URL

**Frontend Deployment Guide:** See [VERCEL_DEPLOYMENT.md](VERCEL_DEPLOYMENT.md)

---

## Assumptions & Design Decisions

### Assumptions

1. **No Authentication**: All endpoints are public
   - _Rationale_: PRD specifies no auth requirement
   - _Production Note_: Add authentication for real deployment

2. **Domestic Only**: US addresses only
   - _Rationale_: Simplifies validation
   - _Future_: Add international support with customs handling

3. **Single Currency**: USD only
   - _Rationale_: US domestic shipping
   - _Future_: Multi-currency for international

4. **SQLite Database**: For development/demo
   - _Rationale_: Zero configuration, easy setup
   - _Production_: Migrate to PostgreSQL

5. **Weight in Ounces**: Internal standard
   - _Rationale_: Matches USPS pricing tiers
   - _Conversion_: Automatic conversion from lb/g/kg

6. **Mock Address Validation**: Basic validation if no API keys
   - _Rationale_: Allows testing without API credentials
   - _Production_: Configure real API providers

### Design Decisions

1. **Layered Architecture**: Separation of concerns
   - Models (domain logic)
   - Services (business logic)
   - Views (orchestration)

2. **Services Layer**: Reusable business logic
   - CSV parsing
   - Address validation
   - Shipping calculation

3. **Fallback Mechanism**: Resilient address validation
   - Primary → Fallback → Basic validation
   - Never blocks workflow

4. **Non-Blocking Validation**: Warnings vs Errors
   - Address validation failures = warnings
   - Missing required fields = errors
   - Only errors block purchase

5. **Session Locking**: Immutable after purchase
   - Prevents accidental edits
   - Maintains data integrity

6. **Automatic Service Assignment**: Smart defaults
   - Based on package weight
   - User can override

7. **Bulk Operations**: Efficient editing
   - Update multiple shipments at once
   - Transaction-based for consistency

8. **Comprehensive Logging**: Production-ready observability
   - Structured JSON logs
   - Contextual metadata
   - Log rotation

9. **UUID Primary Keys**: Scalability
   - No sequential ID leakage
   - Better for distributed systems

10. **Validation on Edit**: Always re-validate
    - Address changes → re-validate
    - Package changes → recalculate shipping

### Required Fields

**Determined through business logic analysis:**

**Ship From/To Address:**
- name, street1, city, state, zip_code

**Package:**
- length, width, height, weight

**Rationale**: Minimum data needed for shipping label creation.

---

## API Error Responses

All errors follow consistent format:

```json
{
  "error": "Human-readable error message",
  "status_code": 400,
  "details": {
    "field_name": "Specific error for this field"
  }
}
```

### Common Status Codes

- `200 OK`: Success
- `201 Created`: Resource created
- `400 Bad Request`: Validation error
- `403 Forbidden`: Session locked
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Address validation failed
- `500 Internal Server Error`: Server error

---

## Project Structure

```
ship task/
├── shipping_backend/          # Django project
│   ├── __init__.py
│   ├── settings.py           # Configuration
│   ├── urls.py               # Root URLs
│   ├── wsgi.py               # WSGI config
│   └── asgi.py               # ASGI config
├── shipping/                  # Main app
│   ├── management/
│   │   └── commands/
│   │       └── load_sample_data.py
│   ├── services/              # Business logic
│   │   ├── csv_parser.py
│   │   ├── address_validator.py
│   │   └── shipping_calculator.py
│   ├── admin.py              # Django admin
│   ├── apps.py
│   ├── constants.py          # Constants and choices
│   ├── exceptions.py         # Custom exceptions
│   ├── models.py             # Database models
│   ├── serializers.py        # DRF serializers
│   ├── urls.py               # API routes
│   └── views.py              # API views
├── logs/                      # Log files
├── media/                     # Uploaded files
├── .env.example              # Environment template
├── manage.py                 # Django CLI
├── requirements.txt          # Dependencies
├── DATABASE_DESIGN.md        # Schema documentation
└── README.md                 # This file
```

---

## Support & Contact

For questions or issues, please refer to the codebase documentation or contact the development team.

---

## License

Proprietary - All rights reserved

---

**Built with ❤️ using Django + Django REST Framework**
