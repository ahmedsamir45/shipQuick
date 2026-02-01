"""
CSV Parser Service
Handles parsing of 2-header-row CSV files for bulk shipment creation.
Supports both PRD Template.csv format and alternative format.
"""
import csv
import io
import logging
from decimal import Decimal, InvalidOperation
from django.db import transaction
from ..models import UploadSession, Shipment, Address, Package
from ..constants import AddressType, ShipmentStatus, DEFAULT_COUNTRY, CSV_HEADER_ROWS
from ..exceptions import CSVParsingException

logger = logging.getLogger(__name__)


class CSVParserService:
    """
    Service for parsing CSV files and creating shipment records.

    Supports two CSV formats (auto-detected by header):
    1. PRD Template.csv: First name, Last name, Address, Address2, City, ZIP, Abbreviation (x2)
       + lbs, oz, Length, width, Height, phone num1, phone num2, order no, Item-sku
    2. Alternative: Ship From Name, Company, Street1, Street2, City, State, ZIP, Phone, Email (x2)
       + Package Length/Width/Height/Weight, Reference Number
    """

    # PRD Template.csv format (from PRD Appendix A)
    PRD_COLUMN_MAPPING = {
        'ship_from_first_name': 0,
        'ship_from_last_name': 1,
        'ship_from_street1': 2,
        'ship_from_street2': 3,
        'ship_from_city': 4,
        'ship_from_zip': 5,
        'ship_from_state': 6,
        'ship_to_first_name': 7,
        'ship_to_last_name': 8,
        'ship_to_street1': 9,
        'ship_to_street2': 10,
        'ship_to_city': 11,
        'ship_to_zip': 12,
        'ship_to_state': 13,
        'package_weight_lbs': 14,
        'package_weight_oz': 15,
        'package_length': 16,
        'package_width': 17,
        'package_height': 18,
        'phone_num1': 19,
        'phone_num2': 20,
        'reference_number': 21,
        'item_sku': 22,
    }

    # Alternative format (Sample_Upload.csv style)
    ALT_COLUMN_MAPPING = {
        'ship_from_name': 0,
        'ship_from_company': 1,
        'ship_from_street1': 2,
        'ship_from_street2': 3,
        'ship_from_city': 4,
        'ship_from_state': 5,
        'ship_from_zip': 6,
        'ship_from_phone': 7,
        'ship_from_email': 8,
        'ship_to_name': 9,
        'ship_to_company': 10,
        'ship_to_street1': 11,
        'ship_to_street2': 12,
        'ship_to_city': 13,
        'ship_to_state': 14,
        'ship_to_zip': 15,
        'ship_to_phone': 16,
        'ship_to_email': 17,
        'package_length': 18,
        'package_width': 19,
        'package_height': 20,
        'package_weight': 21,
        'reference_number': 22,
    }

    # Ship To is required for a valid label; Ship From can be filled via bulk update
    PRD_REQUIRED_FIELDS = [
        'ship_to_first_name', 'ship_to_street1', 'ship_to_city',
        'ship_to_state', 'ship_to_zip',
        'package_length', 'package_width', 'package_height'
    ]
    ALT_REQUIRED_FIELDS = [
        'ship_to_name', 'ship_to_street1', 'ship_to_city',
        'ship_to_state', 'ship_to_zip',
        'package_length', 'package_width', 'package_height'
    ]

    def __init__(self):
        self.errors = []
        self.warnings = []

    def parse_csv_file(self, file_obj, upload_session):
        """
        Parse CSV file and create shipment records.

        Args:
            file_obj: Uploaded file object
            upload_session: UploadSession instance to attach shipments to

        Returns:
            dict: Parsing results with statistics

        Raises:
            CSVParsingException: If parsing fails critically
        """
        logger.info(
            f"Starting CSV parsing for session {upload_session.id}",
            extra={'session_id': str(upload_session.id)}
        )

        try:
            # Read file content
            file_content = file_obj.read()

            # Try to decode as UTF-8
            try:
                content = file_content.decode('utf-8')
            except UnicodeDecodeError:
                # Try UTF-8-BOM or ISO-8859-1
                try:
                    content = file_content.decode('utf-8-sig')
                except UnicodeDecodeError:
                    content = file_content.decode('iso-8859-1')

            # Parse CSV
            csv_reader = csv.reader(io.StringIO(content))
            rows = list(csv_reader)

            # Detect format from header (row 2, index 1)
            if len(rows) < CSV_HEADER_ROWS:
                raise CSVParsingException(
                    "CSV file is empty or has insufficient header rows",
                    errors={'file': 'Invalid CSV format'}
                )

            header_row = rows[CSV_HEADER_ROWS - 1] if len(rows[CSV_HEADER_ROWS - 1]) > 1 else rows[0]
            use_prd_format = self._detect_prd_format(header_row)
            self.COLUMN_MAPPING = self.PRD_COLUMN_MAPPING if use_prd_format else self.ALT_COLUMN_MAPPING
            self.REQUIRED_FIELDS = self.PRD_REQUIRED_FIELDS if use_prd_format else self.ALT_REQUIRED_FIELDS

            logger.info(
                f"CSV format detected: {'PRD Template' if use_prd_format else 'Alternative'}",
                extra={'session_id': str(upload_session.id)}
            )

            # Parse data rows (skip header rows)
            data_rows = rows[CSV_HEADER_ROWS:]
            shipments_created = []
            row_number = CSV_HEADER_ROWS + 1

            with transaction.atomic():
                for row in data_rows:
                    try:
                        shipment = self._parse_row(row, row_number, upload_session)
                        if shipment:
                            shipments_created.append(shipment)

                        logger.debug(
                            f"Parsed row {row_number}",
                            extra={'row_number': row_number, 'shipment_id': str(shipment.id) if shipment else None}
                        )

                    except Exception as e:
                        error_msg = f"Row {row_number}: {str(e)}"
                        self.errors.append(error_msg)
                        logger.warning(
                            f"Error parsing row {row_number}: {str(e)}",
                            extra={'row_number': row_number, 'error': str(e)}
                        )

                    row_number += 1

                # Update session counts
                upload_session.update_counts()

            logger.info(
                f"CSV parsing completed for session {upload_session.id}",
                extra={
                    'session_id': str(upload_session.id),
                    'shipments_created': len(shipments_created),
                    'errors': len(self.errors),
                    'warnings': len(self.warnings)
                }
            )

            return {
                'success': True,
                'shipments_created': len(shipments_created),
                'total_rows': row_number - CSV_HEADER_ROWS - 1,
                'errors': self.errors,
                'warnings': self.warnings,
                'session_id': str(upload_session.id)
            }

        except CSVParsingException:
            raise
        except Exception as e:
            logger.exception(
                f"Critical error parsing CSV for session {upload_session.id}",
                extra={'session_id': str(upload_session.id), 'error': str(e)}
            )
            raise CSVParsingException(
                f"Failed to parse CSV file: {str(e)}",
                errors={'file': str(e)}
            )

    def _parse_row(self, row, row_number, upload_session):
        """
        Parse a single CSV row and create shipment with related objects.

        Args:
            row: CSV row data
            row_number: Row number for tracking
            upload_session: Parent UploadSession

        Returns:
            Shipment instance or None if row is empty
        """
        # Skip empty rows
        if not row or all(not cell.strip() for cell in row):
            logger.debug(f"Skipping empty row {row_number}")
            return None

        # Validate row length
        expected_cols = 23
        if len(row) < expected_cols:
            self.warnings.append(
                f"Row {row_number}: Insufficient columns ({len(row)} found, {expected_cols} expected)"
            )
            row.extend([''] * (expected_cols - len(row)))

        # Extract and normalize data based on format
        data = self._extract_and_normalize_row_data(row)

        # Validate required fields (ship_to required; package weight defaults if missing)
        validation_messages = []
        missing_fields = []

        for field in self.REQUIRED_FIELDS:
            if not data.get(field):
                missing_fields.append(field.replace('_', ' ').title())

        if missing_fields:
            validation_messages.append({
                'message': f"Missing required fields: {', '.join(missing_fields)}",
                'severity': 'error'
            })

        # Create shipment
        shipment = Shipment.objects.create(
            upload_session=upload_session,
            csv_row_number=row_number,
            status=ShipmentStatus.ERROR if missing_fields else ShipmentStatus.VALID,
            validation_messages=validation_messages,
            reference_number=data.get('reference_number', '')
        )

        # Create Ship From address (can be empty - user fills via bulk)
        try:
            Address.objects.create(
                shipment=shipment,
                address_type=AddressType.SHIP_FROM,
                name=data.get('ship_from_name', '') or 'TBD',
                company=data.get('ship_from_company', ''),
                street1=data.get('ship_from_street1', '') or 'TBD',
                street2=data.get('ship_from_street2', ''),
                city=data.get('ship_from_city', '') or 'TBD',
                state=(data.get('ship_from_state', '') or 'NA')[:2],
                zip_code=data.get('ship_from_zip', '') or '00000',
                country=DEFAULT_COUNTRY,
                phone=data.get('ship_from_phone', ''),
                email=data.get('ship_from_email', '')
            ).save_original()
        except Exception as e:
            logger.error(f"Error creating ship_from address for row {row_number}: {e}")
            raise

        # Create Ship To address
        try:
            Address.objects.create(
                shipment=shipment,
                address_type=AddressType.SHIP_TO,
                name=data.get('ship_to_name', ''),
                company=data.get('ship_to_company', ''),
                street1=data.get('ship_to_street1', ''),
                street2=data.get('ship_to_street2', ''),
                city=data.get('ship_to_city', ''),
                state=data.get('ship_to_state', ''),
                zip_code=data.get('ship_to_zip', ''),
                country=DEFAULT_COUNTRY,
                phone=data.get('ship_to_phone', ''),
                email=data.get('ship_to_email', '')
            ).save_original()
        except Exception as e:
            logger.error(f"Error creating ship_to address for row {row_number}: {e}")
            raise

        # Create Package
        try:
            package_data = self._parse_package_data(data, row_number)
            Package.objects.create(
                shipment=shipment,
                **package_data
            )
        except Exception as e:
            logger.error(f"Error creating package for row {row_number}: {e}")
            raise

        return shipment

    def _detect_prd_format(self, header_row):
        """Detect if CSV uses PRD Template format (First name, Last name) vs alternative."""
        if len(header_row) < 2:
            return False
        col0 = (header_row[0] or '').strip().lower()
        col1 = (header_row[1] or '').strip().lower()
        return 'first name' in col0 or 'last name' in col1

    def _extract_and_normalize_row_data(self, row):
        """Extract data and normalize to common structure for both formats."""
        data = {}
        for field, index in self.COLUMN_MAPPING.items():
            value = (row[index] or '').strip() if index < len(row) else ''
            data[field] = value

        # Normalize PRD format to common structure
        if 'ship_from_first_name' in data:
            data['ship_from_name'] = f"{data['ship_from_first_name']} {data['ship_from_last_name']}".strip()
            data['ship_to_name'] = f"{data['ship_to_first_name']} {data['ship_to_last_name']}".strip()
            data['ship_to_phone'] = data.get('phone_num1', '') or data.get('phone_num2', '')
        elif 'ship_from_name' in data:
            pass  # Already in common format

        # Normalize package weight (PRD has lbs + oz, computed in _parse_package_data)
        # No need to set package_weight here - _parse_package_data handles both formats

        return data

    def _parse_package_data(self, data, row_number):
        """
        Parse and validate package dimensions and weight.
        Handles PRD format (lbs+oz) and alternative format (weight in oz).
        """
        package_data = {
            'package_type': 'box',
            'weight_unit': 'oz'
        }

        # Handle weight: PRD has lbs + oz, alternative has package_weight (oz)
        weight_str = data.get('package_weight', '0')
        if not weight_str and 'package_weight_lbs' in data:
            lbs = Decimal(data.get('package_weight_lbs', '0') or '0')
            oz = Decimal(data.get('package_weight_oz', '0') or '0')
            weight_str = str(float(lbs * 16 + oz))

        for field in ['length', 'width', 'height']:
            value_str = data.get(f'package_{field}', '0') or '0'
            try:
                value = Decimal(value_str.replace(',', ''))
                if value <= 0:
                    value = Decimal('1.0')
                package_data[field] = value
            except (InvalidOperation, ValueError):
                self.warnings.append(f"Row {row_number}: Invalid {field}, using default")
                package_data[field] = Decimal('1.0')

        try:
            weight = Decimal(weight_str.replace(',', ''))
            if weight <= 0:
                weight = Decimal('1.0')  # PRD: default to lowest tier
            package_data['weight'] = weight
        except (InvalidOperation, ValueError):
            self.warnings.append(f"Row {row_number}: Invalid weight, using 1 oz default")
            package_data['weight'] = Decimal('1.0')

        return package_data
