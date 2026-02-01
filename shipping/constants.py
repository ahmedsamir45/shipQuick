"""
Constants and choices for the shipping application.
Centralized location for all hardcoded values and business rules.
"""

# ===== Upload Session Status =====
class UploadSessionStatus:
    DRAFT = 'draft'
    IN_REVIEW = 'in_review'
    PURCHASED = 'purchased'

    CHOICES = [
        (DRAFT, 'Draft'),
        (IN_REVIEW, 'In Review'),
        (PURCHASED, 'Purchased'),
    ]


# ===== Shipment Status =====
class ShipmentStatus:
    VALID = 'valid'
    WARNING = 'warning'
    ERROR = 'error'

    CHOICES = [
        (VALID, 'Valid'),
        (WARNING, 'Warning'),
        (ERROR, 'Error'),
    ]


# ===== Address Type =====
class AddressType:
    SHIP_FROM = 'ship_from'
    SHIP_TO = 'ship_to'

    CHOICES = [
        (SHIP_FROM, 'Ship From'),
        (SHIP_TO, 'Ship To'),
    ]


# ===== Address Validation Status =====
class ValidationStatus:
    PENDING = 'pending'
    VALID = 'valid'
    INVALID = 'invalid'
    FALLBACK_VALID = 'fallback_valid'

    CHOICES = [
        (PENDING, 'Pending'),
        (VALID, 'Valid'),
        (INVALID, 'Invalid'),
        (FALLBACK_VALID, 'Fallback Valid'),
    ]


# ===== Address Validation Providers =====
class ValidationProvider:
    USPS = 'usps'
    GOOGLE = 'google'
    SMARTY = 'smarty'
    LOB = 'lob'

    CHOICES = [
        (USPS, 'USPS'),
        (GOOGLE, 'Google Maps'),
        (SMARTY, 'Smarty Streets'),
        (LOB, 'Lob'),
    ]


# ===== Package Type =====
class PackageType:
    BOX = 'box'
    ENVELOPE = 'envelope'
    PAK = 'pak'
    TUBE = 'tube'

    CHOICES = [
        (BOX, 'Box'),
        (ENVELOPE, 'Envelope'),
        (PAK, 'Pak'),
        (TUBE, 'Tube'),
    ]


# ===== Shipping Service Type =====
class ServiceType:
    PRIORITY_MAIL = 'priority_mail'
    GROUND_SHIPPING = 'ground_shipping'

    CHOICES = [
        (PRIORITY_MAIL, 'Priority Mail'),
        (GROUND_SHIPPING, 'Ground Shipping'),
    ]


# ===== Shipping Service Tier =====
# PRD Appendix C: Priority Mail 0-8oz, 9-16oz, 17-32oz, 33+oz | Ground 0-8oz, 9-16oz
class ServiceTier:
    TIER_1 = 'tier_1'   # 0-8 oz
    TIER_2 = 'tier_2'   # 9-16 oz
    TIER_3 = 'tier_3'   # 17-32 oz (Priority only)
    TIER_4 = 'tier_4'   # 33+ oz (Priority only)
    TIER_5 = 'tier_5'   # Legacy/backwards compat - maps to tier_4 for 16+ oz

    CHOICES = [
        (TIER_1, 'Tier 1 (0-8 oz)'),
        (TIER_2, 'Tier 2 (9-16 oz)'),
        (TIER_3, 'Tier 3 (17-32 oz)'),
        (TIER_4, 'Tier 4 (33+ oz)'),
        (TIER_5, 'Tier 5 (16+ oz)'),  # Legacy
    ]


# ===== Label Size =====
class LabelSize:
    LETTER = 'letter'
    LABEL_4X6 = '4x6'

    CHOICES = [
        (LETTER, 'Letter / A4'),
        (LABEL_4X6, '4x6 Label'),
    ]


# ===== Weight Unit =====
class WeightUnit:
    OZ = 'oz'
    LB = 'lb'
    G = 'g'
    KG = 'kg'

    CHOICES = [
        (OZ, 'Ounces'),
        (LB, 'Pounds'),
        (G, 'Grams'),
        (KG, 'Kilograms'),
    ]


# ===== Currency =====
class Currency:
    USD = 'USD'

    CHOICES = [
        (USD, 'US Dollar'),
    ]


# ===== Shipping Rate Pricing =====
# PRD Appendix C - Weight-tier-based pricing
# Priority Mail: 0-8oz=$4, 9-16oz=$5, 17-32oz=$6, 33+oz=$8
# Ground (under 16oz only): 0-8oz=$2, 9-16oz=$3
PRICING_TABLE = {
    ServiceType.PRIORITY_MAIL: {
        ServiceTier.TIER_1: {'weight_min': 0, 'weight_max': 8, 'price': 4.00},
        ServiceTier.TIER_2: {'weight_min': 9, 'weight_max': 16, 'price': 5.00},
        ServiceTier.TIER_3: {'weight_min': 17, 'weight_max': 32, 'price': 6.00},
        ServiceTier.TIER_4: {'weight_min': 33, 'weight_max': float('inf'), 'price': 8.00},
        ServiceTier.TIER_5: {'weight_min': 16, 'weight_max': float('inf'), 'price': 8.00},  # Legacy
    },
    ServiceType.GROUND_SHIPPING: {
        ServiceTier.TIER_1: {'weight_min': 0, 'weight_max': 8, 'price': 2.00},
        ServiceTier.TIER_2: {'weight_min': 9, 'weight_max': 16, 'price': 3.00},
        # Ground shipping not available for 16+ oz
    },
}

# Business Rules
GROUND_SHIPPING_MAX_WEIGHT_OZ = 16  # Ground shipping only for weight strictly under 16 oz
DEFAULT_SERVICE_TYPE = ServiceType.PRIORITY_MAIL
DEFAULT_SERVICE_TIER = ServiceTier.TIER_1

# Validation Rules
REQUIRED_ADDRESS_FIELDS = ['name', 'street1', 'city', 'state', 'zip_code']
REQUIRED_PACKAGE_FIELDS = ['weight', 'length', 'width', 'height']

# CSV Template
CSV_HEADER_ROWS = 2  # Number of header rows in CSV template
CSV_EXPECTED_COLUMNS = 23  # Expected number of columns

# Default country
DEFAULT_COUNTRY = 'US'
