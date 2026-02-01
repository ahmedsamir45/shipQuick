"""
Database models for the bulk shipping label platform.
All models follow production-ready patterns with proper validation and indexing.
"""
import uuid
from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from .constants import (
    UploadSessionStatus, ShipmentStatus, AddressType, ValidationStatus,
    ValidationProvider, PackageType, ServiceType, ServiceTier,
    LabelSize, WeightUnit, Currency, DEFAULT_COUNTRY
)


class BaseModel(models.Model):
    """
    Abstract base model with common fields for all models.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UploadSession(BaseModel):
    """
    Represents one CSV upload workflow from upload to purchase.
    Acts as a container for a batch of shipments.
    """
    status = models.CharField(
        max_length=20,
        choices=UploadSessionStatus.CHOICES,
        default=UploadSessionStatus.DRAFT,
        db_index=True,
        help_text="Current status of the upload session"
    )
    total_shipments = models.IntegerField(
        default=0,
        help_text="Total number of shipments in this session"
    )
    valid_shipments = models.IntegerField(
        default=0,
        help_text="Number of shipments with valid status"
    )
    warning_shipments = models.IntegerField(
        default=0,
        help_text="Number of shipments with warning status"
    )
    error_shipments = models.IntegerField(
        default=0,
        help_text="Number of shipments with error status"
    )
    is_locked = models.BooleanField(
        default=False,
        db_index=True,
        help_text="True after purchase - prevents further edits"
    )
    purchase_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when session was purchased"
    )
    label_size = models.CharField(
        max_length=10,
        choices=LabelSize.CHOICES,
        null=True,
        blank=True,
        help_text="Label size selected at purchase"
    )
    terms_accepted = models.BooleanField(
        default=False,
        help_text="User acceptance of terms and conditions"
    )

    class Meta:
        db_table = 'upload_sessions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'is_locked']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"UploadSession {self.id} - {self.status} ({self.total_shipments} shipments)"

    def update_counts(self):
        """
        Recalculate shipment counts based on current shipments.
        Called after shipment status changes.
        """
        from django.db.models import Count, Q

        counts = self.shipments.aggregate(
            total=Count('id'),
            valid=Count('id', filter=Q(status=ShipmentStatus.VALID)),
            warning=Count('id', filter=Q(status=ShipmentStatus.WARNING)),
            error=Count('id', filter=Q(status=ShipmentStatus.ERROR))
        )

        self.total_shipments = counts['total'] or 0
        self.valid_shipments = counts['valid'] or 0
        self.warning_shipments = counts['warning'] or 0
        self.error_shipments = counts['error'] or 0
        self.save(update_fields=['total_shipments', 'valid_shipments', 'warning_shipments', 'error_shipments', 'updated_at'])

    def lock(self):
        """Lock the session after purchase."""
        self.is_locked = True
        self.status = UploadSessionStatus.PURCHASED
        self.purchase_date = timezone.now()
        self.save(update_fields=['is_locked', 'status', 'purchase_date', 'updated_at'])

    def can_edit(self):
        """Check if session can be edited."""
        return not self.is_locked

    def clean(self):
        """Validate model constraints."""
        if self.is_locked and not self.terms_accepted:
            raise ValidationError("Terms must be accepted before locking session.")
        if self.is_locked and not self.label_size:
            raise ValidationError("Label size must be selected before locking session.")


class Shipment(BaseModel):
    """
    Individual shipment record.
    Can be created from CSV upload or manually.
    """
    upload_session = models.ForeignKey(
        UploadSession,
        on_delete=models.CASCADE,
        related_name='shipments',
        help_text="Parent upload session"
    )
    csv_row_number = models.IntegerField(
        null=True,
        blank=True,
        db_index=True,
        help_text="Original row number in CSV file"
    )
    status = models.CharField(
        max_length=20,
        choices=ShipmentStatus.CHOICES,
        default=ShipmentStatus.VALID,
        db_index=True,
        help_text="Validation status of shipment"
    )
    validation_messages = models.JSONField(
        default=list,
        blank=True,
        help_text="Array of validation warnings/errors"
    )
    address_validation_provider = models.CharField(
        max_length=20,
        choices=ValidationProvider.CHOICES,
        null=True,
        blank=True,
        help_text="Which provider validated the addresses"
    )
    customs_description = models.TextField(
        null=True,
        blank=True,
        help_text="Customs declaration description (international shipments)"
    )
    customs_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Customs declaration value (international shipments)"
    )
    reference_number = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="User-defined reference/order number"
    )

    class Meta:
        db_table = 'shipments'
        ordering = ['csv_row_number', 'created_at']
        indexes = [
            models.Index(fields=['upload_session', 'status']),
            models.Index(fields=['csv_row_number']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"Shipment {self.id} - Row {self.csv_row_number}"

    def add_validation_message(self, message, severity='warning'):
        """Add a validation message to the shipment."""
        if not isinstance(self.validation_messages, list):
            self.validation_messages = []

        self.validation_messages.append({
            'message': message,
            'severity': severity,
            'timestamp': timezone.now().isoformat()
        })

    def update_status_from_addresses(self):
        """
        Update shipment status based on address validation results.
        Called after address validation.
        """
        addresses = self.addresses.all()

        if not addresses.exists():
            self.status = ShipmentStatus.ERROR
            self.add_validation_message("Missing addresses", severity='error')
            self.save()
            return

        has_invalid = any(addr.validation_status == ValidationStatus.INVALID for addr in addresses)
        has_fallback = any(addr.validation_status == ValidationStatus.FALLBACK_VALID for addr in addresses)

        if has_invalid:
            self.status = ShipmentStatus.ERROR
        elif has_fallback:
            self.status = ShipmentStatus.WARNING
            self.add_validation_message("Address validated using fallback provider", severity='warning')
        else:
            # Check if all addresses are valid
            all_valid = all(addr.validation_status == ValidationStatus.VALID for addr in addresses)
            if all_valid:
                self.status = ShipmentStatus.VALID
                # Clear previous validation messages
                self.validation_messages = []
            else:
                self.status = ShipmentStatus.WARNING

        self.save()

        # Update session counts
        if self.upload_session:
            self.upload_session.update_counts()

    def can_edit(self):
        """Check if shipment can be edited."""
        return self.upload_session.can_edit() if self.upload_session else True


class Address(BaseModel):
    """
    Address model for Ship From and Ship To.
    Stores original input, validation status, and normalized address.
    """
    shipment = models.ForeignKey(
        Shipment,
        on_delete=models.CASCADE,
        related_name='addresses',
        help_text="Parent shipment"
    )
    address_type = models.CharField(
        max_length=20,
        choices=AddressType.CHOICES,
        db_index=True,
        help_text="Ship From or Ship To"
    )

    # Address fields
    name = models.CharField(max_length=255, help_text="Recipient/Sender name")
    company = models.CharField(max_length=255, null=True, blank=True)
    street1 = models.CharField(max_length=255, help_text="Street address line 1")
    street2 = models.CharField(max_length=255, null=True, blank=True, help_text="Street address line 2")
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=2, help_text="2-letter state code")
    zip_code = models.CharField(max_length=10, help_text="ZIP or ZIP+4")
    country = models.CharField(max_length=2, default=DEFAULT_COUNTRY, help_text="2-letter country code")
    phone = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)

    # Validation fields
    is_validated = models.BooleanField(
        default=False,
        help_text="Whether address has been validated"
    )
    validation_status = models.CharField(
        max_length=20,
        choices=ValidationStatus.CHOICES,
        default=ValidationStatus.PENDING,
        db_index=True,
        help_text="Validation result status"
    )
    validation_error = models.TextField(
        null=True,
        blank=True,
        help_text="Validation error message if invalid"
    )
    validated_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When address was last validated"
    )
    validated_by_provider = models.CharField(
        max_length=20,
        choices=ValidationProvider.CHOICES,
        null=True,
        blank=True,
        help_text="Which API provider validated this address"
    )

    # Store original and normalized versions
    original_input = models.JSONField(
        default=dict,
        blank=True,
        help_text="Original address before validation"
    )
    normalized_address = models.JSONField(
        null=True,
        blank=True,
        help_text="Normalized address returned by validation API"
    )

    class Meta:
        db_table = 'addresses'
        ordering = ['shipment', 'address_type']
        indexes = [
            models.Index(fields=['shipment', 'address_type']),
            models.Index(fields=['validation_status']),
        ]
        constraints = [
            # Ensure only one ship_from and one ship_to per shipment
            models.UniqueConstraint(
                fields=['shipment', 'address_type'],
                name='unique_address_type_per_shipment'
            )
        ]

    def __str__(self):
        return f"{self.get_address_type_display()} - {self.name} ({self.city}, {self.state})"

    def save_original(self):
        """Store the original input before validation."""
        self.original_input = {
            'name': self.name,
            'company': self.company,
            'street1': self.street1,
            'street2': self.street2,
            'city': self.city,
            'state': self.state,
            'zip_code': self.zip_code,
            'country': self.country,
            'phone': self.phone,
            'email': self.email,
        }

    def mark_as_validated(self, provider, is_valid=True, normalized_data=None, error_message=None):
        """
        Mark address as validated with results.

        Args:
            provider: Which validation provider was used
            is_valid: Whether validation succeeded
            normalized_data: Normalized address from API (if valid)
            error_message: Error message (if invalid)
        """
        self.is_validated = True
        self.validated_at = timezone.now()
        self.validated_by_provider = provider

        if is_valid:
            self.validation_status = ValidationStatus.VALID
            self.normalized_address = normalized_data
            self.validation_error = None
        else:
            self.validation_status = ValidationStatus.INVALID
            self.validation_error = error_message

        self.save()

    def mark_as_fallback_validated(self, provider, normalized_data=None):
        """Mark address as validated using fallback provider."""
        self.is_validated = True
        self.validated_at = timezone.now()
        self.validated_by_provider = provider
        self.validation_status = ValidationStatus.FALLBACK_VALID
        self.normalized_address = normalized_data
        self.save()


class Package(BaseModel):
    """
    Package dimensions and weight for a shipment.
    One-to-one relationship with Shipment.
    """
    shipment = models.OneToOneField(
        Shipment,
        on_delete=models.CASCADE,
        related_name='package',
        help_text="Parent shipment"
    )

    # Dimensions in inches
    length = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Length in inches"
    )
    width = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Width in inches"
    )
    height = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Height in inches"
    )

    # Weight in ounces (default unit)
    weight = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Weight in ounces"
    )
    weight_unit = models.CharField(
        max_length=5,
        choices=WeightUnit.CHOICES,
        default=WeightUnit.OZ,
        help_text="Unit of weight measurement"
    )

    # Package type
    package_type = models.CharField(
        max_length=20,
        choices=PackageType.CHOICES,
        default=PackageType.BOX,
        help_text="Type of package"
    )

    class Meta:
        db_table = 'packages'
        ordering = ['shipment']

    def __str__(self):
        return f"Package for {self.shipment.id} - {self.weight}{self.weight_unit}"

    def get_weight_in_ounces(self):
        """
        Convert weight to ounces for standardization.
        Returns weight rounded up to handle fractional ounces.
        """
        import math

        if self.weight_unit == WeightUnit.OZ:
            return math.ceil(float(self.weight))
        elif self.weight_unit == WeightUnit.LB:
            return math.ceil(float(self.weight) * 16)
        elif self.weight_unit == WeightUnit.G:
            return math.ceil(float(self.weight) / 28.3495)
        elif self.weight_unit == WeightUnit.KG:
            return math.ceil(float(self.weight) * 35.274)
        else:
            return math.ceil(float(self.weight))  # Default to oz


class ShippingServiceSelection(BaseModel):
    """
    Shipping service and pricing for a shipment.
    Auto-assigned based on weight, but can be overridden.
    """
    shipment = models.OneToOneField(
        Shipment,
        on_delete=models.CASCADE,
        related_name='shipping_service',
        help_text="Parent shipment"
    )
    service_type = models.CharField(
        max_length=30,
        choices=ServiceType.CHOICES,
        help_text="Type of shipping service"
    )
    service_tier = models.CharField(
        max_length=10,
        choices=ServiceTier.CHOICES,
        help_text="Service tier based on weight"
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Shipping price in USD"
    )
    currency = models.CharField(
        max_length=3,
        choices=Currency.CHOICES,
        default=Currency.USD
    )
    auto_selected = models.BooleanField(
        default=True,
        help_text="True if auto-assigned by weight, False if manually selected"
    )

    class Meta:
        db_table = 'shipping_service_selections'
        ordering = ['shipment']

    def __str__(self):
        return f"{self.get_service_type_display()} {self.get_service_tier_display()} - ${self.price}"


class SavedAddress(BaseModel):
    """
    Reusable ship-from addresses for bulk operations.
    Pre-populated with demo data.
    """
    nickname = models.CharField(
        max_length=100,
        unique=True,
        help_text="Friendly name for this address"
    )
    name = models.CharField(max_length=255)
    company = models.CharField(max_length=255, null=True, blank=True)
    street1 = models.CharField(max_length=255)
    street2 = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=2)
    zip_code = models.CharField(max_length=10)
    country = models.CharField(max_length=2, default=DEFAULT_COUNTRY)
    phone = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    is_default = models.BooleanField(
        default=False,
        help_text="Default address for new shipments"
    )

    class Meta:
        db_table = 'saved_addresses'
        ordering = ['-is_default', 'nickname']

    def __str__(self):
        return f"{self.nickname} - {self.city}, {self.state}"

    def save(self, *args, **kwargs):
        """Ensure only one default address."""
        if self.is_default:
            SavedAddress.objects.filter(is_default=True).update(is_default=False)
        super().save(*args, **kwargs)


class SavedPackage(BaseModel):
    """
    Reusable package presets for bulk operations.
    Pre-populated with demo data.
    """
    nickname = models.CharField(
        max_length=100,
        unique=True,
        help_text="Friendly name for this package preset"
    )
    length = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    width = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    height = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    weight = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    package_type = models.CharField(
        max_length=20,
        choices=PackageType.CHOICES,
        default=PackageType.BOX
    )
    is_default = models.BooleanField(
        default=False,
        help_text="Default package for new shipments"
    )

    class Meta:
        db_table = 'saved_packages'
        ordering = ['-is_default', 'nickname']

    def __str__(self):
        return f"{self.nickname} - {self.weight}oz"

    def save(self, *args, **kwargs):
        """Ensure only one default package."""
        if self.is_default:
            SavedPackage.objects.filter(is_default=True).update(is_default=False)
        super().save(*args, **kwargs)
