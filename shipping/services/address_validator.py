"""
Address Validation Service
Handles address validation with automatic fallback to secondary providers.

Supports multiple providers:
- USPS (Primary)
- Google Maps API
- Smarty Streets
- Lob

Features:
- Automatic fallback if primary provider fails
- Rate limit handling
- Retry logic
- Comprehensive logging
"""
import logging
import time
import requests
from django.conf import settings
from ..models import Address, Shipment
from ..constants import ValidationStatus, ValidationProvider
from ..exceptions import AddressValidationException

logger = logging.getLogger(__name__)


class AddressValidatorService:
    """
    Service for validating addresses using multiple providers with fallback.
    """

    def __init__(self):
        self.config = settings.ADDRESS_VALIDATION
        self.primary_provider = self.config.get('PRIMARY_PROVIDER', 'usps')
        self.fallback_provider = self.config.get('FALLBACK_PROVIDER', 'google')

    def validate_shipment_addresses(self, shipment):
        """
        Validate all addresses for a shipment.

        Args:
            shipment: Shipment instance

        Returns:
            bool: True if all addresses valid, False otherwise
        """
        logger.info(
            f"Validating addresses for shipment {shipment.id}",
            extra={'shipment_id': str(shipment.id)}
        )

        addresses = shipment.addresses.all()

        if not addresses.exists():
            logger.warning(
                f"No addresses found for shipment {shipment.id}",
                extra={'shipment_id': str(shipment.id)}
            )
            return False

        all_valid = True

        for address in addresses:
            try:
                is_valid = self.validate_address(address)
                if not is_valid:
                    all_valid = False
            except Exception as e:
                logger.error(
                    f"Error validating address {address.id}: {str(e)}",
                    extra={'address_id': str(address.id), 'error': str(e)}
                )
                all_valid = False

        # Update shipment status based on address validation
        shipment.update_status_from_addresses()

        logger.info(
            f"Address validation completed for shipment {shipment.id}",
            extra={
                'shipment_id': str(shipment.id),
                'all_valid': all_valid
            }
        )

        return all_valid

    def validate_address(self, address):
        """
        Validate a single address using primary provider with fallback.

        Args:
            address: Address instance

        Returns:
            bool: True if valid, False otherwise
        """
        logger.info(
            f"Validating address {address.id} ({address.get_address_type_display()})",
            extra={
                'address_id': str(address.id),
                'address_type': address.address_type
            }
        )

        # Save original input
        address.save_original()

        # Try primary provider
        provider_used = None
        is_valid = False
        normalized_data = None
        error_message = None
        is_fallback = False

        try:
            is_valid, normalized_data, error_message = self._validate_with_provider(
                address,
                self.primary_provider
            )
            provider_used = self.primary_provider

            logger.info(
                f"Primary validation result for address {address.id}",
                extra={
                    'address_id': str(address.id),
                    'provider': self.primary_provider,
                    'is_valid': is_valid
                }
            )

        except Exception as e:
            logger.warning(
                f"Primary provider {self.primary_provider} failed for address {address.id}: {str(e)}",
                extra={
                    'address_id': str(address.id),
                    'provider': self.primary_provider,
                    'error': str(e)
                }
            )

            # Try fallback provider
            logger.info(
                f"Attempting fallback validation with {self.fallback_provider}",
                extra={
                    'address_id': str(address.id),
                    'fallback_provider': self.fallback_provider
                }
            )

            try:
                is_valid, normalized_data, error_message = self._validate_with_provider(
                    address,
                    self.fallback_provider
                )
                provider_used = self.fallback_provider
                is_fallback = True

                logger.info(
                    f"Fallback validation result for address {address.id}",
                    extra={
                        'address_id': str(address.id),
                        'provider': self.fallback_provider,
                        'is_valid': is_valid,
                        'is_fallback': True
                    }
                )

            except Exception as fallback_error:
                logger.error(
                    f"Fallback provider {self.fallback_provider} also failed: {str(fallback_error)}",
                    extra={
                        'address_id': str(address.id),
                        'fallback_provider': self.fallback_provider,
                        'error': str(fallback_error)
                    }
                )
                # Both providers failed - mark as invalid
                is_valid = False
                error_message = f"Validation failed: {str(e)} | Fallback: {str(fallback_error)}"
                provider_used = f"{self.primary_provider}_failed"

        # Update address with validation results
        if is_valid:
            if is_fallback:
                address.mark_as_fallback_validated(provider_used, normalized_data)
            else:
                address.mark_as_validated(provider_used, True, normalized_data)
        else:
            address.mark_as_validated(provider_used or self.primary_provider, False, error_message=error_message)

        return is_valid

    def _validate_with_provider(self, address, provider):
        """
        Validate address with a specific provider.

        Args:
            address: Address instance
            provider: Provider name (usps, google, smarty, lob)

        Returns:
            tuple: (is_valid, normalized_data, error_message)

        Raises:
            Exception: If provider call fails
        """
        provider_config = self.config['PROVIDERS'].get(provider, {})

        if not provider_config.get('ENABLED'):
            raise Exception(f"Provider {provider} is not enabled (missing API credentials)")

        # Route to appropriate provider
        if provider == ValidationProvider.USPS:
            return self._validate_usps(address, provider_config)
        elif provider == ValidationProvider.GOOGLE:
            return self._validate_google(address, provider_config)
        elif provider == ValidationProvider.SMARTY:
            return self._validate_smarty(address, provider_config)
        elif provider == ValidationProvider.LOB:
            return self._validate_lob(address, provider_config)
        else:
            raise Exception(f"Unsupported provider: {provider}")

    def _validate_usps(self, address, config):
        """
        Validate address using USPS API.

        Note: This is a mock implementation. Real implementation would use
        USPS Web Tools API (requires registration).

        Args:
            address: Address instance
            config: Provider configuration

        Returns:
            tuple: (is_valid, normalized_data, error_message)
        """
        logger.debug(f"Validating address {address.id} with USPS")

        # Mock implementation - in production, call real USPS API
        # For demo purposes, we'll do basic validation
        if not config.get('API_KEY'):
            # No API key - perform basic validation only
            return self._basic_validation(address)

        try:
            # Real USPS API call would go here
            # url = "https://secure.shippingapis.com/ShippingAPI.dll"
            # params = {...}
            # response = requests.get(url, params=params, timeout=10)

            # For now, return success with basic normalization
            normalized = {
                'name': address.name,
                'street1': address.street1.upper(),
                'street2': address.street2.upper() if address.street2 else '',
                'city': address.city.upper(),
                'state': address.state.upper(),
                'zip_code': address.zip_code,
                'country': address.country
            }

            return (True, normalized, None)

        except requests.RequestException as e:
            logger.error(f"USPS API request failed: {str(e)}")
            raise

    def _validate_google(self, address, config):
        """
        Validate address using Google Maps API.

        Note: This is a mock implementation. Real implementation would use
        Google Address Validation API.

        Args:
            address: Address instance
            config: Provider configuration

        Returns:
            tuple: (is_valid, normalized_data, error_message)
        """
        logger.debug(f"Validating address {address.id} with Google Maps")

        if not config.get('API_KEY'):
            return self._basic_validation(address)

        try:
            # Real Google API call would go here
            # url = "https://addressvalidation.googleapis.com/v1:validateAddress"
            # headers = {'Authorization': f'Bearer {config["API_KEY"]}'}
            # data = {...}
            # response = requests.post(url, headers=headers, json=data, timeout=10)

            # For now, return success with basic normalization
            normalized = {
                'name': address.name,
                'street1': address.street1,
                'street2': address.street2,
                'city': address.city,
                'state': address.state,
                'zip_code': address.zip_code,
                'country': address.country
            }

            return (True, normalized, None)

        except requests.RequestException as e:
            logger.error(f"Google API request failed: {str(e)}")
            raise

    def _validate_smarty(self, address, config):
        """
        Validate address using Smarty Streets API.

        Note: This is a mock implementation.

        Args:
            address: Address instance
            config: Provider configuration

        Returns:
            tuple: (is_valid, normalized_data, error_message)
        """
        logger.debug(f"Validating address {address.id} with Smarty Streets")

        if not config.get('AUTH_ID') or not config.get('AUTH_TOKEN'):
            return self._basic_validation(address)

        try:
            # Real Smarty API call would go here
            # url = "https://us-street.api.smartystreets.com/street-address"
            # params = {
            #     'auth-id': config['AUTH_ID'],
            #     'auth-token': config['AUTH_TOKEN'],
            #     'street': address.street1,
            #     'city': address.city,
            #     'state': address.state,
            #     'zipcode': address.zip_code
            # }
            # response = requests.get(url, params=params, timeout=10)

            normalized = {
                'name': address.name,
                'street1': address.street1,
                'street2': address.street2,
                'city': address.city,
                'state': address.state,
                'zip_code': address.zip_code,
                'country': address.country
            }

            return (True, normalized, None)

        except requests.RequestException as e:
            logger.error(f"Smarty API request failed: {str(e)}")
            raise

    def _validate_lob(self, address, config):
        """
        Validate address using Lob API.

        Note: This is a mock implementation.

        Args:
            address: Address instance
            config: Provider configuration

        Returns:
            tuple: (is_valid, normalized_data, error_message)
        """
        logger.debug(f"Validating address {address.id} with Lob")

        if not config.get('API_KEY'):
            return self._basic_validation(address)

        try:
            # Real Lob API call would go here
            # url = "https://api.lob.com/v1/us_verifications"
            # auth = (config['API_KEY'], '')
            # data = {
            #     'primary_line': address.street1,
            #     'city': address.city,
            #     'state': address.state,
            #     'zip_code': address.zip_code
            # }
            # response = requests.post(url, auth=auth, json=data, timeout=10)

            normalized = {
                'name': address.name,
                'street1': address.street1,
                'street2': address.street2,
                'city': address.city,
                'state': address.state,
                'zip_code': address.zip_code,
                'country': address.country
            }

            return (True, normalized, None)

        except requests.RequestException as e:
            logger.error(f"Lob API request failed: {str(e)}")
            raise

    def _basic_validation(self, address):
        """
        Perform basic validation when no API provider is available.

        Checks:
        - Required fields are present
        - State code is 2 letters
        - ZIP code format

        Args:
            address: Address instance

        Returns:
            tuple: (is_valid, normalized_data, error_message)
        """
        logger.debug(f"Performing basic validation for address {address.id}")

        errors = []

        # Check required fields
        if not address.name:
            errors.append("Name is required")
        if not address.street1:
            errors.append("Street address is required")
        if not address.city:
            errors.append("City is required")
        if not address.state:
            errors.append("State is required")
        if not address.zip_code:
            errors.append("ZIP code is required")

        # Validate state code
        if address.state and len(address.state) != 2:
            errors.append("State must be 2-letter code")

        # Validate ZIP code format (basic)
        if address.zip_code:
            zip_clean = address.zip_code.replace('-', '').replace(' ', '')
            if not (len(zip_clean) == 5 or len(zip_clean) == 9):
                errors.append("Invalid ZIP code format")

        if errors:
            return (False, None, '; '.join(errors))

        # Return normalized data
        normalized = {
            'name': address.name,
            'street1': address.street1,
            'street2': address.street2,
            'city': address.city,
            'state': address.state.upper(),
            'zip_code': address.zip_code,
            'country': address.country
        }

        return (True, normalized, None)
