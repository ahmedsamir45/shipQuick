# Quick Start Guide

Get the Bulk Shipping Label Platform running in 5 minutes.

## Prerequisites

- Python 3.8+ installed
- pip package manager

## Installation Steps

### 1. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env if you have API keys (optional)
# For basic testing, the defaults work fine
```

### 4. Initialize Database

```bash
# Create database tables
python manage.py makemigrations
python manage.py migrate

# Load sample saved addresses and packages
python manage.py load_sample_data
```

### 5. Create Admin User (Optional)

```bash
python manage.py createsuperuser
# Follow prompts to create username/password
```

### 6. Start Server

```bash
python manage.py runserver
```

Server is now running at: **http://localhost:8000**

---

## Testing the API

### Option 1: Use DRF Browsable API

Visit: **http://localhost:8000/api/**

You can interact with all endpoints through the web interface.

### Option 2: Use curl

**1. Create a new upload session:**

```bash
curl -X POST http://localhost:8000/api/sessions/ \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Response:**
```json
{
  "id": "abc-123-def-456",
  "status": "draft",
  "total_shipments": 0,
  ...
}
```

**2. Upload the sample CSV:**

```bash
curl -X POST http://localhost:8000/api/sessions/abc-123-def-456/upload_csv/ \
  -F "file=@Sample_Upload.csv"
```

**3. View shipments:**

```bash
curl http://localhost:8000/api/shipments/?session=abc-123-def-456
```

**4. Get session summary:**

```bash
curl http://localhost:8000/api/sessions/abc-123-def-456/summary/
```

**5. Purchase the session:**

```bash
curl -X POST http://localhost:8000/api/sessions/abc-123-def-456/purchase/ \
  -H "Content-Type: application/json" \
  -d '{
    "label_size": "4x6",
    "terms_accepted": true
  }'
```

### Option 3: Use Django Admin

Visit: **http://localhost:8000/admin/**

Login with the superuser credentials you created.

Browse and manage all data through the admin interface.

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/sessions/` | GET | List all upload sessions |
| `/api/sessions/` | POST | Create new session |
| `/api/sessions/{id}/upload_csv/` | POST | Upload CSV file |
| `/api/sessions/{id}/purchase/` | POST | Confirm purchase |
| `/api/sessions/{id}/summary/` | GET | Get summary |
| `/api/shipments/` | GET | List shipments |
| `/api/shipments/{id}/` | GET/PUT/DELETE | Manage shipment |
| `/api/saved-addresses/` | GET | List saved addresses |
| `/api/saved-packages/` | GET | List saved packages |

See [README.md](README.md) for complete API documentation.

---

## Sample Workflow

```
1. Create Session
   POST /api/sessions/

2. Upload CSV
   POST /api/sessions/{id}/upload_csv/
   (System automatically validates addresses and assigns shipping services)

3. Review Shipments
   GET /api/shipments/?session={id}

4. Edit if Needed
   PUT /api/shipments/{shipment_id}/
   POST /api/shipments/bulk_update_address/

5. Purchase
   POST /api/sessions/{id}/purchase/
   (Session is locked, no further edits)
```

---

## Common Issues

### Port 8000 Already in Use

```bash
# Windows: Find and kill process
netstat -ano | findstr :8000
taskkill /PID <process_id> /F

# Mac/Linux:
lsof -ti:8000 | xargs kill -9
```

### ImportError or Module Not Found

Make sure virtual environment is activated:

```bash
# Check if (venv) appears in your prompt
# If not, activate it:
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
```

### Database Locked

Close any database browsers (e.g., DB Browser for SQLite) and restart server.

---

## Next Steps

- Read [README.md](README.md) for detailed documentation
- Check [DATABASE_DESIGN.md](DATABASE_DESIGN.md) for schema details
- Review [Sample_Upload.csv](Sample_Upload.csv) for CSV format
- Explore the code in `shipping/` directory

---

## Production Deployment

For production deployment, see the "Deployment" section in [README.md](README.md).

Key changes needed:
- Set `DEBUG=False`
- Use PostgreSQL instead of SQLite
- Configure real address validation APIs
- Set up HTTPS
- Use production WSGI server (Gunicorn)

---

**Happy Shipping! 🚚📦**
