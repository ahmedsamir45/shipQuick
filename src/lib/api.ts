import axios, { AxiosInstance } from 'axios'
import type {
  UploadSession,
  Shipment,
  SavedAddress,
  SavedPackage,
  CSVUploadResult,
  PurchaseRequest,
  BulkUpdateAddressRequest,
  BulkUpdatePackageRequest,
  BulkUpdateServiceRequest,
  BulkDeleteRequest,
} from './types'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'

class ApiClient {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    })
  }

  // ========== Upload Session APIs ==========

  async createSession(): Promise<UploadSession> {
    const response = await this.client.post('/sessions/')
    return response.data
  }

  async getSession(sessionId: string): Promise<UploadSession> {
    const response = await this.client.get(`/sessions/${sessionId}/`)
    return response.data
  }

  async uploadCSV(sessionId: string, file: File): Promise<CSVUploadResult> {
    const formData = new FormData()
    formData.append('file', file)

    const response = await this.client.post(
      `/sessions/${sessionId}/upload_csv/`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    )
    return response.data
  }

  async getSessionSummary(sessionId: string): Promise<any> {
    const response = await this.client.get(`/sessions/${sessionId}/summary/`)
    return response.data
  }

  async purchaseSession(
    sessionId: string,
    data: PurchaseRequest
  ): Promise<any> {
    const response = await this.client.post(
      `/sessions/${sessionId}/purchase/`,
      data
    )
    return response.data
  }

  // ========== Shipment APIs ==========

  async getShipments(sessionId: string): Promise<{ results: Shipment[] }> {
    const response = await this.client.get(`/shipments/?session=${sessionId}`)
    return response.data
  }

  async getShipment(shipmentId: string): Promise<Shipment> {
    const response = await this.client.get(`/shipments/${shipmentId}/`)
    return response.data
  }

  async updateShipment(
    shipmentId: string,
    data: Partial<Shipment>
  ): Promise<Shipment> {
    const response = await this.client.patch(`/shipments/${shipmentId}/`, data)
    return response.data
  }

  async deleteShipment(shipmentId: string): Promise<void> {
    await this.client.delete(`/shipments/${shipmentId}/`)
  }

  async bulkDeleteShipments(data: BulkDeleteRequest): Promise<any> {
    const response = await this.client.post(`/shipments/bulk_delete/`, data)
    return response.data
  }

  async bulkUpdateAddress(data: BulkUpdateAddressRequest): Promise<any> {
    const response = await this.client.post(
      `/shipments/bulk_update_address/`,
      data
    )
    return response.data
  }

  async bulkUpdatePackage(data: BulkUpdatePackageRequest): Promise<any> {
    const response = await this.client.post(
      `/shipments/bulk_update_package/`,
      data
    )
    return response.data
  }

  async bulkUpdateService(data: BulkUpdateServiceRequest): Promise<any> {
    const response = await this.client.post(
      `/shipments/bulk_update_service/`,
      data
    )
    return response.data
  }

  // ========== Saved Presets APIs ==========

  async getSavedAddresses(): Promise<SavedAddress[]> {
    const response = await this.client.get('/saved-addresses/')
    return response.data.results || response.data
  }

  async getSavedPackages(): Promise<SavedPackage[]> {
    const response = await this.client.get('/saved-packages/')
    return response.data.results || response.data
  }

  // ========== Address & Package APIs ==========

  async updateAddress(addressId: string, data: Partial<any>): Promise<any> {
    const response = await this.client.patch(`/addresses/${addressId}/`, data)
    return response.data
  }

  async updatePackage(packageId: string, data: Partial<any>): Promise<any> {
    const response = await this.client.patch(`/packages/${packageId}/`, data)
    return response.data
  }
}

export const api = new ApiClient()
export default api
