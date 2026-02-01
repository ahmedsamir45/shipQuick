/**
 * TypeScript interfaces matching the Django backend models
 */

export interface Address {
  id: string
  shipment: string
  address_type: 'ship_from' | 'ship_to'
  address_type_display: string
  name: string
  company?: string
  street1: string
  street2?: string
  city: string
  state: string
  zip_code: string
  country: string
  phone?: string
  email?: string
  is_validated: boolean
  validation_status: 'pending' | 'valid' | 'invalid' | 'fallback_valid'
  validation_status_display: string
  validation_error?: string
  validated_at?: string
  validated_by_provider?: string
  created_at: string
  updated_at: string
}

export interface Package {
  id: string
  shipment: string
  length: string
  width: string
  height: string
  weight: string
  weight_unit: string
  weight_in_ounces: number
  package_type: 'box' | 'envelope' | 'pak' | 'tube'
  created_at: string
  updated_at: string
}

export interface ShippingService {
  id: string
  shipment: string
  service_type: 'priority_mail' | 'ground_shipping'
  service_type_display: string
  service_tier: string
  service_tier_display: string
  price: string
  currency: string
  auto_selected: boolean
  created_at: string
  updated_at: string
}

export interface Shipment {
  id: string
  upload_session: string
  csv_row_number?: number
  status: 'valid' | 'warning' | 'error'
  status_display: string
  validation_messages: Array<{
    message: string
    severity: string
    timestamp?: string
  }>
  address_validation_provider?: string
  customs_description?: string
  customs_value?: string
  reference_number?: string
  addresses: Address[]
  package?: Package
  shipping_service?: ShippingService
  can_edit: boolean
  created_at: string
  updated_at: string

  // Simplified properties for list view
  ship_from_summary?: string
  ship_to_summary?: string
  shipping_price?: string
  package_summary?: string
  available_services?: Array<{ service_type: string; service_tier: string; price: number; description: string }>
}

export interface UploadSession {
  id: string
  status: 'draft' | 'in_review' | 'purchased'
  status_display: string
  total_shipments: number
  valid_shipments: number
  warning_shipments: number
  error_shipments: number
  is_locked: boolean
  purchase_date?: string
  label_size?: 'letter' | '4x6'
  label_size_display?: string
  terms_accepted: boolean
  can_edit: boolean
  total_price: string
  created_at: string
  updated_at: string
  shipments?: Shipment[]
}

export interface SavedAddress {
  id: string
  nickname: string
  name: string
  company?: string
  street1: string
  street2?: string
  city: string
  state: string
  zip_code: string
  country: string
  phone?: string
  email?: string
  is_default: boolean
  created_at: string
  updated_at: string
}

export interface SavedPackage {
  id: string
  nickname: string
  length: string
  width: string
  height: string
  weight: string
  package_type: 'box' | 'envelope' | 'pak' | 'tube'
  is_default: boolean
  created_at: string
  updated_at: string
}

export interface CSVUploadResult {
  message: string
  result: {
    success: boolean
    shipments_created: number
    total_rows: number
    errors: string[]
    warnings: string[]
    session_id: string
  }
  session: UploadSession
}

export interface PurchaseRequest {
  label_size: 'letter' | '4x6'
  terms_accepted: boolean
}

export interface BulkUpdateAddressRequest {
  shipment_ids: string[]
  saved_address_id: string
}

export interface BulkUpdatePackageRequest {
  shipment_ids: string[]
  saved_package_id: string
}

export interface BulkUpdateServiceRequest {
  shipment_ids: string[]
  service_type: 'priority_mail' | 'ground_shipping' | 'most_affordable'
}

export interface BulkDeleteRequest {
  shipment_ids: string[]
}

// UI-specific types

export type WizardStep = 1 | 2 | 3 | 4

export interface WizardStepInfo {
  number: WizardStep
  title: string
  description: string
  path: string
}

export interface TableColumn<T> {
  id: string
  header: string
  accessorKey?: keyof T
  cell?: (row: T) => React.ReactNode
  enableSorting?: boolean
  enableColumnFilter?: boolean
}

export interface ApiError {
  error: string
  status_code: number
  details?: Record<string, any>
}
