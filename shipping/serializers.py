"""
DRF Serializers for all shipping models.
Handles validation, nested relationships, and API representation.
"""
from rest_framework import serializers
from decimal import Decimal
from .models import (
    UploadSession, Shipment, Address, Package,
    ShippingServiceSelection, SavedAddress, SavedPackage
)
from .constants import (
    UploadSessionStatus, ShipmentStatus, AddressType,
    ValidationStatus, PackageType, ServiceType, ServiceTier,
    LabelSize, REQUIRED_ADDRESS_FIELDS, REQUIRED_PACKAGE_FIELDS
)


class AddressSerializer(serializers.ModelSerializer):
    """
    Serializer for Address model with validation.
    """
    address_type_display = serializers.CharField(
        source='get_address_type_display',
        read_only=True
    )
    validation_status_display = serializers.CharField(
        source='get_validation_status_display',
        read_only=True
    )

    class Meta:
        model = Address
        fields = [
            'id', 'shipment', 'address_type', 'address_type_display',
            'name', 'company', 'street1', 'street2', 'city', 'state',
            'zip_code', 'country', 'phone', 'email',
            'is_validated', 'validation_status', 'validation_status_display',
            'validation_error', 'validated_at', 'validated_by_provider',
            'original_input', 'normalized_address',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'is_validated', 'validation_status', 'validation_error',
            'validated_at', 'validated_by_provider', 'original_input',
            'normalized_address', 'created_at', 'updated_at'
        ]

    def validate(self, data):
        """Validate required address fields."""
        errors = {}

        for field in REQUIRED_ADDRESS_FIELDS:
            if field not in data or not data[field]:
                errors[field] = f"{field.replace('_', ' ').title()} is required"

        # Validate state code (2 letters)
        if 'state' in data and data['state']:
            if len(data['state']) != 2:
                errors['state'] = "State must be a 2-letter code"

        if errors:
            raise serializers.ValidationError(errors)

        return data


class AddressCreateSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for creating addresses (no read-only fields).
    """
    class Meta:
        model = Address
        fields = [
            'address_type', 'name', 'company', 'street1', 'street2',
            'city', 'state', 'zip_code', 'country', 'phone', 'email'
        ]


class PackageSerializer(serializers.ModelSerializer):
    """
    Serializer for Package model with weight conversion.
    """
    weight_in_ounces = serializers.SerializerMethodField()

    class Meta:
        model = Package
        fields = [
            'id', 'shipment', 'length', 'width', 'height',
            'weight', 'weight_unit', 'weight_in_ounces',
            'package_type', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_weight_in_ounces(self, obj):
        """Return weight converted to ounces."""
        return obj.get_weight_in_ounces()

    def validate(self, data):
        """Validate package dimensions and weight."""
        errors = {}

        # Validate required fields
        for field in REQUIRED_PACKAGE_FIELDS:
            if field not in data or not data[field]:
                errors[field] = f"{field.replace('_', ' ').title()} is required"

        # Validate positive values
        for field in ['length', 'width', 'height', 'weight']:
            if field in data and data[field] <= 0:
                errors[field] = f"{field.title()} must be greater than 0"

        if errors:
            raise serializers.ValidationError(errors)

        return data


class PackageCreateSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for creating packages.
    """
    class Meta:
        model = Package
        fields = ['length', 'width', 'height', 'weight', 'weight_unit', 'package_type']


class ShippingServiceSelectionSerializer(serializers.ModelSerializer):
    """
    Serializer for ShippingServiceSelection with display names.
    """
    service_type_display = serializers.CharField(
        source='get_service_type_display',
        read_only=True
    )
    service_tier_display = serializers.CharField(
        source='get_service_tier_display',
        read_only=True
    )

    class Meta:
        model = ShippingServiceSelection
        fields = [
            'id', 'shipment', 'service_type', 'service_type_display',
            'service_tier', 'service_tier_display', 'price', 'currency',
            'auto_selected', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'auto_selected', 'created_at', 'updated_at']


class ShipmentSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for Shipment with nested relationships.
    """
    addresses = AddressSerializer(many=True, read_only=True)
    package = PackageSerializer(read_only=True)
    shipping_service = ShippingServiceSelectionSerializer(read_only=True)
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )
    can_edit = serializers.SerializerMethodField()

    class Meta:
        model = Shipment
        fields = [
            'id', 'upload_session', 'csv_row_number', 'status', 'status_display',
            'validation_messages', 'address_validation_provider',
            'customs_description', 'customs_value', 'reference_number',
            'addresses', 'package', 'shipping_service', 'can_edit',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'status', 'validation_messages', 'address_validation_provider',
            'created_at', 'updated_at'
        ]

    def get_can_edit(self, obj):
        """Check if shipment can be edited."""
        return obj.can_edit()


class ShipmentCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating shipments with nested objects.
    """
    ship_from = AddressCreateSerializer()
    ship_to = AddressCreateSerializer()
    package = PackageCreateSerializer()

    class Meta:
        model = Shipment
        fields = [
            'upload_session', 'ship_from', 'ship_to', 'package',
            'customs_description', 'customs_value', 'reference_number'
        ]

    def create(self, validated_data):
        """Create shipment with nested addresses and package."""
        from .services.address_validator import AddressValidatorService
        from .services.shipping_calculator import ShippingCalculatorService

        ship_from_data = validated_data.pop('ship_from')
        ship_to_data = validated_data.pop('ship_to')
        package_data = validated_data.pop('package')

        # Create shipment
        shipment = Shipment.objects.create(**validated_data)

        # Create addresses
        ship_from = Address.objects.create(
            shipment=shipment,
            address_type=AddressType.SHIP_FROM,
            **ship_from_data
        )
        ship_to = Address.objects.create(
            shipment=shipment,
            address_type=AddressType.SHIP_TO,
            **ship_to_data
        )

        # Create package
        package = Package.objects.create(
            shipment=shipment,
            **package_data
        )

        # Validate addresses
        validator = AddressValidatorService()
        validator.validate_shipment_addresses(shipment)

        # Calculate and assign shipping service
        calculator = ShippingCalculatorService()
        calculator.assign_default_service(shipment)

        # Refresh from database to get all relationships
        shipment.refresh_from_db()

        return shipment


class ShipmentListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing shipments.
    """
    ship_from_summary = serializers.SerializerMethodField()
    ship_to_summary = serializers.SerializerMethodField()
    shipping_price = serializers.SerializerMethodField()
    package_summary = serializers.SerializerMethodField()
    package = serializers.SerializerMethodField()
    shipping_service = serializers.SerializerMethodField()
    available_services = serializers.SerializerMethodField()
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )

    class Meta:
        model = Shipment
        fields = [
            'id', 'upload_session', 'csv_row_number', 'status', 'status_display',
            'ship_from_summary', 'ship_to_summary', 'package_summary', 'package',
            'shipping_price', 'shipping_service', 'available_services',
            'reference_number', 'created_at'
        ]

    def get_ship_from_summary(self, obj):
        """Return brief ship-from address."""
        try:
            addr = obj.addresses.get(address_type=AddressType.SHIP_FROM)
            return f"{addr.name} - {addr.city}, {addr.state}"
        except Address.DoesNotExist:
            return None

    def get_ship_to_summary(self, obj):
        """Return brief ship-to address."""
        try:
            addr = obj.addresses.get(address_type=AddressType.SHIP_TO)
            return f"{addr.name} - {addr.city}, {addr.state}"
        except Address.DoesNotExist:
            return None

    def get_package_summary(self, obj):
        """Return package dimensions and weight."""
        try:
            pkg = obj.package
            return f"{pkg.length}x{pkg.width}x{pkg.height} in, {pkg.weight} oz"
        except (AttributeError, Package.DoesNotExist):
            return None

    def get_package(self, obj):
        """Return package with weight for shipping calculation."""
        try:
            pkg = obj.package
            return {
                'id': str(pkg.id),
                'weight_in_ounces': pkg.get_weight_in_ounces(),
                'length': str(pkg.length),
                'width': str(pkg.width),
                'height': str(pkg.height),
                'weight': str(pkg.weight),
            }
        except (AttributeError, Package.DoesNotExist):
            return None

    def get_available_services(self, obj):
        """Return available shipping options for this package weight."""
        from .services.shipping_calculator import ShippingCalculatorService
        try:
            weight_oz = obj.package.get_weight_in_ounces()
            calc = ShippingCalculatorService()
            return calc.get_available_services_for_weight(weight_oz)
        except (AttributeError, Package.DoesNotExist):
            return []

    def get_shipping_service(self, obj):
        """Return shipping service for selector."""
        try:
            svc = obj.shipping_service
            return {
                'id': str(svc.id),
                'service_type': svc.service_type,
                'service_type_display': svc.get_service_type_display(),
                'service_tier': svc.service_tier,
                'price': str(svc.price),
            }
        except (AttributeError, ShippingServiceSelection.DoesNotExist):
            return None

    def get_shipping_price(self, obj):
        """Return shipping price."""
        try:
            return str(obj.shipping_service.price)
        except (AttributeError, ShippingServiceSelection.DoesNotExist):
            return None


class UploadSessionSerializer(serializers.ModelSerializer):
    """
    Serializer for UploadSession with statistics.
    """
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )
    label_size_display = serializers.CharField(
        source='get_label_size_display',
        read_only=True
    )
    can_edit = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = UploadSession
        fields = [
            'id', 'status', 'status_display', 'total_shipments',
            'valid_shipments', 'warning_shipments', 'error_shipments',
            'is_locked', 'purchase_date', 'label_size', 'label_size_display',
            'terms_accepted', 'can_edit', 'total_price',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'total_shipments', 'valid_shipments', 'warning_shipments',
            'error_shipments', 'is_locked', 'purchase_date',
            'created_at', 'updated_at'
        ]

    def get_can_edit(self, obj):
        """Check if session can be edited."""
        return obj.can_edit()

    def get_total_price(self, obj):
        """Calculate total price of all shipments."""
        from django.db.models import Sum
        total = obj.shipments.aggregate(
            total=Sum('shipping_service__price')
        )['total']
        return str(total) if total else "0.00"


class UploadSessionDetailSerializer(UploadSessionSerializer):
    """
    Detailed serializer for UploadSession with nested shipments.
    """
    shipments = ShipmentListSerializer(many=True, read_only=True)

    class Meta(UploadSessionSerializer.Meta):
        fields = UploadSessionSerializer.Meta.fields + ['shipments']


class PurchaseConfirmationSerializer(serializers.Serializer):
    """
    Serializer for purchase confirmation request.
    """
    label_size = serializers.ChoiceField(
        choices=LabelSize.CHOICES,
        required=True,
        help_text="Select label size: letter or 4x6"
    )
    terms_accepted = serializers.BooleanField(
        required=True,
        help_text="Must accept terms and conditions"
    )

    def validate_terms_accepted(self, value):
        """Ensure terms are accepted."""
        if not value:
            raise serializers.ValidationError("You must accept the terms and conditions")
        return value


class SavedAddressSerializer(serializers.ModelSerializer):
    """
    Serializer for SavedAddress.
    """
    class Meta:
        model = SavedAddress
        fields = [
            'id', 'nickname', 'name', 'company', 'street1', 'street2',
            'city', 'state', 'zip_code', 'country', 'phone', 'email',
            'is_default', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, data):
        """Validate required address fields."""
        errors = {}

        for field in REQUIRED_ADDRESS_FIELDS:
            if field not in data or not data[field]:
                errors[field] = f"{field.replace('_', ' ').title()} is required"

        if errors:
            raise serializers.ValidationError(errors)

        return data


class SavedPackageSerializer(serializers.ModelSerializer):
    """
    Serializer for SavedPackage.
    """
    class Meta:
        model = SavedPackage
        fields = [
            'id', 'nickname', 'length', 'width', 'height',
            'weight', 'package_type', 'is_default',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, data):
        """Validate package dimensions and weight."""
        errors = {}

        # Validate positive values
        for field in ['length', 'width', 'height', 'weight']:
            if field in data and data[field] <= 0:
                errors[field] = f"{field.title()} must be greater than 0"

        if errors:
            raise serializers.ValidationError(errors)

        return data


class BulkUpdateAddressSerializer(serializers.Serializer):
    """
    Serializer for bulk address update operations.
    """
    shipment_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=True,
        help_text="List of shipment IDs to update"
    )
    saved_address_id = serializers.UUIDField(
        required=True,
        help_text="ID of saved address to apply"
    )


class BulkUpdatePackageSerializer(serializers.Serializer):
    """
    Serializer for bulk package update operations.
    """
    shipment_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=True,
        help_text="List of shipment IDs to update"
    )
    saved_package_id = serializers.UUIDField(
        required=True,
        help_text="ID of saved package to apply"
    )


class BulkUpdateShippingServiceSerializer(serializers.Serializer):
    """
    Serializer for bulk shipping service update.
    service_type: 'priority_mail', 'ground_shipping', or 'most_affordable'
    """
    shipment_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=True,
        help_text="List of shipment IDs to update"
    )
    service_type = serializers.ChoiceField(
        choices=list(ServiceType.CHOICES) + [('most_affordable', 'Most Affordable')],
        required=True,
        help_text="Shipping service type or most_affordable"
    )


class BulkDeleteSerializer(serializers.Serializer):
    """
    Serializer for bulk delete operations.
    """
    shipment_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=True,
        help_text="List of shipment IDs to delete"
    )
