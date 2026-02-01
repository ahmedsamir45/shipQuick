# Database Design - Bulk Shipping Label Platform

## Entity Relationship Overview

```
UploadSession (1) ----< (N) Shipment
Shipment (1) ----< (N) Address [Ship From/Ship To polymorphic]
Shipment (1) ---- (1) Package
Shipment (1) ---- (1) ShippingServiceSelection

SavedAddress (independent reference table)
SavedPackage (independent reference table)
```

## Models

### 1. UploadSession
Represents one CSV upload workflow from upload to purchase.

**Fields:**
- `id` (PK, UUID)
- `created_at` (DateTime)
- `updated_at` (DateTime)
- `status` (CharField) - `draft`, `in_review`, `purchased`
- `total_shipments` (Integer)
- `valid_shipments` (Integer)
- `warning_shipments` (Integer)
- `error_shipments` (Integer)
- `is_locked` (Boolean) - True after purchase
- `purchase_date` (DateTime, nullable)
- `label_size` (CharField) - `letter`, `4x6` (set at purchase)
- `terms_accepted` (Boolean)

**Business Rules:**
- Cannot edit shipments if `is_locked=True`
- Status transitions: draft → in_review → purchased

---

### 2. Shipment
Individual shipment record from CSV or manual creation.

**Fields:**
- `id` (PK, UUID)
- `upload_session` (FK → UploadSession)
- `csv_row_number` (Integer, nullable) - Original row in CSV
- `created_at` (DateTime)
- `updated_at` (DateTime)
- `status` (CharField) - `valid`, `warning`, `error`
- `validation_messages` (JSONField) - Array of validation issues
- `address_validation_provider` (CharField) - Which API validated addresses
- `customs_description` (TextField, nullable)
- `customs_value` (DecimalField, nullable)
- `reference_number` (CharField, nullable)

**Business Rules:**
- Must have exactly 1 ship_from and 1 ship_to address
- Must have exactly 1 package
- Status determined by address validation results
- Cannot be edited if session is locked

---

### 3. Address
Polymorphic model for Ship From and Ship To addresses.

**Fields:**
- `id` (PK, UUID)
- `shipment` (FK → Shipment)
- `address_type` (CharField) - `ship_from`, `ship_to`
- `name` (CharField)
- `company` (CharField, nullable)
- `street1` (CharField)
- `street2` (CharField, nullable)
- `city` (CharField)
- `state` (CharField) - 2-letter code
- `zip_code` (CharField)
- `country` (CharField) - Default 'US'
- `phone` (CharField, nullable)
- `email` (EmailField, nullable)
- `is_validated` (Boolean)
- `validation_status` (CharField) - `pending`, `valid`, `invalid`, `fallback_valid`
- `validation_error` (TextField, nullable)
- `validated_at` (DateTime, nullable)
- `validated_by_provider` (CharField, nullable) - `usps`, `google`, `smarty`, `lob`
- `original_input` (JSONField) - Store original before normalization
- `normalized_address` (JSONField, nullable) - API-returned normalized version

**Business Rules:**
- Re-validate on every edit
- Store validation metadata for debugging
- Must have at least name, street1, city, state, zip

---

### 4. Package
Package dimensions and weight.

**Fields:**
- `id` (PK, UUID)
- `shipment` (OneToOne → Shipment)
- `length` (DecimalField) - inches
- `width` (DecimalField) - inches
- `height` (DecimalField) - inches
- `weight` (DecimalField) - ounces (oz)
- `weight_unit` (CharField) - Default 'oz'
- `package_type` (CharField) - `box`, `envelope`, `pak`, `tube`

**Business Rules:**
- Weight required for shipping service selection
- Fractional weights round up
- All dimensions must be > 0

---

### 5. ShippingServiceSelection
Shipping service and pricing for a shipment.

**Fields:**
- `id` (PK, UUID)
- `shipment` (OneToOne → Shipment)
- `service_type` (CharField) - `priority_mail`, `ground_shipping`
- `service_tier` (CharField) - `tier_1`, `tier_2`, `tier_3`, `tier_4`, `tier_5`
- `price` (DecimalField)
- `currency` (CharField) - Default 'USD'
- `auto_selected` (Boolean) - True if auto-assigned by weight
- `created_at` (DateTime)
- `updated_at` (DateTime)

**Business Rules:**
- Auto-assign based on weight:
  - < 4 oz → Priority Mail Tier 1
  - 4-8 oz → Priority Mail Tier 2
  - 8-12 oz → Priority Mail Tier 3
  - 12-16 oz → Priority Mail Tier 4 OR Ground (user can choose)
  - > 16 oz → Priority Mail Tier 5 only
- Ground shipping only available if weight < 16 oz
- Missing weight → default to Priority Mail Tier 1

**Pricing Table:**
| Service | Weight Range | Price |
|---------|--------------|-------|
| Priority Mail Tier 1 | 0-4 oz | $4.50 |
| Priority Mail Tier 2 | 4-8 oz | $5.75 |
| Priority Mail Tier 3 | 8-12 oz | $7.00 |
| Priority Mail Tier 4 | 12-16 oz | $8.25 |
| Priority Mail Tier 5 | 16+ oz | $9.50 |
| Ground Tier 1 | 0-4 oz | $3.50 |
| Ground Tier 2 | 4-8 oz | $4.25 |
| Ground Tier 3 | 8-12 oz | $5.00 |
| Ground Tier 4 | 12-16 oz | $5.75 |

---

### 6. SavedAddress
Reusable ship-from addresses.

**Fields:**
- `id` (PK, UUID)
- `nickname` (CharField) - e.g., "Main Warehouse"
- `name` (CharField)
- `company` (CharField, nullable)
- `street1` (CharField)
- `street2` (CharField, nullable)
- `city` (CharField)
- `state` (CharField)
- `zip_code` (CharField)
- `country` (CharField)
- `phone` (CharField, nullable)
- `email` (EmailField, nullable)
- `is_default` (Boolean)
- `created_at` (DateTime)

**Business Rules:**
- Used for bulk "apply saved address" operations
- Only one default address allowed
- Pre-populate with demo data

---

### 7. SavedPackage
Reusable package presets.

**Fields:**
- `id` (PK, UUID)
- `nickname` (CharField) - e.g., "Small Box"
- `length` (DecimalField)
- `width` (DecimalField)
- `height` (DecimalField)
- `weight` (DecimalField)
- `package_type` (CharField)
- `is_default` (Boolean)
- `created_at` (DateTime)

**Business Rules:**
- Used for bulk "apply saved package" operations
- Only one default package allowed
- Pre-populate with demo data

---

## Indexes & Performance

**Recommended Indexes:**
- `UploadSession.status`
- `Shipment.upload_session + status`
- `Shipment.csv_row_number`
- `Address.shipment + address_type`
- `Address.validation_status`

---

## Status Flow

```
CSV Upload → Shipments created (status: pending)
    ↓
Address Validation → status: valid | warning | error
    ↓
User Edits → Re-validate → Update status
    ↓
Shipping Service Selection → Calculate price
    ↓
Purchase Confirmation → Lock session
```

---

## Validation Rules (Required Fields)

**Ship From/To Address:**
- name (required)
- street1 (required)
- city (required)
- state (required)
- zip_code (required)

**Package:**
- weight (required)
- length, width, height (required)

**Customs (if international - future):**
- customs_description (required if country != 'US')
- customs_value (required if country != 'US')

---

## Assumptions

1. **No authentication**: All endpoints are public
2. **Single currency**: USD only
3. **Domestic only**: US addresses (international = future enhancement)
4. **SQLite**: Development/demo database
5. **Validation providers**: Primary = USPS, Fallback = Google/Smarty
6. **Weight unit**: Ounces (oz) internally
7. **Dimension unit**: Inches internally
