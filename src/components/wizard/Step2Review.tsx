import { useState, useMemo } from 'react'
import { useStore } from '../../store/useStore'
import { api } from '../../lib/api'
import { toast } from 'sonner'
import {
  Search,
  Edit2,
  Trash2,
  ChevronLeft,
  ChevronRight,
  X,
} from 'lucide-react'
import { cn, getStatusColor } from '../../lib/utils'
import type { Shipment } from '../../lib/types'

const US_STATES = 'AL,AK,AZ,AR,CA,CO,CT,DE,FL,GA,HI,ID,IL,IN,IA,KS,KY,LA,ME,MD,MA,MI,MN,MS,MO,MT,NE,NV,NH,NJ,NM,NY,NC,ND,OH,OK,OR,PA,RI,SC,SD,TN,TX,UT,VT,VA,WA,WV,WI,WY,DC,PR'.split(',')

export default function Step2Review() {
  const {
    session,
    shipments,
    setShipments,
    setSession,
    selectedShipmentIds,
    setSelectedShipmentIds,
    toggleShipmentSelection,
    clearSelection,
    nextStep,
    setCurrentStep,
    savedAddresses,
    savedPackages,
  } = useStore()

  const [searchQuery, setSearchQuery] = useState('')
  const [currentPage, setCurrentPage] = useState(1)
  const [editModal, setEditModal] = useState<{ shipment: Shipment; tab: 'address' | 'package' | 'order' } | null>(null)
  const [editForm, setEditForm] = useState<Record<string, string | number>>({})
  const [saving, setSaving] = useState(false)
  const itemsPerPage = 10

  // Filter shipments based on search
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

  // Pagination
  const paginatedShipments = useMemo(() => {
    const start = (currentPage - 1) * itemsPerPage
    return filteredShipments.slice(start, start + itemsPerPage)
  }, [filteredShipments, currentPage])

  const totalPages = Math.ceil(filteredShipments.length / itemsPerPage)

  // Handlers
  const handleSelectAll = () => {
    if (selectedShipmentIds.length === paginatedShipments.length) {
      clearSelection()
    } else {
      setSelectedShipmentIds(paginatedShipments.map((s) => s.id))
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

  const handleBulkUpdateAddress = async (addressId: string) => {
    if (selectedShipmentIds.length === 0) return

    try {
      await api.bulkUpdateAddress({
        shipment_ids: selectedShipmentIds,
        saved_address_id: addressId,
      })

      // Refresh shipments
      const response = await api.getShipments(shipments[0].upload_session)
      setShipments(response.results)
      clearSelection()
      toast.success(`Updated ${selectedShipmentIds.length} addresses`)
    } catch (error) {
      toast.error('Failed to update addresses')
    }
  }

  const handleBulkUpdatePackage = async (packageId: string) => {
    if (selectedShipmentIds.length === 0) return

    try {
      await api.bulkUpdatePackage({
        shipment_ids: selectedShipmentIds,
        saved_package_id: packageId,
      })

      const response = await api.getShipments(shipments[0].upload_session)
      setShipments(response.results)
      clearSelection()
      toast.success(`Updated ${selectedShipmentIds.length} packages`)
    } catch (error) {
      toast.error('Failed to update packages')
    }
  }

  const handleEdit = async (shipmentId: string) => {
    try {
      const full = await api.getShipment(shipmentId)
      const shipTo = full.addresses?.find((a: any) => a.address_type === 'ship_to')
      const pkg = full.package
      setEditForm({
        name: shipTo?.name || '',
        street1: shipTo?.street1 || '',
        street2: shipTo?.street2 || '',
        city: shipTo?.city || '',
        state: shipTo?.state || '',
        zip_code: shipTo?.zip_code || '',
        phone: shipTo?.phone || '',
        length: pkg ? parseFloat(String(pkg.length)) : 0,
        width: pkg ? parseFloat(String(pkg.width)) : 0,
        height: pkg ? parseFloat(String(pkg.height)) : 0,
        weight: pkg ? parseFloat(String(pkg.weight)) : 0,
        reference_number: full.reference_number || '',
      })
      setEditModal({ shipment: full, tab: 'address' })
    } catch {
      toast.error('Failed to load shipment')
    }
  }

  const handleSaveEdit = async () => {
    if (!editModal) return
    setSaving(true)
    try {
      const shipTo = editModal.shipment.addresses?.find((a: any) => a.address_type === 'ship_to')
      if (shipTo) {
        await api.updateAddress(shipTo.id, {
          name: String(editForm.name),
          street1: String(editForm.street1),
          street2: String(editForm.street2),
          city: String(editForm.city),
          state: String(editForm.state),
          zip_code: String(editForm.zip_code),
          phone: String(editForm.phone),
        })
      }
      if (editModal.shipment.package) {
        await api.updatePackage(editModal.shipment.package.id, {
          length: Number(editForm.length),
          width: Number(editForm.width),
          height: Number(editForm.height),
          weight: Number(editForm.weight),
        })
      }
      // Update shipment reference number
      await api.updateShipment(editModal.shipment.id, {
        reference_number: String(editForm.reference_number),
      })
      const response = await api.getShipments(session?.id || editModal.shipment.upload_session)
      setShipments(response.results)
      setEditModal(null)
      toast.success('Saved')
    } catch (e: any) {
      toast.error(e?.response?.data?.error || 'Save failed')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="max-w-7xl mx-auto p-4 md:p-8 animate-fade-in">
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        {/* Header */}
        <div className="p-4 md:p-6 border-b border-gray-200">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-4">
            <div>
              <h2 className="text-xl md:text-2xl font-bold text-gray-900">
                Review and Edit File
              </h2>
              <p className="text-sm md:text-base text-gray-600 mt-1">
                {filteredShipments.length} shipments loaded
              </p>
            </div>

            {/* Search */}
            <div className="relative w-full md:w-80">
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

          {/* Bulk Actions Bar */}
          {selectedShipmentIds.length > 0 && (
            <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg border border-blue-200">
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
                {/* Bulk Update Address Dropdown */}
                <select
                  className="px-3 py-1.5 border border-blue-300 rounded-lg text-sm bg-white"
                  onChange={(e) => e.target.value && handleBulkUpdateAddress(e.target.value)}
                  defaultValue=""
                >
                  <option value="">Change Ship From Address</option>
                  {savedAddresses.map((addr) => (
                    <option key={addr.id} value={addr.id}>
                      {addr.nickname}
                    </option>
                  ))}
                </select>

                {/* Bulk Update Package Dropdown */}
                <select
                  className="px-3 py-1.5 border border-blue-300 rounded-lg text-sm bg-white"
                  onChange={(e) => e.target.value && handleBulkUpdatePackage(e.target.value)}
                  defaultValue=""
                >
                  <option value="">Change Package Details</option>
                  {savedPackages.map((pkg) => (
                    <option key={pkg.id} value={pkg.id}>
                      {pkg.nickname}
                    </option>
                  ))}
                </select>

                {/* Bulk Delete */}
                <button
                  onClick={handleBulkDelete}
                  className="px-3 py-1.5 bg-red-600 text-white rounded-lg text-sm hover:bg-red-700 flex items-center space-x-1"
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
                  <input
                    type="checkbox"
                    checked={
                      paginatedShipments.length > 0 &&
                      selectedShipmentIds.length === paginatedShipments.length
                    }
                    onChange={handleSelectAll}
                    className="rounded border-gray-300"
                  />
                </th>
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">
                  #
                </th>
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">
                  Status
                </th>
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">
                  Ship From
                </th>
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">
                  Ship To
                </th>
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">
                  Phone
                </th>
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">
                  Package
                </th>
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">
                  Order No
                </th>
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">
                  Actions
                </th>
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
                    <input
                      type="checkbox"
                      checked={selectedShipmentIds.includes(shipment.id)}
                      onChange={() => toggleShipmentSelection(shipment.id)}
                      className="rounded border-gray-300"
                    />
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-900">
                    #{shipment.csv_row_number || '-'}
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className={cn(
                        'px-2 py-1 rounded text-xs font-medium border',
                        getStatusColor(shipment.status)
                      )}
                    >
                      {shipment.status_display}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-900">
                    {shipment.ship_from_summary || 'N/A'}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-900">
                    {shipment.ship_to_summary || 'N/A'}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-900">
                    {shipment.addresses?.find((a: any) => a.address_type === 'ship_to')?.phone || '-'}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-900">
                    {shipment.package_summary || (shipment.package ? `${shipment.package.weight}oz` : '-')}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-900">
                    {shipment.reference_number || '-'}
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => handleEdit(shipment.id)}
                        className="p-1.5 text-blue-600 hover:bg-blue-50 rounded"
                        title="Edit"
                      >
                        <Edit2 className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleDelete(shipment.id)}
                        className="p-1.5 text-red-600 hover:bg-red-50 rounded"
                        title="Delete"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
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
              Page {currentPage} of {totalPages}
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
        <div className="p-4 md:p-6 border-t border-gray-200 flex flex-col sm:flex-row justify-between gap-3">
          <button
            onClick={() => {
              if (
                confirm(
                  'Going back will lose your current data. Are you sure you want to return to the upload step?'
                )
              ) {
                setSession(null)
                setShipments([])
                clearSelection()
                setCurrentStep(1)
              }
            }}
            className="px-4 md:px-6 py-2.5 border border-gray-300 rounded-lg font-medium text-gray-700 hover:bg-gray-50 transition-all duration-200 hover:shadow-md order-2 sm:order-1"
          >
            Back
          </button>
          <button
            onClick={nextStep}
            className="px-4 md:px-6 py-2.5 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-all duration-200 hover:shadow-lg transform hover:-translate-y-0.5 order-1 sm:order-2"
          >
            Continue to Shipping
          </button>
        </div>
      </div>

      {/* Edit Modal - PRD 4.2.4 & 4.2.5 */}
      {editModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full max-h-[90vh] overflow-y-auto">
            <div className="p-4 border-b flex justify-between items-center">
              <h3 className="font-semibold">Edit Shipment</h3>
              <button onClick={() => setEditModal(null)} className="p-1 text-gray-500 hover:text-gray-700">
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="p-4 space-y-4">
              <div className="flex gap-2 border-b">
                <button
                  onClick={() => setEditModal((m) => m && { ...m, tab: 'address' })}
                  className={cn('px-3 py-2 text-sm font-medium', editModal.tab === 'address' ? 'border-b-2 border-blue-600 text-blue-600' : 'text-gray-500')}
                >
                  Address
                </button>
                <button
                  onClick={() => setEditModal((m) => m && { ...m, tab: 'package' })}
                  className={cn('px-3 py-2 text-sm font-medium', editModal.tab === 'package' ? 'border-b-2 border-blue-600 text-blue-600' : 'text-gray-500')}
                >
                  Package
                </button>
                <button
                  onClick={() => setEditModal((m) => m && { ...m, tab: 'order' })}
                  className={cn('px-3 py-2 text-sm font-medium', editModal.tab === 'order' ? 'border-b-2 border-blue-600 text-blue-600' : 'text-gray-500')}
                >
                  Order Info
                </button>
              </div>
              {editModal.tab === 'address' ? (
                <div className="grid gap-2 text-sm">
                  <div>
                    <label className="block text-gray-600 mb-1">Name</label>
                    <input value={editForm.name || ''} onChange={(e) => setEditForm((f) => ({ ...f, name: e.target.value }))} className="w-full border rounded px-2 py-1.5" />
                  </div>
                  <div>
                    <label className="block text-gray-600 mb-1">Address Line 1</label>
                    <input value={editForm.street1 || ''} onChange={(e) => setEditForm((f) => ({ ...f, street1: e.target.value }))} className="w-full border rounded px-2 py-1.5" />
                  </div>
                  <div>
                    <label className="block text-gray-600 mb-1">Address Line 2</label>
                    <input value={editForm.street2 || ''} onChange={(e) => setEditForm((f) => ({ ...f, street2: e.target.value }))} className="w-full border rounded px-2 py-1.5" />
                  </div>
                  <div className="grid grid-cols-2 gap-2">
                    <div>
                      <label className="block text-gray-600 mb-1">City</label>
                      <input value={editForm.city || ''} onChange={(e) => setEditForm((f) => ({ ...f, city: e.target.value }))} className="w-full border rounded px-2 py-1.5" />
                    </div>
                    <div>
                      <label className="block text-gray-600 mb-1">State</label>
                      <select value={editForm.state || ''} onChange={(e) => setEditForm((f) => ({ ...f, state: e.target.value }))} className="w-full border rounded px-2 py-1.5">
                        <option value="">Select</option>
                        {US_STATES.map((s) => (
                          <option key={s} value={s}>{s}</option>
                        ))}
                      </select>
                    </div>
                  </div>
                  <div>
                    <label className="block text-gray-600 mb-1">Zip Code</label>
                    <input value={editForm.zip_code || ''} onChange={(e) => setEditForm((f) => ({ ...f, zip_code: e.target.value }))} className="w-full border rounded px-2 py-1.5" />
                  </div>
                  <div>
                    <label className="block text-gray-600 mb-1">Phone</label>
                    <input value={editForm.phone || ''} onChange={(e) => setEditForm((f) => ({ ...f, phone: e.target.value }))} className="w-full border rounded px-2 py-1.5" />
                  </div>
                </div>
              ) : editModal.tab === 'package' ? (
                <div className="grid gap-2 text-sm">
                  <div>
                    <label className="block text-gray-600 mb-1">Length (in)</label>
                    <input type="number" step="0.1" value={editForm.length || ''} onChange={(e) => setEditForm((f) => ({ ...f, length: parseFloat(e.target.value) || 0 }))} className="w-full border rounded px-2 py-1.5" />
                  </div>
                  <div>
                    <label className="block text-gray-600 mb-1">Width (in)</label>
                    <input type="number" step="0.1" value={editForm.width || ''} onChange={(e) => setEditForm((f) => ({ ...f, width: parseFloat(e.target.value) || 0 }))} className="w-full border rounded px-2 py-1.5" />
                  </div>
                  <div>
                    <label className="block text-gray-600 mb-1">Height (in)</label>
                    <input type="number" step="0.1" value={editForm.height || ''} onChange={(e) => setEditForm((f) => ({ ...f, height: parseFloat(e.target.value) || 0 }))} className="w-full border rounded px-2 py-1.5" />
                  </div>
                  <div>
                    <label className="block text-gray-600 mb-1">Weight (oz)</label>
                    <input type="number" step="0.1" value={editForm.weight || ''} onChange={(e) => setEditForm((f) => ({ ...f, weight: parseFloat(e.target.value) || 0 }))} className="w-full border rounded px-2 py-1.5" />
                  </div>
                </div>
              ) : (
                <div className="grid gap-2 text-sm">
                  <div>
                    <label className="block text-gray-600 mb-1">Order Number</label>
                    <input
                      value={editForm.reference_number || ''}
                      onChange={(e) => setEditForm((f) => ({ ...f, reference_number: e.target.value }))}
                      className="w-full border rounded px-2 py-1.5"
                      placeholder="Enter order/reference number"
                    />
                  </div>
                  <p className="text-xs text-gray-500 mt-1">
                    This is your internal order or reference number for tracking this shipment.
                  </p>
                </div>
              )}
            </div>
            <div className="p-4 border-t flex justify-end gap-2">
              <button onClick={() => setEditModal(null)} className="px-4 py-2 border rounded-lg text-sm">Cancel</button>
              <button onClick={handleSaveEdit} disabled={saving} className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm disabled:opacity-50">
                {saving ? 'Saving...' : 'Save'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
