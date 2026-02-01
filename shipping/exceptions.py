"""
Custom exceptions and exception handler for the shipping app.
Provides consistent error responses across all API endpoints.
"""
import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError as DjangoValidationError

logger = logging.getLogger(__name__)


class ShippingException(Exception):
    """Base exception for shipping-related errors."""
    default_message = "An error occurred in the shipping system"
    default_status = status.HTTP_400_BAD_REQUEST

    def __init__(self, message=None, status_code=None, errors=None):
        self.message = message or self.default_message
        self.status_code = status_code or self.default_status
        self.errors = errors or {}
        super().__init__(self.message)


class CSVParsingException(ShippingException):
    """Raised when CSV parsing fails."""
    default_message = "CSV parsing failed"
    default_status = status.HTTP_400_BAD_REQUEST


class AddressValidationException(ShippingException):
    """Raised when address validation fails."""
    default_message = "Address validation failed"
    default_status = status.HTTP_422_UNPROCESSABLE_ENTITY


class SessionLockedException(ShippingException):
    """Raised when attempting to edit a locked session."""
    default_message = "This session is locked and cannot be edited"
    default_status = status.HTTP_403_FORBIDDEN


class InvalidShippingServiceException(ShippingException):
    """Raised when invalid shipping service is selected."""
    default_message = "Invalid shipping service selection"
    default_status = status.HTTP_400_BAD_REQUEST


class PurchaseException(ShippingException):
    """Raised when purchase fails validation."""
    default_message = "Purchase failed"
    default_status = status.HTTP_400_BAD_REQUEST


def custom_exception_handler(exc, context):
    """
    Custom exception handler that provides consistent error responses.

    Args:
        exc: The exception raised
        context: The context in which the exception was raised

    Returns:
        Response object with error details
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)

    # Handle custom shipping exceptions
    if isinstance(exc, ShippingException):
        logger.error(
            f"{exc.__class__.__name__}: {exc.message}",
            extra={
                'status_code': exc.status_code,
                'errors': exc.errors,
                'context': context
            }
        )

        error_response = {
            'error': exc.message,
            'status_code': exc.status_code,
        }

        if exc.errors:
            error_response['details'] = exc.errors

        return Response(error_response, status=exc.status_code)

    # Handle Django ValidationError
    if isinstance(exc, DjangoValidationError):
        logger.error(
            f"Django ValidationError: {str(exc)}",
            extra={'context': context}
        )

        error_response = {
            'error': 'Validation error',
            'status_code': status.HTTP_400_BAD_REQUEST,
            'details': exc.message_dict if hasattr(exc, 'message_dict') else {'message': exc.messages}
        }

        return Response(error_response, status=status.HTTP_400_BAD_REQUEST)

    # If response is already created by DRF, enhance it with our format
    if response is not None:
        logger.error(
            f"API Error: {exc.__class__.__name__}",
            extra={
                'status_code': response.status_code,
                'data': response.data,
                'context': context
            }
        )

        # Reformat the response to match our standard
        error_data = {
            'error': str(exc) if not response.data else response.data.get('detail', str(exc)),
            'status_code': response.status_code,
        }

        # Include validation errors if present
        if isinstance(response.data, dict) and len(response.data) > 1:
            error_data['details'] = {k: v for k, v in response.data.items() if k != 'detail'}

        response.data = error_data
        return response

    # Unhandled exceptions
    logger.exception(
        f"Unhandled exception: {exc.__class__.__name__}",
        extra={'context': context}
    )

    return Response(
        {
            'error': 'An unexpected error occurred',
            'status_code': status.HTTP_500_INTERNAL_SERVER_ERROR,
            'details': {'message': str(exc)} if logger.level == logging.DEBUG else {}
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
