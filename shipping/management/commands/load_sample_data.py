"""
Management command to load sample data for saved addresses and packages.

Usage:
    python manage.py load_sample_data
"""
from django.core.management.base import BaseCommand
from decimal import Decimal
from shipping.models import SavedAddress, SavedPackage


class Command(BaseCommand):
    help = 'Load sample saved addresses and packages for demo purposes'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Loading sample data...'))

        # Clear existing data
        SavedAddress.objects.all().delete()
        SavedPackage.objects.all().delete()

        # Create saved addresses
        addresses = [
            {
                'nickname': 'Main Warehouse',
                'name': 'John Smith',
                'company': 'ACME Corporation',
                'street1': '123 Industrial Blvd',
                'street2': 'Suite 100',
                'city': 'Los Angeles',
                'state': 'CA',
                'zip_code': '90001',
                'country': 'US',
                'phone': '555-0100',
                'email': 'warehouse@acme.com',
                'is_default': True
            },
            {
                'nickname': 'East Coast Distribution',
                'name': 'Jane Doe',
                'company': 'ACME Distribution',
                'street1': '456 Commerce St',
                'street2': '',
                'city': 'New York',
                'state': 'NY',
                'zip_code': '10001',
                'country': 'US',
                'phone': '555-0200',
                'email': 'eastcoast@acme.com',
                'is_default': False
            },
            {
                'nickname': 'Chicago Office',
                'name': 'Bob Johnson',
                'company': 'ACME Midwest',
                'street1': '789 Michigan Ave',
                'street2': 'Floor 3',
                'city': 'Chicago',
                'state': 'IL',
                'zip_code': '60601',
                'country': 'US',
                'phone': '555-0300',
                'email': 'chicago@acme.com',
                'is_default': False
            },
            {
                'nickname': 'Texas Hub',
                'name': 'Sarah Williams',
                'company': 'ACME Texas',
                'street1': '321 Lone Star Dr',
                'street2': '',
                'city': 'Houston',
                'state': 'TX',
                'zip_code': '77001',
                'country': 'US',
                'phone': '555-0400',
                'email': 'texas@acme.com',
                'is_default': False
            }
        ]

        for address_data in addresses:
            address = SavedAddress.objects.create(**address_data)
            self.stdout.write(
                self.style.SUCCESS(f'  ✓ Created saved address: {address.nickname}')
            )

        # Create saved packages
        packages = [
            {
                'nickname': 'Small Envelope',
                'length': Decimal('9.0'),
                'width': Decimal('6.0'),
                'height': Decimal('0.25'),
                'weight': Decimal('2.0'),
                'package_type': 'envelope',
                'is_default': True
            },
            {
                'nickname': 'Medium Box',
                'length': Decimal('12.0'),
                'width': Decimal('9.0'),
                'height': Decimal('6.0'),
                'weight': Decimal('8.0'),
                'package_type': 'box',
                'is_default': False
            },
            {
                'nickname': 'Large Box',
                'length': Decimal('18.0'),
                'width': Decimal('14.0'),
                'height': Decimal('10.0'),
                'weight': Decimal('20.0'),
                'package_type': 'box',
                'is_default': False
            },
            {
                'nickname': 'Flat Rate Envelope',
                'length': Decimal('12.5'),
                'width': Decimal('9.5'),
                'height': Decimal('0.5'),
                'weight': Decimal('3.5'),
                'package_type': 'envelope',
                'is_default': False
            },
            {
                'nickname': 'Tube Package',
                'length': Decimal('24.0'),
                'width': Decimal('3.0'),
                'height': Decimal('3.0'),
                'weight': Decimal('6.0'),
                'package_type': 'tube',
                'is_default': False
            },
            {
                'nickname': 'Extra Small Box',
                'length': Decimal('6.0'),
                'width': Decimal('4.0'),
                'height': Decimal('2.0'),
                'weight': Decimal('1.5'),
                'package_type': 'box',
                'is_default': False
            }
        ]

        for package_data in packages:
            package = SavedPackage.objects.create(**package_data)
            self.stdout.write(
                self.style.SUCCESS(f'  ✓ Created saved package: {package.nickname}')
            )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nSuccessfully loaded {len(addresses)} saved addresses and {len(packages)} saved packages!'
            )
        )
