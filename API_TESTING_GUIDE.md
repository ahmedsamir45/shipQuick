# API Testing Guide

Complete guide for testing all API endpoints of the Bulk Shipping Label Platform.

## Setup

Make sure the server is running:

```bash
python manage.py runserver
```

Base URL: `http://localhost:8000/api/`

---

## 1. Upload Session Flow (Complete Workflow)

### Step 1: Create New Session

**Request:**
```bash
curl -X POST http://localhost:8000/api/sessions/ \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Expected Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "draft",
  "status_display": "Draft",
  "total_shipments": 0,
  "valid_shipments": 0,
  "warning_shipments": 0,
  "error_shipments": 0,
  "is_locked": false,
  "purchase_date": null,
  "label_size": null,
  "label_size_display": null,
  "terms_accepted": false,
  "can_edit": true,
  "total_price": "0.00",
  "created_at": "2026-01-31T10:00:00.000000Z",
  "updated_at": "2026-01-31T10:00:00.000000Z"
}
```

**Save the `id` for subsequent requests.**

---

### Step 2: Upload CSV File

**Request:**
```bash
curl -X POST http://localhost:8000/api/sessions/{session_id}/upload_csv/ \
  -F "file=@Sample_Upload.csv"
```

**Expected Response:**
```json
{
  "message": "CSV uploaded and processed successfully",
  "result": {
    "success": true,
    "shipments_created": 10,
    "total_rows": 10,
    "errors": [],
    "warnings": [],
    "session_id": "550e8400-e29b-41d4-a716-446655440000"
  },
  "session": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "in_review",
    "total_shipments": 10,
    "valid_shipments": 10,
    "warning_shipments": 0,
    "error_shipments": 0,
    "shipments": [...]
  }
}
```

**What Happens Automatically:**
1. CSV is parsed (skipping 2 header rows)
2. Shipments, addresses, and packages are created
3. Addresses are validated (using basic validation or configured API)
4. Shipping services are auto-assigned based on weight
5. Session status changes to `in_review`

---

### Step 3: Get Session Summary

**Request:**
```bash
curl http://localhost:8000/api/sessions/{session_id}/summary/
```

**Expected Response:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "in_review",
  "total_shipments": 10,
  "valid_shipments": 10,
  "warning_shipments": 0,
  "error_shipments": 0,
  "total_price": "68.25",
  "is_locked": false,
  "can_purchase": true
}
```

---

### Step 4: List Shipments in Session

**Request:**
```bash
curl "http://localhost:8000/api/shipments/?session={session_id}"
```

**Expected Response:**
```json
{
  "count": 10,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "shipment-uuid-1",
      "csv_row_number": 3,
      "status": "valid",
      "status_display": "Valid",
      "ship_from_summary": "John Smith - Los Angeles, CA",
      "ship_to_summary": "Alice Johnson - San Francisco, CA",
      "shipping_price": "7.00",
      "reference_number": "ORD-1001",
      "created_at": "2026-01-31T10:00:01.000000Z"
    },
    ...
  ]
}
```

---

### Step 5: Get Individual Shipment Details

**Request:**
```bash
curl http://localhost:8000/api/shipments/{shipment_id}/
```

**Expected Response:**
```json
{
  "id": "shipment-uuid-1",
  "upload_session": "session-uuid",
  "csv_row_number": 3,
  "status": "valid",
  "status_display": "Valid",
  "validation_messages": [],
  "address_validation_provider": "usps",
  "customs_description": null,
  "customs_value": null,
  "reference_number": "ORD-1001",
  "addresses": [
    {
      "id": "address-uuid-1",
      "address_type": "ship_from",
      "address_type_display": "Ship From",
      "name": "John Smith",
      "company": "ACME Corporation",
      "street1": "123 Industrial Blvd",
      "street2": "Suite 100",
      "city": "Los Angeles",
      "state": "CA",
      "zip_code": "90001",
      "country": "US",
      "phone": "555-0100",
      "email": "warehouse@acme.com",
      "is_validated": true,
      "validation_status": "valid",
      "validation_status_display": "Valid",
      "validation_error": null,
      "validated_at": "2026-01-31T10:00:02.000000Z",
      "validated_by_provider": "usps"
    },
    {
      "id": "address-uuid-2",
      "address_type": "ship_to",
      ...
    }
  ],
  "package": {
    "id": "package-uuid-1",
    "length": "12.00",
    "width": "9.00",
    "height": "6.00",
    "weight": "8.50",
    "weight_unit": "oz",
    "weight_in_ounces": 9,
    "package_type": "box"
  },
  "shipping_service": {
    "id": "service-uuid-1",
    "service_type": "priority_mail",
    "service_type_display": "Priority Mail",
    "service_tier": "tier_2",
    "service_tier_display": "Tier 2 (4-8 oz)",
    "price": "5.75",
    "currency": "USD",
    "auto_selected": true
  },
  "can_edit": true
}
```

---

### Step 6: Edit Shipment Address

**Request:**
```bash
curl -X PUT http://localhost:8000/api/addresses/{address_id}/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Smith Jr",
    "street1": "456 New Address St",
    "city": "Los Angeles",
    "state": "CA",
    "zip_code": "90002"
  }'
```

**What Happens:**
1. Address is updated
2. Address is re-validated
3. Shipment status is updated based on validation result

---

### Step 7: Edit Package (Triggers Shipping Recalculation)

**Request:**
```bash
curl -X PATCH http://localhost:8000/api/packages/{package_id}/ \
  -H "Content-Type: application/json" \
  -d '{
    "weight": "15.5"
  }'
```

**What Happens:**
1. Package weight is updated
2. Shipping service is recalculated automatically
3. Price is updated based on new weight tier

---

### Step 8: Purchase Session

**Request:**
```bash
curl -X POST http://localhost:8000/api/sessions/{session_id}/purchase/ \
  -H "Content-Type: application/json" \
  -d '{
    "label_size": "4x6",
    "terms_accepted": true
  }'
```

**Expected Response:**
```json
{
  "message": "Purchase confirmed successfully",
  "session": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "purchased",
    "is_locked": true,
    "purchase_date": "2026-01-31T10:05:00.000000Z",
    "label_size": "4x6",
    "terms_accepted": true,
    "can_edit": false
  }
}
```

**What Happens:**
1. Session is validated (no errors, at least one shipment)
2. Session status changes to `purchased`
3. Session is locked (`is_locked` = true)
4. No further edits allowed

---

## 2. Bulk Operations

### Bulk Update Ship-From Address

**Request:**
```bash
curl -X POST http://localhost:8000/api/shipments/bulk_update_address/ \
  -H "Content-Type: application/json" \
  -d '{
    "shipment_ids": ["uuid1", "uuid2", "uuid3"],
    "saved_address_id": "saved-address-uuid"
  }'
```

**Expected Response:**
```json
{
  "message": "Updated 3 shipments",
  "updated_count": 3
}
```

---

### Bulk Update Package

**Request:**
```bash
curl -X POST http://localhost:8000/api/shipments/bulk_update_package/ \
  -H "Content-Type: application/json" \
  -d '{
    "shipment_ids": ["uuid1", "uuid2", "uuid3"],
    "saved_package_id": "saved-package-uuid"
  }'
```

---

### Bulk Update Shipping Service

**Request:**
```bash
curl -X POST http://localhost:8000/api/shipments/bulk_update_service/ \
  -H "Content-Type: application/json" \
  -d '{
    "shipment_ids": ["uuid1", "uuid2"],
    "service_type": "ground_shipping"
  }'
```

**Note:** This may fail for heavy packages (16+ oz) since ground shipping is not available.

---

### Bulk Delete Shipments

**Request:**
```bash
curl -X POST http://localhost:8000/api/shipments/bulk_delete/ \
  -H "Content-Type: application/json" \
  -d '{
    "shipment_ids": ["uuid1", "uuid2", "uuid3"]
  }'
```

---

## 3. Saved Addresses & Packages

### List Saved Addresses

**Request:**
```bash
curl http://localhost:8000/api/saved-addresses/
```

**Expected Response:**
```json
{
  "count": 4,
  "results": [
    {
      "id": "uuid",
      "nickname": "Main Warehouse",
      "name": "John Smith",
      "company": "ACME Corporation",
      "street1": "123 Industrial Blvd",
      "street2": "Suite 100",
      "city": "Los Angeles",
      "state": "CA",
      "zip_code": "90001",
      "country": "US",
      "phone": "555-0100",
      "email": "warehouse@acme.com",
      "is_default": true,
      "created_at": "2026-01-31T09:00:00.000000Z"
    },
    ...
  ]
}
```

---

### Create New Saved Address

**Request:**
```bash
curl -X POST http://localhost:8000/api/saved-addresses/ \
  -H "Content-Type: application/json" \
  -d '{
    "nickname": "Seattle Office",
    "name": "Jane Doe",
    "street1": "100 Pike St",
    "city": "Seattle",
    "state": "WA",
    "zip_code": "98101",
    "phone": "555-0200",
    "is_default": false
  }'
```

---

### List Saved Packages

**Request:**
```bash
curl http://localhost:8000/api/saved-packages/
```

---

### Create New Saved Package

**Request:**
```bash
curl -X POST http://localhost:8000/api/saved-packages/ \
  -H "Content-Type: application/json" \
  -d '{
    "nickname": "Custom Box",
    "length": 10,
    "width": 8,
    "height": 6,
    "weight": 5.5,
    "package_type": "box",
    "is_default": false
  }'
```

---

## 4. Error Cases to Test

### Attempt to Edit Locked Session

**Request:**
```bash
# After purchasing, try to update a shipment
curl -X PUT http://localhost:8000/api/shipments/{shipment_id}/ \
  -H "Content-Type: application/json" \
  -d '{"reference_number": "UPDATED"}'
```

**Expected Response:**
```json
{
  "error": "Cannot edit shipment in a locked session",
  "status_code": 403,
  "details": {
    "shipment": "This shipment belongs to a purchased session"
  }
}
```

---

### Purchase Session with Errors

**Request:**
```bash
# Try to purchase a session with error-status shipments
curl -X POST http://localhost:8000/api/sessions/{session_id}/purchase/ \
  -H "Content-Type: application/json" \
  -d '{
    "label_size": "4x6",
    "terms_accepted": true
  }'
```

**Expected Response:**
```json
{
  "error": "Cannot purchase session with 2 error(s)",
  "status_code": 400,
  "details": {
    "session": "All shipments must be valid or have warnings only"
  }
}
```

---

### Invalid Ground Shipping for Heavy Package

**Request:**
```bash
# Try to set ground shipping for a 20oz package
curl -X POST http://localhost:8000/api/shipments/bulk_update_service/ \
  -H "Content-Type: application/json" \
  -d '{
    "shipment_ids": ["heavy-package-uuid"],
    "service_type": "ground_shipping"
  }'
```

**Expected Response:**
```json
{
  "message": "Updated 0 shipments",
  "updated_count": 0,
  "errors": [
    {
      "shipment_id": "heavy-package-uuid",
      "error": "Ground shipping not available for packages 16+ oz (current weight: 20 oz)"
    }
  ]
}
```

---

### Missing Required CSV Fields

Upload a CSV with missing required fields to test error handling.

---

## 5. Using Postman/Insomnia

Import these requests into Postman or Insomnia:

1. Create a new collection
2. Set base URL: `http://localhost:8000/api`
3. Add all endpoints from above
4. Use environment variables for session_id, shipment_id, etc.

---

## 6. Using DRF Browsable API

1. Open browser: `http://localhost:8000/api/`
2. Navigate to any endpoint
3. Use the HTML forms to test GET/POST/PUT/DELETE
4. View formatted JSON responses

---

## 7. Validation Testing

### Test Address Validation Fallback

1. Configure primary provider to fail (invalid API key)
2. Configure fallback provider with valid credentials
3. Upload CSV
4. Check that addresses are marked as `fallback_valid`
5. Check logs to see fallback mechanism in action

### Test Weight-Based Tier Assignment

Upload CSV with various weights and verify pricing:

| Weight (oz) | Expected Tier | Priority Price | Ground Price |
|-------------|---------------|----------------|--------------|
| 2.5         | Tier 1        | $4.50          | $3.50        |
| 6.0         | Tier 2        | $5.75          | $4.25        |
| 10.5        | Tier 3        | $7.00          | $5.00        |
| 14.0        | Tier 4        | $8.25          | $5.75        |
| 18.0        | Tier 5        | $9.50          | N/A          |

---

## 8. Checking Logs

View structured logs during testing:

```bash
# Tail logs
tail -f logs/shipping_platform.log

# Pretty print JSON logs (requires jq)
tail -f logs/shipping_platform.log | jq .
```

**Look for:**
- CSV parsing events
- Address validation (primary/fallback)
- Shipping service calculations
- Purchase confirmations
- Error events

---

## Common Test Scenarios

### Scenario 1: Happy Path
1. Create session
2. Upload valid CSV
3. Review shipments (all valid)
4. Purchase session
5. Verify session locked

### Scenario 2: Edit and Retry
1. Create session
2. Upload CSV with some invalid addresses
3. Edit invalid shipments
4. Verify re-validation
5. Purchase when all valid

### Scenario 3: Bulk Operations
1. Create session
2. Upload CSV
3. Bulk update all ship-from addresses
4. Bulk change package type
5. Bulk switch to ground shipping (where applicable)
6. Purchase

### Scenario 4: Error Handling
1. Upload invalid CSV format
2. Try to purchase empty session
3. Try to edit after purchase
4. Try invalid shipping service

---

**Happy Testing! 🧪✅**
