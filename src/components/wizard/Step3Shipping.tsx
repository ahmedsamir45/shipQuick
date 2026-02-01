import { useState, useMemo, useCallback } from 'react'
import { useStore } from '../../store/useStore'
import { api } from '../../lib/api'
import { toast } from 'sonner'
import {
  Search,
  ChevronLeft,
  ChevronRight,
  Trash2,
  X,
} from 'lucide-react'
import { cn, formatCurrency } from '../../lib/utils'

export default function Step3Shipping() {
  const {
    session,
    shipments,
    setShipments,
    selectedShipmentIds,
    setSelectedShipmentIds,
    toggleShipmentSelection,
    clearSelection,
    nextStep,
    previousStep,
  } = useStore()

  const [searchQuery, setSearchQuery] = useState('')
  const [currentPage, setCurrentPage] = useState(1)
  const [bulkServiceModal, setBulkServiceModal] = useState(false)
  const [updatingService, setUpdatingService] = useState<string | null>(null)
  const itemsPerPage = 10

  const sessionId = session?.id
  const canEdit = session && !session.is_locked

  const filteredShipments = useMemo(() => {
    if (!searchQuery) return shipments
    const query = searchQuery.toLowerCase()
    return shipments.filter(
      (s) =>
        s.reference_number?.toLowerCase().includes(query) ||
        s.ship_from_summary?.toLowerCase().includes(query) ||
        s.ship_to_summary?.toLowerCase().includes(query)
    )
  }, [shipments, searchQuery])

  const paginatedShipments = useMemo(() => {
    const start = (currentPage - 1) * itemsPerPage
    return filteredShipments.slice(start, start + itemsPerPage)
  }, [filteredShipments, currentPage])

  const totalPages = Math.ceil(filteredShipments.length / itemsPerPage)

  const totalPrice = useMemo(() => {
    return shipments.reduce((sum, s) => {
      const price = s.shipping_price ? parseFloat(s.shipping_price) : 0
      return sum + price
    }, 0)
  }, [shipments])

  const handleSelectAll = () => {
    if (selectedShipmentIds.length === paginatedShipments.length) {
      clearSelection()
    } else {
      setSelectedShipmentIds(paginatedShipments.map((s) => s.id))
    }
  }

  const handleServiceChange = useCallback(
    async (shipmentId: string, serviceType: string) => {
      if (!canEdit) return
      setUpdatingService(shipmentId)
      try {
        await api.bulkUpdateService({
          shipment_ids: [shipmentId],
          service_type: serviceType as 'priority_mail' | 'ground_shipping' | 'most_affordable',
        })
        const response = await api.getShipments(sessionId!)
        setShipments(response.results)
        toast.success('Shipping service updated')
      } catch (error: any) {
        toast.error(error?.response?.data?.error || 'Failed to update service')
      } finally {
        setUpdatingService(null)
      }
    },
    [canEdit, sessionId, setShipments]
  )

  const handleBulkServiceChange = async (serviceType: string) => {
    if (selectedShipmentIds.length === 0) return
    setBulkServiceModal(false)
    try {
      await api.bulkUpdateService({
        shipment_ids: selectedShipmentIds,
        service_type: serviceType as 'priority_mail' | 'ground_shipping' | 'most_affordable',
      })
      const response = await api.getShipments(sessionId!)
      setShipments(response.results)
      clearSelection()
      toast.success(`Updated ${selectedShipmentIds.length} shipments`)
    } catch (error: any) {
      toast.error(error?.response?.data?.error || 'Failed to update services')
    }
  }

  const handleDelete = async (shipmentId: string) => {
    if (!confirm('Are you sure you want to delete this shipment?')) return
    try {
      await api.deleteShipment(shipmentId)
      setShipments(shipments.filter((s) => s.id !== shipmentId))
      toast.success('Shipment deleted')
    } catch (error) {
      toast.error('Failed to delete shipment')
    }
  }

  const handleBulkDelete = async () => {
    if (selectedShipmentIds.length === 0) return
    if (!confirm(`Delete ${selectedShipmentIds.length} shipments?`)) return
    try {
      await api.bulkDeleteShipments({ shipment_ids: selectedShipmentIds })
      setShipments(shipments.filter((s) => !selectedShipmentIds.includes(s.id)))
      clearSelection()
      toast.success(`Deleted ${selectedShipmentIds.length} shipments`)
    } catch (error) {
      toast.error('Failed to delete shipments')
    }
  }

  if (!sessionId) {
    return (
      <div className="max-w-4xl mx-auto p-8">
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 text-center">
          <p className="text-yellow-800">No session found. Please start from Step 1.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto p-4 md:p-8 animate-fade-in">
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        {/* Header with Total */}
        <div className="p-4 md:p-6 border-b border-gray-200">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-4">
            <div>
              <h2 className="text-xl md:text-2xl font-bold text-gray-900">
                Select Shipping Provider
              </h2>
              <p className="text-sm md:text-base text-gray-600 mt-1">
                {filteredShipments.length} shipments • Choose shipping service for each
              </p>
            </div>
            <div className="text-left md:text-right">
              <div className="text-sm text-gray-500">Total</div>
              <div className="text-2xl md:text-3xl font-bold text-blue-600 animate-pulse-slow">
                {formatCurrency(totalPrice)}
              </div>
            </div>
          </div>

          <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 sm:gap-4">
            <div className="relative w-full sm:w-80">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search by reference, name, or address..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>

          {/* Bulk Actions */}
          {selectedShipmentIds.length > 0 && (
            <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg border border-blue-200 mt-4">
              <div className="flex items-center space-x-4">
                <span className="text-sm font-medium text-blue-900">
                  {selectedShipmentIds.length} selected
                </span>
                <button
                  onClick={clearSelection}
                  className="text-sm text-blue-700 hover:text-blue-800 flex items-center space-x-1"
                >
                  <X className="w-4 h-4" />
                  <span>Clear</span>
                </button>
              </div>
              <div className="flex items-center space-x-2">
                <div className="relative group">
                  <button
                    onClick={() => setBulkServiceModal(!bulkServiceModal)}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700"
                  >
                    Change Shipping for Selected
                  </button>
                  {bulkServiceModal && (
                    <div className="absolute right-0 mt-1 w-56 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-10">
                      <button
                        onClick={() => handleBulkServiceChange('most_affordable')}
                        className="w-full px-4 py-2 text-left text-sm hover:bg-gray-50"
                      >
                        Switch to most affordable rate
                      </button>
                      <button
                        onClick={() => handleBulkServiceChange('priority_mail')}
                        className="w-full px-4 py-2 text-left text-sm hover:bg-gray-50"
                      >
                        Change to Priority Mail
                      </button>
                      <button
                        onClick={() => handleBulkServiceChange('ground_shipping')}
                        className="w-full px-4 py-2 text-left text-sm hover:bg-gray-50"
                      >
                        Change to Ground Shipping (under 1 lb only)
                      </button>
                    </div>
                  )}
                </div>
                <button
                  onClick={handleBulkDelete}
                  className="px-4 py-2 bg-red-600 text-white rounded-lg text-sm hover:bg-red-700 flex items-center space-x-1"
                >
                  <Trash2 className="w-4 h-4" />
                  <span>Delete Selected</span>
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Table */}
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-4 py-3 text-left">
                  {canEdit && (
                    <input
                      type="checkbox"
                      checked={
                        paginatedShipments.length > 0 &&
                        selectedShipmentIds.length === paginatedShipments.length
                      }
                      onChange={handleSelectAll}
                      className="rounded border-gray-300"
                    />
                  )}
                </th>
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">
                  Ship From
                </th>
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">
                  Ship To
                </th>
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">
                  Package
                </th>
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">
                  Order No
                </th>
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">
                  Shipping Service
                </th>
                {canEdit && (
                  <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">
                    Action
                  </th>
                )}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {paginatedShipments.map((shipment) => (
                <tr
                  key={shipment.id}
                  className={cn(
                    'hover:bg-gray-50',
                    selectedShipmentIds.includes(shipment.id) && 'bg-blue-50'
                  )}
                >
                  <td className="px-4 py-3">
                    {canEdit && (
                      <input
                        type="checkbox"
                        checked={selectedShipmentIds.includes(shipment.id)}
                        onChange={() => toggleShipmentSelection(shipment.id)}
                        className="rounded border-gray-300"
                      />
                    )}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-900">
                    {shipment.ship_from_summary || '—'}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-900">
                    {shipment.ship_to_summary || '—'}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-900">
                    {shipment.package_summary || '—'}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-900">
                    {shipment.reference_number || '—'}
                  </td>
                  <td className="px-4 py-3">
                    {canEdit && shipment.available_services?.length ? (
                      <select
                        value={shipment.shipping_service?.service_type || ''}
                        onChange={(e) =>
                          handleServiceChange(shipment.id, e.target.value)
                        }
                        disabled={!!updatingService}
                        className="text-sm border border-gray-300 rounded px-2 py-1.5 min-w-[140px]"
                      >
                        {shipment.available_services.map((opt) => (
                          <option
                            key={`${opt.service_type}-${opt.service_tier}`}
                            value={opt.service_type}
                          >
                            {opt.service_type === 'priority_mail'
                              ? 'Priority Mail'
                              : 'Ground'}{' '}
                            — {formatCurrency(opt.price ?? 0)}
                          </option>
                        ))}
                      </select>
                    ) : (
                      <span className="text-sm">
                        {shipment.shipping_service?.service_type_display} —{' '}
                        {formatCurrency(shipment.shipping_price)}
                      </span>
                    )}
                  </td>
                  {canEdit && (
                    <td className="px-4 py-3">
                      <button
                        onClick={() => handleDelete(shipment.id)}
                        className="p-1.5 text-red-600 hover:bg-red-50 rounded"
                        title="Delete"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        <div className="p-4 border-t border-gray-200 flex items-center justify-between">
          <div className="text-sm text-gray-600">
            Showing {(currentPage - 1) * itemsPerPage + 1} to{' '}
            {Math.min(currentPage * itemsPerPage, filteredShipments.length)} of{' '}
            {filteredShipments.length} shipments
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
              disabled={currentPage === 1}
              className={cn(
                'p-2 rounded border',
                currentPage === 1
                  ? 'border-gray-200 text-gray-400 cursor-not-allowed'
                  : 'border-gray-300 text-gray-700 hover:bg-gray-50'
              )}
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <span className="text-sm text-gray-700">
              Page {currentPage} of {totalPages || 1}
            </span>
            <button
              onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
              disabled={currentPage === totalPages}
              className={cn(
                'p-2 rounded border',
                currentPage === totalPages
                  ? 'border-gray-200 text-gray-400 cursor-not-allowed'
                  : 'border-gray-300 text-gray-700 hover:bg-gray-50'
              )}
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Navigation */}
        <div className="p-4 md:p-6 border-t border-gray-200 flex flex-col sm:flex-row justify-between items-stretch sm:items-center gap-3">
          <button
            onClick={previousStep}
            className="px-4 md:px-6 py-2.5 border border-gray-300 rounded-lg font-medium text-gray-700 hover:bg-gray-50 transition-all duration-200 hover:shadow-md order-2 sm:order-1"
          >
            Back
          </button>
          <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3 order-1 sm:order-2">
            <span className="text-base md:text-lg font-semibold text-gray-900 text-center sm:text-left">
              Total: {formatCurrency(totalPrice)}
            </span>
            <button
              onClick={nextStep}
              disabled={shipments.length === 0}
              className={cn(
                'px-4 md:px-6 py-2.5 rounded-lg font-medium transition-all duration-200',
                shipments.length > 0
                  ? 'bg-blue-600 text-white hover:bg-blue-700 hover:shadow-lg transform hover:-translate-y-0.5'
                  : 'bg-gray-200 text-gray-400 cursor-not-allowed'
              )}
            >
              Continue to Purchase
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
