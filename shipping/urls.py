"""
URL Configuration for shipping app.
Maps API endpoints to ViewSets using Django REST Framework routers.
"""
import os
from django.urls import path, include
from django.conf import settings
from django.http import HttpResponse
from rest_framework.routers import DefaultRouter
from .views import (
    UploadSessionViewSet,
    ShipmentViewSet,
    AddressViewSet,
    PackageViewSet,
    ShippingServiceSelectionViewSet,
    SavedAddressViewSet,
    SavedPackageViewSet,
)

# Create router and register viewsets
router = DefaultRouter()

# Upload sessions
router.register(r'sessions', UploadSessionViewSet, basename='session')

# Shipments
router.register(r'shipments', ShipmentViewSet, basename='shipment')

# Addresses and packages
router.register(r'addresses', AddressViewSet, basename='address')
router.register(r'packages', PackageViewSet, basename='package')
router.register(r'shipping-services', ShippingServiceSelectionViewSet, basename='shipping-service')

# Saved presets
router.register(r'saved-addresses', SavedAddressViewSet, basename='saved-address')
router.register(r'saved-packages', SavedPackageViewSet, basename='saved-package')

def download_template(request):
    """Serve Template.csv for download."""
    template_path = os.path.join(settings.BASE_DIR, 'Template.csv')
    if os.path.exists(template_path):
        with open(template_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="Template.csv"'
            return response
    return HttpResponse('Template not found', status=404)


# URL patterns
urlpatterns = [
    path('template.csv', download_template),
    path('', include(router.urls)),
]

"""
API Endpoint Summary:

Upload Sessions:
- GET    /api/sessions/                      - List all sessions
- POST   /api/sessions/                      - Create new session
- GET    /api/sessions/{id}/                 - Get session details
- PUT    /api/sessions/{id}/                 - Update session
- PATCH  /api/sessions/{id}/                 - Partial update session
- DELETE /api/sessions/{id}/                 - Delete session
- POST   /api/sessions/{id}/upload_csv/      - Upload CSV file
- POST   /api/sessions/{id}/purchase/        - Confirm purchase
- GET    /api/sessions/{id}/summary/         - Get session summary

Shipments:
- GET    /api/shipments/                     - List shipments (filter by ?session={id})
- POST   /api/shipments/                     - Create new shipment
- GET    /api/shipments/{id}/                - Get shipment details
- PUT    /api/shipments/{id}/                - Update shipment
- PATCH  /api/shipments/{id}/                - Partial update shipment
- DELETE /api/shipments/{id}/                - Delete shipment
- POST   /api/shipments/bulk_delete/         - Bulk delete shipments
- POST   /api/shipments/bulk_update_address/ - Bulk update ship-from address
- POST   /api/shipments/bulk_update_package/ - Bulk update package
- POST   /api/shipments/bulk_update_service/ - Bulk update shipping service

Addresses:
- GET    /api/addresses/                     - List addresses
- GET    /api/addresses/{id}/                - Get address details
- PUT    /api/addresses/{id}/                - Update address (triggers re-validation)
- PATCH  /api/addresses/{id}/                - Partial update address
- DELETE /api/addresses/{id}/                - Delete address

Packages:
- GET    /api/packages/                      - List packages
- GET    /api/packages/{id}/                 - Get package details
- PUT    /api/packages/{id}/                 - Update package (recalculates shipping)
- PATCH  /api/packages/{id}/                 - Partial update package
- DELETE /api/packages/{id}/                 - Delete package

Shipping Services:
- GET    /api/shipping-services/             - List shipping services
- GET    /api/shipping-services/{id}/        - Get service details
- PUT    /api/shipping-services/{id}/        - Update service
- PATCH  /api/shipping-services/{id}/        - Partial update service

Saved Addresses:
- GET    /api/saved-addresses/               - List saved addresses
- POST   /api/saved-addresses/               - Create saved address
- GET    /api/saved-addresses/{id}/          - Get saved address details
- PUT    /api/saved-addresses/{id}/          - Update saved address
- PATCH  /api/saved-addresses/{id}/          - Partial update saved address
- DELETE /api/saved-addresses/{id}/          - Delete saved address

Saved Packages:
- GET    /api/saved-packages/                - List saved packages
- POST   /api/saved-packages/                - Create saved package
- GET    /api/saved-packages/{id}/           - Get saved package details
- PUT    /api/saved-packages/{id}/           - Update saved package
- PATCH  /api/saved-packages/{id}/           - Partial update saved package
- DELETE /api/saved-packages/{id}/           - Delete saved package
"""
