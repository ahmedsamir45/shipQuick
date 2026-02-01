# Product Requirements Document (PRD)
## Bulk Shipping Label Creation Platform

---

## Document Information
| Field | Value |
|-------|-------|
| Test Type | Technical Assessment |
| Duration | As specified by hiring manager |
| Deliverables | Functional web application with live deployment |

---

## 1. Introduction

### 1.1 Background

E-commerce businesses need efficient ways to create shipping labels for multiple orders simultaneously. Manually creating labels one-by-one is time-consuming and error-prone. A bulk shipping label creation system allows merchants to upload their order data via spreadsheet and generate labels for all orders in a streamlined workflow.

### 1.2 Your Task

Build a **Bulk Shipping Label Creation Platform** that enables users to:
1. Upload a spreadsheet containing shipping order data
2. Review, edit, and manage the imported records
3. Select shipping providers for each shipment
4. Purchase and generate shipping labels in bulk

The application should be a web-based platform with a clean, professional user interface.

### 1.3 What We're Evaluating

- **Creative Design & User Flow**: UI/UX decisions, visual hierarchy, user experience, and the best possible user flow — design that feels natural and effortless
- **Technical Implementation**: Code quality, architecture, best practices
- **Problem Solving**: How you handle edge cases and data issues
- **Attention to Detail**: Form handling, state management, error scenarios

---

## 2. Product Overview

### 2.1 Core Concept

A 4-step wizard that guides users through the bulk shipping label creation process:

```
[Step 1: Upload] → [Step 2: Review & Edit] → [Step 3: Select Shipping] → [Step 4: Purchase]
```

### 2.2 Target Users

- E-commerce store owners
- Fulfillment center operators
- Small business merchants
- Anyone who needs to ship multiple packages regularly

### 2.3 Key Value Proposition

- Save time by processing hundreds of shipments at once
- Reduce errors through data review and editing capabilities
- Compare shipping rates across providers
- Maintain consistency with saved addresses and package presets

---

## 3. Application Structure

### 3.1 Navigation Sidebar

The application should have a persistent left sidebar with the following menu items:

| Menu Item | Purpose |
|-----------|---------|
| Dashboard | Main overview page |
| Create a Label | Single label creation (not in scope) |
| **Upload Spreadsheet** | Bulk upload feature (this PRD) |
| Order History | View past orders (not in scope) |
| Pricing | View pricing information (not in scope) |
| Billing | Billing management (not in scope) |
| Settings | Account settings (not in scope) |
| Support & Help | Help resources (not in scope) |

**Note**: All sidebar menu items should be visible for a realistic application feel. Only the "Upload Spreadsheet" flow needs to be fully implemented. Non-implemented items should appear as disabled/grayed out.

### 3.2 Header Area

- Application logo/name
- User information display (name, account balance)
- System notification banner capability

### 3.3 User Context

Display a logged-in user context with:
- User name
- Account balance (simulated)

---

## 4. Feature Requirements

### 4.1 STEP 1: Upload Spreadsheet

**Page Title**: "Upload Spreadsheet (Step 1 of 4)"

#### 4.1.1 File Upload Component

Create a file upload area that supports:
- Drag and drop functionality
- Click to browse files
- Visual feedback during upload
- Loading state while processing

#### 4.1.2 Address Validation on Upload

After CSV parsing:
- All addresses (Ship From and Ship To) must be validated through the address validation API
- Rows with invalid addresses should be flagged with a warning indicator
- Invalid addresses should **not** block the user from proceeding
- Display a summary of validation results (e.g., "85 of 100 addresses validated, 15 flagged for review")

#### 4.1.3 Help Section

Provide a sidebar or section with:
- Link to download the template file (Template.csv provided)
- Brief instructions on how the upload process works

#### 4.1.4 Supported File Format

The system must parse CSV files with the following structure:

**Template.csv Header Structure:**
```
Row 1: From,,,,,,,To,,,,,,,weight*,weight*,Dimensions*,Dimensions*,Dimensions*,,,,
Row 2: First name*,Last name,Address*,Address2,City*,ZIP/Postal code*,Abbreviation*,First name*,Last name,Address*,Address2,City*,ZIP/Postal code*,Abbreviation*,lbs,oz,Length,width,Height,phone num1,phone num2,order no,Item-sku
Row 3+: [Data rows]
```

**Column Mapping:**

| Column Index | Field Name | Category |
|--------------|------------|----------|
| 0 | First name (From) | Ship From |
| 1 | Last name (From) | Ship From |
| 2 | Address (From) | Ship From |
| 3 | Address2 (From) | Ship From |
| 4 | City (From) | Ship From |
| 5 | ZIP/Postal code (From) | Ship From |
| 6 | Abbreviation/State (From) | Ship From |
| 7 | First name (To) | Ship To |
| 8 | Last name (To) | Ship To |
| 9 | Address (To) | Ship To |
| 10 | Address2 (To) | Ship To |
| 11 | City (To) | Ship To |
| 12 | ZIP/Postal code (To) | Ship To |
| 13 | Abbreviation/State (To) | Ship To |
| 14 | Weight (lbs) | Package |
| 15 | Weight (oz) | Package |
| 16 | Length | Package |
| 17 | Width | Package |
| 18 | Height | Package |
| 19 | Phone num1 | Contact |
| 20 | Phone num2 | Contact |
| 21 | Order no | Reference |
| 22 | Item-sku | Reference |

**Note**: Fields marked with `*` in the template indicate importance. The candidate should determine which fields are required and implement appropriate handling.

---

### 4.2 STEP 2: Review and Edit File

**Page Title**: "Review and Edit File (Step 2 of 4)"

#### 4.2.1 Data Table

Display all imported records in a data table with the following columns:

| Column | Content |
|--------|---------|
| Selection | Checkbox for bulk selection |
| Ship From Address | Formatted sender address |
| Ship To Address | Formatted recipient address |
| Package Details | Dimensions and weight |
| Order No | Order reference |
| Status | Record status indicator (valid, warning, error) |
| Action | Edit and delete buttons |

#### 4.2.2 Address Re-Validation on Edit

When any address is edited in this step:
- Re-validate the changed address through the address validation API
- Update the row's status indicator accordingly

#### 4.2.3 Individual Row Actions

For each row, provide:
- **Edit**: Opens a modal to edit address or package details
- **Delete**: Removes the row (with confirmation)

#### 4.2.4 Edit Address Modal

When editing an address, display a modal form with fields:
- First Name
- Last Name
- Address Line 1
- Address Line 2
- City
- State (dropdown with US states)
- Zip Code
- Phone

#### 4.2.5 Edit Package Details Modal

When editing package details, display a modal form with fields:
- Item ID / SKU
- Length (inches)
- Width (inches)
- Height (inches)
- Weight (lbs)
- Weight (oz)

#### 4.2.6 Bulk Actions

When one or more rows are selected, show bulk action buttons:
- **Change Ship From Address for Selected**: Apply a saved address to all selected rows
- **Change Package Details for Selected**: Apply a saved package preset to all selected rows
- **Delete Selected**: Delete all selected rows

#### 4.2.7 Saved Addresses Feature

Implement a "Saved Addresses" system where users can:
- Store frequently used ship-from addresses
- Select from saved addresses when bulk-editing
- Display addresses in a dropdown/list format

**Sample Saved Addresses** (pre-populate for demo):
```
Address 1:
  Name: Print TTS
  Address: 502 W Arrow Hwy, STE P
  City: San Dimas
  State: CA
  ZIP: 91773

Address 2:
  Name: Print TTS
  Address: 500 W Foothill Blvd, STE P
  City: Claremont
  State: CA
  ZIP: 91711

Address 3:
  Name: Print TTS
  Address: 1170 Grove Ave
  City: Ontario
  State: CA
  ZIP: 91764
```

#### 4.2.8 Saved Packages Feature

Implement a "Saved Packages" system where users can:
- Store frequently used package dimensions/weights
- Select from saved packages when bulk-editing

**Sample Saved Packages** (pre-populate for demo):
```
Package 1:
  Name: Light Package
  Dimensions: 6x6x6 inches
  Weight: 1 lb 0 oz

Package 2:
  Name: 8 Oz Item
  Dimensions: 4x4x4 inches
  Weight: 0 lb 8 oz

Package 3:
  Name: Standard Box
  Dimensions: 12x12x12 inches
  Weight: 2 lb 0 oz
```

#### 4.2.9 Search Functionality

Provide a search input that filters the table based on:
- Address text
- Order number
- Recipient name

#### 4.2.10 Navigation

- **Back Button**: Returns to Step 1 (should warn about data loss)
- **Continue Button**: Proceeds to Step 3

---

### 4.3 STEP 3: Select Shipping Provider

**Page Title**: "Select Shipping Provider (Step 3 of 4)"

#### 4.3.1 Data Table

Display records with an additional column for shipping service selection:

| Column | Content |
|--------|---------|
| Selection | Checkbox for bulk selection |
| Ship From Address | Formatted sender address |
| Ship To Address | Formatted recipient address |
| Package Details | Dimensions and weight |
| Order No | Order reference |
| Shipping Services | Service selector with price |
| Action | Delete button |

**Note**: Addresses and package details are **not editable** in this step. Only shipping service selection and row deletion are allowed.

#### 4.3.2 Shipping Service Options

For each shipment, provide two shipping options with **weight-tier-based pricing**:

**Priority Mail:**

| Weight Tier | Price |
|-------------|-------|
| 0 - 8 oz | $4.00 |
| 9 - 16 oz | $5.00 |
| 17 - 32 oz (up to 2 lbs) | $6.00 |
| 33+ oz (over 2 lbs) | $8.00 |

**Ground Shipping** (available for shipments under 1 lb only):

| Weight Tier | Price |
|-------------|-------|
| 0 - 8 oz | $2.00 |
| 9 - 16 oz | $3.00 |

**Pricing Rules:**
- Any fractional ounce rounds **up** to the next tier
- Ground Shipping is only available for packages weighing **strictly under 16 oz** (under 1 lb). A package weighing exactly 16 oz or more must use Priority Mail.
- If a package has no weight data, default to Priority Mail at the lowest tier until the user provides weight information

#### 4.3.3 Total Price Display

Show a running total in the header area that updates as:
- Shipping services are changed
- Rows are added or removed

Format: "Total: $XXX.XX"

#### 4.3.4 Bulk Service Change

When rows are selected, provide a bulk action to change shipping service:
- **Change Shipping Services for Selected**: Opens a modal/dropdown with options:
  - "Switch to the most affordable rate available"
  - "Change to Priority Mail"
  - "Change to Ground Shipping" (only applied to eligible rows under 1 lb)

#### 4.3.5 Delete Functionality

Allow deletion of rows with confirmation dialog.

#### 4.3.6 Navigation

- **Back Button**: Returns to Step 2
- **Continue Button**: Proceeds to Step 4 (Purchase)

---

### 4.4 STEP 4: Purchase/Checkout

**Page Title**: "Purchase Labels (Step 4 of 4)"

**Note**: This is a confirmation-only step. No editing of addresses, packages, or shipping services is allowed here.

#### 4.4.1 Label Size Selection

Before final purchase, prompt user to select label format:

| Option | Description |
|--------|-------------|
| Letter/A4 | Standard paper size (8.5x11 or A4) |
| 4x6 inch | Thermal label format |

#### 4.4.2 Final Confirmation

Display:
- Grand total amount
- Terms acceptance checkbox
- Purchase/Confirm button

#### 4.4.3 Success State

After purchase, show a success confirmation with:
- Success message
- Summary of labels created
- Option to download/print (can be simulated)

---

## 5. User Interface Specifications

### 5.1 Layout Structure

```
+----------------------------------------------------------------+
|  HEADER (Logo, User Info, Notifications)                        |
+---------------+------------------------------------------------+
|               |                                                 |
|   SIDEBAR     |              MAIN CONTENT AREA                  |
|               |                                                 |
|  - Dashboard  |   +------------------------------------------+  |
|  - Create     |   |  Step Title              [Back] [Continue]|  |
|  - Upload*    |   +------------------------------------------+  |
|  - History    |   |                                          |  |
|  - Pricing    |   |           Step Content                   |  |
|  - Billing    |   |                                          |  |
|  - Settings   |   |                                          |  |
|  - Support    |   |                                          |  |
|               |   +------------------------------------------+  |
+---------------+------------------------------------------------+
```

### 5.2 Color Guidance

Use a professional color scheme. Suggested approach:
- **Primary Action**: Blue tones
- **Danger/Delete**: Red tones
- **Success**: Green tones
- **Warnings/Alerts**: Yellow/Orange tones
- **Backgrounds**: Light grays/whites
- **Active States**: Highlighted backgrounds

### 5.3 Table Design

- Sortable column headers (optional but appreciated)
- Alternating row backgrounds for readability
- Clear visual distinction for selected rows
- Status indicators that are immediately recognizable

### 5.4 Modal Dialogs

- Centered on screen with backdrop overlay
- Clear title and purpose
- Cancel and confirm actions
- Form inputs with labels

### 5.5 Responsive Considerations

While not required, consideration for different screen sizes is appreciated.

---

## 6. Data Flow

### 6.1 State Management

The application should maintain state for:
- Current step in the wizard
- Uploaded/imported shipment records
- Selected rows for bulk actions
- Selected shipping services
- Saved addresses and packages
- Running total calculation

### 6.2 Data Persistence

Data must be persisted through the backend. Use MongoDB, PostgreSQL, or SQLite as the database. The server side (API routes, Express, or Django) handles all validation and business logic.

### 6.3 Sample Data Flow

```
1. User uploads Template.csv
   |
2. Backend parses CSV and creates shipment records
   |
3. Backend validates all addresses via address validation API
   |
4. Records displayed in table (Step 2) with validation status indicators
   |
5. User reviews, edits, fixes any issues
   |
6. Edited addresses re-validated via API
   |
7. User continues to Step 3
   |
8. System assigns default shipping service based on weight tiers
   |
9. User adjusts shipping selections
   |
10. Total price calculated
    |
11. User proceeds to Step 4 (Purchase)
    |
12. User selects label size, accepts terms, confirms purchase
    |
13. Success confirmation displayed
```

---

## 7. Provided Resources

### 7.1 Template File

A `Template.csv` file is provided with:
- Proper header structure (2 header rows)
- 100 sample shipment records
- Mix of complete and incomplete data
- Various US addresses

### 7.2 Sample Data Characteristics

The provided template contains:
- Records with only "Ship To" addresses (Ship From is empty)
- Some records missing weight/dimension data
- Various US states represented
- Apartment/unit numbers in Address2 field

---

## 8. Confirmation Dialogs

### 8.1 Delete Confirmation

When deleting records, show a confirmation dialog:
- Warning message asking for confirmation
- Confirm button (destructive action styling)
- Cancel button

### 8.2 Navigation Warning

When going back from Step 2 to Step 1:
- Warn that current data will be lost
- Confirm button to proceed
- Cancel button to stay

### 8.3 Success Feedback

After successful operations, show brief success feedback:
- Delete confirmation
- Save confirmation
- Purchase completion

---

## 9. Technical Specifications

### 9.1 Required Stack

Choose one of the following stack options:

**Option A: Next.js (Recommended)**

| Layer | Technology |
|-------|------------|
| **Framework** | Next.js (App Router or Pages Router) |
| **Frontend** | React + TypeScript |
| **Backend** | Next.js API routes or separate Express.js server |
| **Database** | MongoDB, PostgreSQL, or SQLite |
| **API Style** | REST |

**Option B: Django + React**

| Layer | Technology |
|-------|------------|
| **Backend** | Django with Django REST Framework (DRF) |
| **Frontend** | React + TypeScript |
| **Database** | MongoDB, PostgreSQL, or SQLite |
| **API Style** | REST |

All validation and business logic must be implemented on the server side.

### 9.2 Code Quality Expectations

- Clean, readable code
- Appropriate component structure
- Meaningful variable/function names
- Proper error handling
- Structured logging throughout

### 9.3 Not Required

- User authentication
- Actual shipping API integration (shipping services are simulated)
- Unit tests (but appreciated if included)

---

## 10. Deliverables

### 10.1 Required

1. Working web application implementing the described features
2. **Live demo URL** - hosted and accessible for at least 2 weeks
3. Source code (GitHub repository or zip file)
4. README with setup instructions, assumptions made, and architectural decisions

### 10.2 Optional (Bonus Points)

- Unit or integration tests
- Performance optimizations
- Accessibility considerations
- Address auto-correction via validation API
- Additional features you think would be valuable

---

## 11. Evaluation Criteria

Your submission will be evaluated on:

| Criteria | Weight |
|----------|--------|
| UI/UX Design & User Flow | Highest - visual appeal, polish, user experience, and best possible user flow |
| Logging | High - structured, meaningful logging across all flows |
| Functionality | Core features work as expected |
| Code Quality | Clean, maintainable, well-structured |
| Problem Solving | How you handle edge cases and data issues |
| Attention to Detail | Polish and completeness |

---

## 12. User Flow Summary

```
+----------------------------------------------------------------------------+
|                         BULK SHIPPING WIZARD                                |
+----------------------------------------------------------------------------+

 STEP 1                    STEP 2                      STEP 3
+-------------+          +-----------------+         +-----------------+
|   UPLOAD    |          |  REVIEW & EDIT  |         | SELECT SHIPPING |
|             |          |                 |         |                 |
| +---------+ |          | +-------------+ |         | +-------------+ |
| |  Drop   | |   --->   | | Data Table  | |  --->   | | Data Table  | |
| |  File   | |          | | + Edit/Del  | |         | | + Services  | |
| |  Here   | |          | | + Bulk Acts | |         | | + Pricing   | |
| +---------+ |          | +-------------+ |         | +-------------+ |
|             |          |                 |         |                 |
| + Validate  |          | [Back][Continue]|         | Total: $XXX     |
| [Template]  |          +-----------------+         | [Back][Continue]|
+-------------+                                      +--------+--------+
                                                              |
                                                              v
                                                     +-----------------+
                                                     |    PURCHASE     |
                                                     |   (Step 4)      |
                                                     |                 |
                                                     | * Label Size    |
                                                     | * Grand Total   |
                                                     | * Terms Accept  |
                                                     | * Confirm       |
                                                     |                 |
                                                     |   [Purchase]    |
                                                     +--------+--------+
                                                              |
                                                              v
                                                     +-----------------+
                                                     |    SUCCESS!     |
                                                     |                 |
                                                     |  Labels Created |
                                                     +-----------------+
```

---

## Appendix A: Template.csv Structure Reference

### Header Rows
```csv
From,,,,,,,To,,,,,,,weight*,weight*,Dimensions*,Dimensions*,Dimensions*,,,,
First name*,Last name,Address*,Address2,City*,ZIP/Postal code*,Abbreviation*,First name*,Last name,Address*,Address2,City*,ZIP/Postal code*,Abbreviation*,lbs,oz,Length,width,Height,phone num1,phone num2,order no,Item-sku
```

### Sample Data Row
```csv
,,,,,,,Salina Dixon,,61 Sunny Trail Rd,Apt 10885,Wallace,28466-9087,NC,,,,,,,,,
```

### Column Count
Total columns: 23 (indices 0-22)

---

## Appendix B: US State Abbreviations

For the State dropdown in address forms, use standard 2-letter US state abbreviations:

AL, AK, AZ, AR, CA, CO, CT, DE, FL, GA, HI, ID, IL, IN, IA, KS, KY, LA, ME, MD, MA, MI, MN, MS, MO, MT, NE, NV, NH, NJ, NM, NY, NC, ND, OH, OK, OR, PA, RI, SC, SD, TN, TX, UT, VT, VA, WA, WV, WI, WY

Also include territories: PR (Puerto Rico), DC (District of Columbia)

---

## Appendix C: Shipping Service Pricing (Weight Tiers)

### Priority Mail

| Weight Tier | Price |
|-------------|-------|
| 0 - 8 oz | $4.00 |
| 9 - 16 oz | $5.00 |
| 17 - 32 oz (up to 2 lbs) | $6.00 |
| 33+ oz (over 2 lbs) | $8.00 |

### Ground Shipping (under 1 lb only)

| Weight Tier | Price |
|-------------|-------|
| 0 - 8 oz | $2.00 |
| 9 - 16 oz | $3.00 |

**Rules:**
- Any weight that exceeds a tier boundary rounds **up** to the next tier
- Ground Shipping is **only available** for packages weighing **strictly under 16 oz** (under 1 lb). A package weighing exactly 16 oz or more must use Priority Mail.
- If weight data is missing, default to Priority Mail at the lowest tier ($4.00) until the user provides weight

---

**Good luck! We look forward to seeing your implementation.**
