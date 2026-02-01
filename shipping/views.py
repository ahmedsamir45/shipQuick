"""
API Views and ViewSets for the shipping application.
Handles all REST API endpoints with proper error handling and logging.
"""
import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.db import transaction
from django.shortcuts import get_object_or_404

from .models import (
    UploadSession, Shipment, Address, Package,
    ShippingServiceSelection, SavedAddress, SavedPackage
)
from .serializers import (
    UploadSessionSerializer, UploadSessionDetailSerializer,
    ShipmentSerializer, ShipmentListSerializer, ShipmentCreateSerializer,
    AddressSerializer, PackageSerializer, ShippingServiceSelectionSerializer,
    SavedAddressSerializer, SavedPackageSerializer,
    PurchaseConfirmationSerializer, BulkUpdateAddressSerializer,
    BulkUpdatePackageSerializer, BulkUpdateShippingServiceSerializer,
    BulkDeleteSerializer
)
from .services import CSVParserService, AddressValidatorService, ShippingCalculatorService
from .exceptions import (
    CSVParsingException, SessionLockedException,
    InvalidShippingServiceException, PurchaseException
)
from .constants import UploadSessionStatus, AddressType, ServiceType

logger = logging.getLogger(__name__)


class UploadSessionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing upload sessions.

    Endpoints:
    - GET /api/sessions/ - List all sessions
    - POST /api/sessions/ - Create new session
    - GET /api/sessions/{id}/ - Get session details
    - PUT/PATCH /api/sessions/{id}/ - Update session
    - DELETE /api/sessions/{id}/ - Delete session
    - POST /api/sessions/{id}/upload_csv/ - Upload CSV file
    - POST /api/sessions/{id}/purchase/ - Confirm purchase
    - GET /api/sessions/{id}/summary/ - Get session summary
    """
    queryset = UploadSession.objects.all().order_by('-created_at')
    serializer_class = UploadSessionSerializer

    def get_serializer_class(self):
        """Use detailed serializer for retrieve action."""
        if self.action == 'retrieve':
            return UploadSessionDetailSerializer
        return UploadSessionSerializer

    def perform_destroy(self, instance):
        """Prevent deletion of locked sessions."""
        if instance.is_locked:
            raise SessionLockedException(
                "Cannot delete a purchased session",
                errors={'session': 'This session has been purchased and cannot be deleted'}
            )
        logger.info(
            f"Deleting session {instance.id}",
            extra={'session_id': str(instance.id)}
        )
        instance.delete()

    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload_csv(self, request, pk=None):
        """
        Upload and parse CSV file to create shipments.

        Expected CSV format: 2 header rows + 23 columns (see CSV_HEADER_ROWS constant)
        """
        session = self.get_object()

        logger.info(
            f"CSV upload initiated for session {session.id}",
            extra={'session_id': str(session.id)}
        )

        # Check if session is locked
        if session.is_locked:
            logger.warning(
                f"Attempted to upload CSV to locked session {session.id}",
                extra={'session_id': str(session.id)}
            )
            raise SessionLockedException()

        # Get uploaded file
        csv_file = request.FILES.get('file')
        if not csv_file:
            logger.warning("No file provided in upload request")
            return Response(
                {'error': 'No file provided', 'details': {'file': 'This field is required'}},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate file type
        if not csv_file.name.endswith('.csv'):
            logger.warning(f"Invalid file type: {csv_file.name}")
            return Response(
                {'error': 'Invalid file type', 'details': {'file': 'Only CSV files are allowed'}},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Reject HTML files (e.g. user uploaded wrong file or got HTML from failed template download)
        try:
            csv_file.seek(0)
            sample = csv_file.read(200).decode('utf-8', errors='ignore').strip()
            csv_file.seek(0)
            if sample.startswith('<') or '<!DOCTYPE' in sample or '<html' in sample.lower():
                logger.warning("Uploaded file appears to be HTML, not CSV")
                return Response(
                    {'error': 'Invalid file content', 'details': {'file': 'File appears to be HTML. Please upload the actual Template.csv file.'}},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Exception:
            pass  # If we can't read, let parser handle it

        try:
            # Parse CSV
            parser = CSVParserService()
            result = parser.parse_csv_file(csv_file, session)

            # Validate all addresses
            logger.info(f"Validating addresses for session {session.id}")
            validator = AddressValidatorService()

            for shipment in session.shipments.all():
                validator.validate_shipment_addresses(shipment)

            # Assign shipping services
            logger.info(f"Assigning shipping services for session {session.id}")
            calculator = ShippingCalculatorService()

            for shipment in session.shipments.all():
                if not hasattr(shipment, 'shipping_service'):
                    calculator.assign_default_service(shipment)

            # Update session status
            session.status = UploadSessionStatus.IN_REVIEW
            session.save()

            logger.info(
                f"CSV processing completed for session {session.id}",
                extra={
                    'session_id': str(session.id),
                    'shipments_created': result['shipments_created']
                }
            )

            return Response({
                'message': 'CSV uploaded and processed successfully',
                'result': result,
                'session': UploadSessionDetailSerializer(session).data
            }, status=status.HTTP_201_CREATED)

        except CSVParsingException as e:
            logger.error(
                f"CSV parsing failed for session {session.id}: {str(e)}",
                extra={'session_id': str(session.id), 'error': str(e)}
            )
            raise

    @action(detail=True, methods=['post'])
    def purchase(self, request, pk=None):
        """
        Confirm purchase and lock the session.

        Required fields:
        - label_size: 'letter' or '4x6'
        - terms_accepted: true
        """
        session = self.get_object()

        logger.info(
            f"Purchase initiated for session {session.id}",
            extra={'session_id': str(session.id)}
        )

        # Check if already locked
        if session.is_locked:
            logger.warning(
                f"Attempted to purchase already locked session {session.id}",
                extra={'session_id': str(session.id)}
            )
            raise PurchaseException(
                "Session already purchased",
                errors={'session': 'This session has already been purchased'}
            )

        # Validate request data
        serializer = PurchaseConfirmationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Validate session has shipments
        if session.total_shipments == 0:
            raise PurchaseException(
                "Cannot purchase empty session",
                errors={'session': 'Session must contain at least one shipment'}
            )

        # Check for errors
        if session.error_shipments > 0:
            raise PurchaseException(
                f"Cannot purchase session with {session.error_shipments} error(s)",
                errors={'session': 'All shipments must be valid or have warnings only'}
            )

        # Update session
        session.label_size = serializer.validated_data['label_size']
        session.terms_accepted = serializer.validated_data['terms_accepted']
        session.lock()

        logger.info(
            f"Purchase confirmed for session {session.id}",
            extra={
                'session_id': str(session.id),
                'total_shipments': session.total_shipments,
                'label_size': session.label_size
            }
        )

        return Response({
            'message': 'Purchase confirmed successfully',
            'session': UploadSessionSerializer(session).data
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def summary(self, request, pk=None):
        """
        Get session summary including statistics and total price.
        """
        session = self.get_object()

        calculator = ShippingCalculatorService()
        total_price = calculator.calculate_session_total(session)

        return Response({
            'session_id': str(session.id),
            'status': session.status,
            'total_shipments': session.total_shipments,
            'valid_shipments': session.valid_shipments,
            'warning_shipments': session.warning_shipments,
            'error_shipments': session.error_shipments,
            'total_price': str(total_price),
            'is_locked': session.is_locked,
            'can_purchase': session.error_shipments == 0 and session.total_shipments > 0
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def download_labels(self, request, pk=None):
        """
        Download shipping labels for a purchased session as a PDF.
        Each label is formatted in a table on a separate page.
        """
        from django.http import HttpResponse
        from datetime import datetime
        from io import BytesIO
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer, PageBreak

        session = self.get_object()

        logger.info(
            f"Label download initiated for session {session.id}",
            extra={'session_id': str(session.id)}
        )

        # Check if session is locked (purchased)
        if not session.is_locked:
            return Response({
                'error': 'Labels can only be downloaded after purchase is confirmed'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get all shipments for this session
        shipments = session.shipments.all().select_related(
            'package', 'shipping_service'
        ).prefetch_related('addresses')

        # Create PDF in memory
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            topMargin=0.5*inch,
            bottomMargin=0.5*inch,
            leftMargin=0.75*inch,
            rightMargin=0.75*inch
        )
        elements = []

        # Title page data
        title_data = [[f'Shipping Labels - Session {str(session.id)[:8]}']]
        title_table = Table(title_data, colWidths=[7*inch])
        title_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 18),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1e40af')),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ]))
        elements.append(title_table)

        # Summary info
        summary_data = [
            [f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'],
            [f'Total Labels: {shipments.count()}'],
        ]
        summary_table = Table(summary_data, colWidths=[7*inch])
        summary_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.grey),
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 0.3*inch))

        # Generate a label for each shipment
        for idx, shipment in enumerate(shipments, 1):
            ship_from = shipment.addresses.filter(address_type='ship_from').first()
            ship_to = shipment.addresses.filter(address_type='ship_to').first()
            pkg = shipment.package
            svc = shipment.shipping_service

            # Build address strings
            from_addr = []
            if ship_from:
                from_addr.append(ship_from.name or 'N/A')
                from_addr.append(ship_from.street1 or '')
                if ship_from.street2:
                    from_addr.append(ship_from.street2)
                from_addr.append(f"{ship_from.city or ''}, {ship_from.state or ''} {ship_from.zip_code or ''}")
            else:
                from_addr = ['N/A']

            to_addr = []
            if ship_to:
                to_addr.append(ship_to.name or 'N/A')
                to_addr.append(ship_to.street1 or '')
                if ship_to.street2:
                    to_addr.append(ship_to.street2)
                to_addr.append(f"{ship_to.city or ''}, {ship_to.state or ''} {ship_to.zip_code or ''}")
            else:
                to_addr = ['N/A']

            # Label header
            header_data = [[f"Label #{idx} - Reference: {shipment.reference_number or 'N/A'}"]]
            header_table = Table(header_data, colWidths=[7*inch])
            header_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 14),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1e40af')),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))
            elements.append(header_table)

            # Tracking number
            tracking = f'TRACK-{str(shipment.id)[:8].upper()}'
            tracking_data = [[f'Tracking Number: {tracking}']]
            tracking_table = Table(tracking_data, colWidths=[7*inch])
            tracking_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ]))
            elements.append(tracking_table)

            # Address table
            addr_data = [
                ['SHIP FROM', 'SHIP TO'],
                ['\n'.join(from_addr), '\n'.join(to_addr)]
            ]
            addr_table = Table(addr_data, colWidths=[3.5*inch, 3.5*inch])
            addr_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#dbeafe')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('FONTSIZE', (0, 1), (-1, 1), 9),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#94a3b8')),
                ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#1e40af')),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                ('TOPPADDING', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('TOPPADDING', (0, 1), (-1, 1), 12),
                ('BOTTOMPADDING', (0, 1), (-1, 1), 12),
            ]))
            elements.append(addr_table)
            elements.append(Spacer(1, 0.15*inch))

            # Package and service details
            pkg_info = f"Weight: {pkg.weight if pkg else '0'} oz\nDimensions: {pkg.length if pkg else '0'} x {pkg.width if pkg else '0'} x {pkg.height if pkg else '0'} in"
            svc_info = f"Service: {svc.get_service_type_display() if svc else 'N/A'}\nPrice: ${svc.price if svc else '0.00'}"

            details_data = [
                ['Package Details', 'Shipping Service'],
                [pkg_info, svc_info]
            ]
            details_table = Table(details_data, colWidths=[3.5*inch, 3.5*inch])
            details_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f1f5f9')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#334155')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('FONTSIZE', (0, 1), (-1, 1), 9),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e1')),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))
            elements.append(details_table)

            # Add page break between labels (except for the last one)
            if idx < shipments.count():
                elements.append(PageBreak())

        # Build PDF
        doc.build(elements)

        # Get PDF data
        pdf_data = buffer.getvalue()
        buffer.close()

        # Create response
        response = HttpResponse(pdf_data, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="shipping-labels-{session.id}.pdf"'

        logger.info(
            f"Labels downloaded successfully for session {session.id}",
            extra={
                'session_id': str(session.id),
                'label_count': shipments.count()
            }
        )

        return response


class ShipmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing shipments.

    Endpoints:
    - GET /api/shipments/ - List shipments (filterable by session)
    - POST /api/shipments/ - Create new shipment
    - GET /api/shipments/{id}/ - Get shipment details
    - PUT/PATCH /api/shipments/{id}/ - Update shipment
    - DELETE /api/shipments/{id}/ - Delete shipment
    - POST /api/shipments/bulk_delete/ - Delete multiple shipments
    - POST /api/shipments/bulk_update_address/ - Bulk update ship-from address
    - POST /api/shipments/bulk_update_package/ - Bulk update package
    - POST /api/shipments/bulk_update_service/ - Bulk update shipping service
    """
    queryset = Shipment.objects.all().select_related(
        'upload_session', 'package', 'shipping_service'
    ).prefetch_related('addresses')

    def get_serializer_class(self):
        """Use appropriate serializer based on action."""
        if self.action == 'list':
            return ShipmentListSerializer
        elif self.action == 'create':
            return ShipmentCreateSerializer
        return ShipmentSerializer

    def get_queryset(self):
        """Filter by session if provided."""
        queryset = super().get_queryset()
        session_id = self.request.query_params.get('session')

        if session_id:
            queryset = queryset.filter(upload_session_id=session_id)

        return queryset.order_by('csv_row_number', 'created_at')

    def perform_update(self, serializer):
        """Check if shipment can be edited before updating."""
        shipment = self.get_object()

        if not shipment.can_edit():
            raise SessionLockedException(
                "Cannot edit shipment in a locked session",
                errors={'shipment': 'This shipment belongs to a purchased session'}
            )

        serializer.save()

    def perform_destroy(self, instance):
        """Check if shipment can be deleted."""
        if not instance.can_edit():
            raise SessionLockedException()

        logger.info(
            f"Deleting shipment {instance.id}",
            extra={'shipment_id': str(instance.id)}
        )

        session = instance.upload_session
        instance.delete()

        # Update session counts
        if session:
            session.update_counts()

    @action(detail=False, methods=['post'])
    def bulk_delete(self, request):
        """Delete multiple shipments."""
        serializer = BulkDeleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        shipment_ids = serializer.validated_data['shipment_ids']

        logger.info(
            f"Bulk deleting {len(shipment_ids)} shipments",
            extra={'shipment_count': len(shipment_ids)}
        )

        with transaction.atomic():
            shipments = Shipment.objects.filter(id__in=shipment_ids)

            # Check if all can be deleted
            locked_sessions = set()
            for shipment in shipments:
                if not shipment.can_edit():
                    locked_sessions.add(str(shipment.upload_session_id))

            if locked_sessions:
                raise SessionLockedException(
                    f"Some shipments belong to locked sessions",
                    errors={'sessions': list(locked_sessions)}
                )

            # Track sessions to update
            sessions = set(s.upload_session for s in shipments if s.upload_session)

            # Delete shipments
            deleted_count = shipments.delete()[0]

            # Update session counts
            for session in sessions:
                session.update_counts()

        logger.info(
            f"Bulk deleted {deleted_count} shipments",
            extra={'deleted_count': deleted_count}
        )

        return Response({
            'message': f'Deleted {deleted_count} shipments',
            'deleted_count': deleted_count
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def bulk_update_address(self, request):
        """Bulk update ship-from address using saved address."""
        serializer = BulkUpdateAddressSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        shipment_ids = serializer.validated_data['shipment_ids']
        saved_address_id = serializer.validated_data['saved_address_id']

        logger.info(
            f"Bulk updating address for {len(shipment_ids)} shipments",
            extra={'shipment_count': len(shipment_ids), 'saved_address_id': str(saved_address_id)}
        )

        # Get saved address
        saved_address = get_object_or_404(SavedAddress, id=saved_address_id)

        with transaction.atomic():
            shipments = Shipment.objects.filter(id__in=shipment_ids)

            # Check if all can be edited
            for shipment in shipments:
                if not shipment.can_edit():
                    raise SessionLockedException()

            validator = AddressValidatorService()
            updated_count = 0

            for shipment in shipments:
                # Update ship-from address
                ship_from = shipment.addresses.get(address_type=AddressType.SHIP_FROM)
                ship_from.name = saved_address.name
                ship_from.company = saved_address.company
                ship_from.street1 = saved_address.street1
                ship_from.street2 = saved_address.street2
                ship_from.city = saved_address.city
                ship_from.state = saved_address.state
                ship_from.zip_code = saved_address.zip_code
                ship_from.country = saved_address.country
                ship_from.phone = saved_address.phone
                ship_from.email = saved_address.email
                ship_from.save()

                # Revalidate
                validator.validate_address(ship_from)
                shipment.update_status_from_addresses()

                updated_count += 1

        logger.info(
            f"Bulk updated {updated_count} shipments",
            extra={'updated_count': updated_count}
        )

        return Response({
            'message': f'Updated {updated_count} shipments',
            'updated_count': updated_count
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def bulk_update_package(self, request):
        """Bulk update package using saved package preset."""
        serializer = BulkUpdatePackageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        shipment_ids = serializer.validated_data['shipment_ids']
        saved_package_id = serializer.validated_data['saved_package_id']

        logger.info(
            f"Bulk updating package for {len(shipment_ids)} shipments",
            extra={'shipment_count': len(shipment_ids), 'saved_package_id': str(saved_package_id)}
        )

        # Get saved package
        saved_package = get_object_or_404(SavedPackage, id=saved_package_id)

        with transaction.atomic():
            shipments = Shipment.objects.filter(id__in=shipment_ids)

            # Check if all can be edited
            for shipment in shipments:
                if not shipment.can_edit():
                    raise SessionLockedException()

            calculator = ShippingCalculatorService()
            updated_count = 0

            for shipment in shipments:
                # Update package
                package = shipment.package
                package.length = saved_package.length
                package.width = saved_package.width
                package.height = saved_package.height
                package.weight = saved_package.weight
                package.package_type = saved_package.package_type
                package.save()

                # Recalculate shipping service
                calculator.recalculate_service_after_weight_change(shipment)

                updated_count += 1

        logger.info(
            f"Bulk updated {updated_count} packages",
            extra={'updated_count': updated_count}
        )

        return Response({
            'message': f'Updated {updated_count} packages',
            'updated_count': updated_count
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def bulk_update_service(self, request):
        """Bulk update shipping service."""
        serializer = BulkUpdateShippingServiceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        shipment_ids = serializer.validated_data['shipment_ids']
        service_type = serializer.validated_data['service_type']

        logger.info(
            f"Bulk updating shipping service for {len(shipment_ids)} shipments",
            extra={'shipment_count': len(shipment_ids), 'service_type': service_type}
        )

        with transaction.atomic():
            shipments = Shipment.objects.filter(id__in=shipment_ids)

            # Check if all can be edited
            for shipment in shipments:
                if not shipment.can_edit():
                    raise SessionLockedException()

            calculator = ShippingCalculatorService()
            updated_count = 0
            errors = []

            for shipment in shipments:
                try:
                    # most_affordable = pick cheapest (Ground if <16oz, else Priority)
                    effective_type = service_type
                    if service_type == 'most_affordable':
                        weight_oz = shipment.package.get_weight_in_ounces()
                        effective_type = (ServiceType.GROUND_SHIPPING
                                         if weight_oz < 16 else ServiceType.PRIORITY_MAIL)
                    calculator.update_shipping_service(shipment, effective_type)
                    updated_count += 1
                except InvalidShippingServiceException as e:
                    errors.append({
                        'shipment_id': str(shipment.id),
                        'error': str(e)
                    })

        logger.info(
            f"Bulk updated {updated_count} shipping services",
            extra={'updated_count': updated_count, 'errors': len(errors)}
        )

        response_data = {
            'message': f'Updated {updated_count} shipments',
            'updated_count': updated_count
        }

        if errors:
            response_data['errors'] = errors

        return Response(response_data, status=status.HTTP_200_OK)


class AddressViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing addresses.
    """
    queryset = Address.objects.all().select_related('shipment')
    serializer_class = AddressSerializer

    def perform_update(self, serializer):
        """Revalidate address after update."""
        address = serializer.save()

        # Revalidate
        validator = AddressValidatorService()
        validator.validate_address(address)

        # Update shipment status
        address.shipment.update_status_from_addresses()


class PackageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing packages.
    """
    queryset = Package.objects.all().select_related('shipment')
    serializer_class = PackageSerializer

    def perform_update(self, serializer):
        """Recalculate shipping service after package update."""
        package = serializer.save()

        # Recalculate shipping
        calculator = ShippingCalculatorService()
        calculator.recalculate_service_after_weight_change(package.shipment)


class ShippingServiceSelectionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing shipping service selections.
    """
    queryset = ShippingServiceSelection.objects.all().select_related('shipment')
    serializer_class = ShippingServiceSelectionSerializer


class SavedAddressViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing saved addresses.

    Endpoints:
    - GET /api/saved-addresses/ - List all saved addresses
    - POST /api/saved-addresses/ - Create new saved address
    - GET /api/saved-addresses/{id}/ - Get saved address details
    - PUT/PATCH /api/saved-addresses/{id}/ - Update saved address
    - DELETE /api/saved-addresses/{id}/ - Delete saved address
    """
    queryset = SavedAddress.objects.all().order_by('-is_default', 'nickname')
    serializer_class = SavedAddressSerializer


class SavedPackageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing saved packages.

    Endpoints:
    - GET /api/saved-packages/ - List all saved packages
    - POST /api/saved-packages/ - Create new saved package
    - GET /api/saved-packages/{id}/ - Get saved package details
    - PUT/PATCH /api/saved-packages/{id}/ - Update saved package
    - DELETE /api/saved-packages/{id}/ - Delete saved package
    """
    queryset = SavedPackage.objects.all().order_by('-is_default', 'nickname')
    serializer_class = SavedPackageSerializer
