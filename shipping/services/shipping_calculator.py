"""
Shipping Calculator Service
Handles shipping rate calculation based on weight tiers and business rules.

Business Rules (PRD Appendix C):
1. Weight-based tier assignment:
   - 0-8 oz → Tier 1
   - 9-16 oz → Tier 2
   - 17-32 oz → Tier 3 (Priority only)
   - 33+ oz → Tier 4 (Priority only)

2. Ground shipping only for weight strictly under 16 oz

3. Fractional weights round up to next tier

4. Missing weight defaults to Priority Mail Tier 1 ($4.00)
"""
import logging
import math
from decimal import Decimal
from ..models import ShippingServiceSelection, Package
from ..constants import (
    ServiceType, ServiceTier, Currency, PRICING_TABLE,
    GROUND_SHIPPING_MAX_WEIGHT_OZ, DEFAULT_SERVICE_TYPE,
    DEFAULT_SERVICE_TIER
)
from ..exceptions import InvalidShippingServiceException

logger = logging.getLogger(__name__)


class ShippingCalculatorService:
    """
    Service for calculating shipping rates and assigning services.
    """

    def __init__(self):
        self.pricing = PRICING_TABLE

    def assign_default_service(self, shipment):
        """
        Assign default shipping service based on package weight.

        Args:
            shipment: Shipment instance with package

        Returns:
            ShippingServiceSelection instance
        """
        logger.info(
            f"Assigning default shipping service for shipment {shipment.id}",
            extra={'shipment_id': str(shipment.id)}
        )

        try:
            package = shipment.package
        except Package.DoesNotExist:
            logger.warning(
                f"No package found for shipment {shipment.id}, using defaults",
                extra={'shipment_id': str(shipment.id)}
            )
            # Create default shipping service
            return self._create_shipping_service(
                shipment,
                DEFAULT_SERVICE_TYPE,
                DEFAULT_SERVICE_TIER,
                auto_selected=True
            )

        # Get weight in ounces (rounded up)
        weight_oz = package.get_weight_in_ounces()

        logger.debug(
            f"Package weight: {weight_oz} oz",
            extra={'shipment_id': str(shipment.id), 'weight_oz': weight_oz}
        )

        # Determine service type and tier based on weight
        service_type, service_tier = self._determine_service_from_weight(weight_oz)

        # Create shipping service selection
        shipping_service = self._create_shipping_service(
            shipment,
            service_type,
            service_tier,
            auto_selected=True
        )

        logger.info(
            f"Assigned {service_type} {service_tier} for shipment {shipment.id}",
            extra={
                'shipment_id': str(shipment.id),
                'service_type': service_type,
                'service_tier': service_tier,
                'price': str(shipping_service.price)
            }
        )

        return shipping_service

    def update_shipping_service(self, shipment, service_type, service_tier=None):
        """
        Update shipping service for a shipment.

        Args:
            shipment: Shipment instance
            service_type: Desired service type
            service_tier: Optional tier (auto-calculated if not provided)

        Returns:
            ShippingServiceSelection instance

        Raises:
            InvalidShippingServiceException: If service is invalid for weight
        """
        logger.info(
            f"Updating shipping service for shipment {shipment.id}",
            extra={
                'shipment_id': str(shipment.id),
                'service_type': service_type,
                'service_tier': service_tier
            }
        )

        # Get package weight
        try:
            package = shipment.package
            weight_oz = package.get_weight_in_ounces()
        except Package.DoesNotExist:
            weight_oz = 0

        # Validate service selection against weight
        if service_type == ServiceType.GROUND_SHIPPING:
            if weight_oz >= GROUND_SHIPPING_MAX_WEIGHT_OZ:
                raise InvalidShippingServiceException(
                    f"Ground shipping not available for packages {GROUND_SHIPPING_MAX_WEIGHT_OZ}+ oz (current weight: {weight_oz} oz)",
                    errors={
                        'service_type': f'Ground shipping only available for weight < {GROUND_SHIPPING_MAX_WEIGHT_OZ} oz'
                    }
                )

        # Auto-determine tier if not provided
        if not service_tier:
            service_tier = self._determine_tier_from_weight(weight_oz)

        # Delete existing shipping service if present
        try:
            shipment.shipping_service.delete()
        except ShippingServiceSelection.DoesNotExist:
            pass

        # Create new shipping service
        shipping_service = self._create_shipping_service(
            shipment,
            service_type,
            service_tier,
            auto_selected=False
        )

        logger.info(
            f"Updated shipping service for shipment {shipment.id}",
            extra={
                'shipment_id': str(shipment.id),
                'service_type': service_type,
                'service_tier': service_tier,
                'price': str(shipping_service.price)
            }
        )

        return shipping_service

    def recalculate_service_after_weight_change(self, shipment):
        """
        Recalculate shipping service after package weight changes.

        Args:
            shipment: Shipment instance

        Returns:
            ShippingServiceSelection instance
        """
        logger.info(
            f"Recalculating shipping service after weight change for shipment {shipment.id}",
            extra={'shipment_id': str(shipment.id)}
        )

        try:
            current_service = shipment.shipping_service

            # If manually selected, keep the service type but update tier and price
            if not current_service.auto_selected:
                return self.update_shipping_service(
                    shipment,
                    current_service.service_type
                )
            else:
                # If auto-selected, delete it and create a new one
                current_service.delete()
        except ShippingServiceSelection.DoesNotExist:
            pass

        # Assign new default service
        return self.assign_default_service(shipment)

    def calculate_session_total(self, upload_session):
        """
        Calculate total shipping cost for all shipments in a session.

        Args:
            upload_session: UploadSession instance

        Returns:
            Decimal: Total price
        """
        from django.db.models import Sum

        total = upload_session.shipments.aggregate(
            total=Sum('shipping_service__price')
        )['total']

        logger.info(
            f"Calculated total for session {upload_session.id}: ${total or 0}",
            extra={
                'session_id': str(upload_session.id),
                'total': str(total or 0)
            }
        )

        return total or Decimal('0.00')

    def _determine_service_from_weight(self, weight_oz):
        """
        Determine service type and tier from weight.

        Args:
            weight_oz: Weight in ounces

        Returns:
            tuple: (service_type, service_tier)
        """
        # Default to Priority Mail
        service_type = ServiceType.PRIORITY_MAIL
        service_tier = self._determine_tier_from_weight(weight_oz)

        return (service_type, service_tier)

    def _determine_tier_from_weight(self, weight_oz):
        """
        Determine service tier from weight (PRD: fractional rounds up).

        Args:
            weight_oz: Weight in ounces (already rounded up)

        Returns:
            str: Service tier
        """
        if weight_oz <= 8:
            return ServiceTier.TIER_1
        elif weight_oz <= 16:
            return ServiceTier.TIER_2
        elif weight_oz <= 32:
            return ServiceTier.TIER_3
        else:
            return ServiceTier.TIER_4

    def _create_shipping_service(self, shipment, service_type, service_tier, auto_selected=True):
        """
        Create ShippingServiceSelection with calculated price.

        Args:
            shipment: Shipment instance
            service_type: Service type
            service_tier: Service tier
            auto_selected: Whether auto-assigned

        Returns:
            ShippingServiceSelection instance

        Raises:
            InvalidShippingServiceException: If pricing not found
        """
        # Get price from pricing table
        try:
            price = Decimal(str(self.pricing[service_type][service_tier]['price']))
        except KeyError:
            logger.error(
                f"Pricing not found for {service_type} {service_tier}",
                extra={'service_type': service_type, 'service_tier': service_tier}
            )
            raise InvalidShippingServiceException(
                f"Invalid service combination: {service_type} {service_tier}",
                errors={'service': 'Pricing not available for this service'}
            )

        # Create shipping service selection
        shipping_service = ShippingServiceSelection.objects.create(
            shipment=shipment,
            service_type=service_type,
            service_tier=service_tier,
            price=price,
            currency=Currency.USD,
            auto_selected=auto_selected
        )

        return shipping_service

    def get_available_services_for_weight(self, weight_oz):
        """
        Get list of available services for a given weight.

        Args:
            weight_oz: Weight in ounces

        Returns:
            list: Available services with pricing
        """
        tier = self._determine_tier_from_weight(weight_oz)
        available = []

        # Priority Mail is always available
        if tier in self.pricing[ServiceType.PRIORITY_MAIL]:
            price = self.pricing[ServiceType.PRIORITY_MAIL][tier]['price']
            available.append({
                'service_type': ServiceType.PRIORITY_MAIL,
                'service_tier': tier,
                'price': price,
                'description': f'Priority Mail {tier.replace("_", " ").title()}'
            })

        # Ground Shipping only if weight < 16 oz
        if weight_oz < GROUND_SHIPPING_MAX_WEIGHT_OZ:
            if tier in self.pricing[ServiceType.GROUND_SHIPPING]:
                price = self.pricing[ServiceType.GROUND_SHIPPING][tier]['price']
                available.append({
                    'service_type': ServiceType.GROUND_SHIPPING,
                    'service_tier': tier,
                    'price': price,
                    'description': f'Ground Shipping {tier.replace("_", " ").title()}'
                })

        return available
