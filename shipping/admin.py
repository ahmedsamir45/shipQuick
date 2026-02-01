"""
Django Admin configuration for shipping models.
Provides a user-friendly interface for managing data.
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import (
    UploadSession, Shipment, Address, Package,
    ShippingServiceSelection, SavedAddress, SavedPackage
)


@admin.register(UploadSession)
class UploadSessionAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'status', 'total_shipments', 'valid_shipments',
        'warning_shipments', 'error_shipments', 'is_locked',
        'created_at', 'purchase_date'
    ]
    list_filter = ['status', 'is_locked', 'created_at']
    search_fields = ['id']
    readonly_fields = ['id', 'created_at', 'updated_at', 'purchase_date']
    fieldsets = (
        ('Session Info', {
            'fields': ('id', 'status', 'is_locked', 'terms_accepted')
        }),
        ('Shipment Counts', {
            'fields': ('total_shipments', 'valid_shipments', 'warning_shipments', 'error_shipments')
        }),
        ('Purchase Details', {
            'fields': ('label_size', 'purchase_date')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of locked sessions"""
        if obj and obj.is_locked:
            return False
        return super().has_delete_permission(request, obj)


class AddressInline(admin.TabularInline):
    model = Address
    extra = 0
    fields = ['address_type', 'name', 'street1', 'city', 'state', 'zip_code', 'validation_status']
    readonly_fields = ['validation_status']


class PackageInline(admin.StackedInline):
    model = Package
    extra = 0
    fields = ['length', 'width', 'height', 'weight', 'weight_unit', 'package_type']


class ShippingServiceInline(admin.StackedInline):
    model = ShippingServiceSelection
    extra = 0
    fields = ['service_type', 'service_tier', 'price', 'auto_selected']
    readonly_fields = ['auto_selected']


@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'upload_session', 'csv_row_number', 'status',
        'address_validation_provider', 'created_at'
    ]
    list_filter = ['status', 'address_validation_provider', 'created_at']
    search_fields = ['id', 'reference_number']
    readonly_fields = ['id', 'created_at', 'updated_at', 'validation_messages']
    inlines = [AddressInline, PackageInline, ShippingServiceInline]

    fieldsets = (
        ('Shipment Info', {
            'fields': ('id', 'upload_session', 'csv_row_number', 'status', 'reference_number')
        }),
        ('Validation', {
            'fields': ('address_validation_provider', 'validation_messages')
        }),
        ('Customs (International)', {
            'fields': ('customs_description', 'customs_value'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('upload_session')


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'shipment', 'address_type', 'name', 'city',
        'state', 'validation_status_badge', 'validated_by_provider'
    ]
    list_filter = ['address_type', 'validation_status', 'validated_by_provider', 'state']
    search_fields = ['name', 'city', 'zip_code']
    readonly_fields = [
        'id', 'created_at', 'updated_at', 'validated_at',
        'original_input', 'normalized_address'
    ]

    fieldsets = (
        ('Address Info', {
            'fields': ('id', 'shipment', 'address_type')
        }),
        ('Contact', {
            'fields': ('name', 'company', 'phone', 'email')
        }),
        ('Location', {
            'fields': ('street1', 'street2', 'city', 'state', 'zip_code', 'country')
        }),
        ('Validation', {
            'fields': (
                'is_validated', 'validation_status', 'validation_error',
                'validated_by_provider', 'validated_at'
            )
        }),
        ('Validation Data', {
            'fields': ('original_input', 'normalized_address'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def validation_status_badge(self, obj):
        """Display validation status with color coding"""
        colors = {
            'valid': 'green',
            'pending': 'orange',
            'invalid': 'red',
            'fallback_valid': 'blue'
        }
        color = colors.get(obj.validation_status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_validation_status_display()
        )
    validation_status_badge.short_description = 'Validation Status'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('shipment')


@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'shipment', 'package_type', 'weight', 'weight_unit',
        'dimensions', 'created_at'
    ]
    list_filter = ['package_type', 'weight_unit']
    search_fields = ['shipment__id']
    readonly_fields = ['id', 'created_at', 'updated_at']

    def dimensions(self, obj):
        return f"{obj.length} × {obj.width} × {obj.height} in"
    dimensions.short_description = 'Dimensions (L×W×H)'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('shipment')


@admin.register(ShippingServiceSelection)
class ShippingServiceSelectionAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'shipment', 'service_type', 'service_tier',
        'price_display', 'auto_selected', 'created_at'
    ]
    list_filter = ['service_type', 'service_tier', 'auto_selected']
    search_fields = ['shipment__id']
    readonly_fields = ['id', 'created_at', 'updated_at']

    def price_display(self, obj):
        return f"${obj.price} {obj.currency}"
    price_display.short_description = 'Price'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('shipment')


@admin.register(SavedAddress)
class SavedAddressAdmin(admin.ModelAdmin):
    list_display = [
        'nickname', 'name', 'city', 'state', 'is_default', 'created_at'
    ]
    list_filter = ['is_default', 'state']
    search_fields = ['nickname', 'name', 'city']
    readonly_fields = ['id', 'created_at', 'updated_at']

    fieldsets = (
        ('Preset Info', {
            'fields': ('id', 'nickname', 'is_default')
        }),
        ('Contact', {
            'fields': ('name', 'company', 'phone', 'email')
        }),
        ('Location', {
            'fields': ('street1', 'street2', 'city', 'state', 'zip_code', 'country')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(SavedPackage)
class SavedPackageAdmin(admin.ModelAdmin):
    list_display = [
        'nickname', 'package_type', 'weight', 'dimensions',
        'is_default', 'created_at'
    ]
    list_filter = ['is_default', 'package_type']
    search_fields = ['nickname']
    readonly_fields = ['id', 'created_at', 'updated_at']

    def dimensions(self, obj):
        return f"{obj.length} × {obj.width} × {obj.height} in"
    dimensions.short_description = 'Dimensions (L×W×H)'

    fieldsets = (
        ('Preset Info', {
            'fields': ('id', 'nickname', 'is_default')
        }),
        ('Package Details', {
            'fields': ('package_type', 'length', 'width', 'height', 'weight')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
