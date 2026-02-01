import { useState } from 'react'
import { useStore } from '../../store/useStore'
import { api } from '../../lib/api'
import { toast } from 'sonner'
import { CheckCircle, Download } from 'lucide-react'
import { cn, formatCurrency } from '../../lib/utils'

export default function Step4Purchase() {
  const { session, shipments, previousStep, reset } = useStore()
  const [labelSize, setLabelSize] = useState<'letter' | '4x6'>('4x6')
  const [termsAccepted, setTermsAccepted] = useState(false)
  const [purchasing, setPurchasing] = useState(false)
  const [purchaseComplete, setPurchaseComplete] = useState(false)

  const sessionId = session?.id
  const totalPrice = shipments.reduce((sum, s) => {
    const price = s.shipping_price ? parseFloat(s.shipping_price) : 0
    return sum + price
  }, 0)

  const canPurchase =
    session &&
    !session.is_locked &&
    shipments.length > 0 &&
    termsAccepted &&
    session.error_shipments === 0

  const handlePurchase = async () => {
    if (!canPurchase || !sessionId) return
    setPurchasing(true)
    try {
      await api.purchaseSession(sessionId, {
        label_size: labelSize,
        terms_accepted: termsAccepted,
      })
      setPurchaseComplete(true)
      toast.success('Purchase completed successfully!')
    } catch (error: any) {
      toast.error(
        error?.response?.data?.error || 'Purchase failed. Please try again.'
      )
    } finally {
      setPurchasing(false)
    }
  }

  const handleNewOrder = () => {
    reset()
    window.location.reload()
  }

  const handleDownloadLabels = async () => {
    if (!sessionId) return

    try {
      toast.loading('Preparing labels for download...')

      // Call backend API to get labels
      const response = await fetch(`http://localhost:8000/api/sessions/${sessionId}/download_labels/`, {
        method: 'GET',
        headers: {
          'Accept': 'application/json,application/pdf,application/zip',
        },
      })

      if (!response.ok) {
        throw new Error('Failed to download labels')
      }

      // Get filename from response header or create based on content type
      const contentType = response.headers.get('Content-Type') || ''
      const contentDisposition = response.headers.get('Content-Disposition')

      let filename = contentDisposition
        ? contentDisposition.split('filename=')[1]?.replace(/"/g, '')
        : null

      // If no filename from header, create based on content type
      if (!filename) {
        if (contentType.includes('json')) {
          filename = `shipping-labels-${sessionId}.json`
        } else if (contentType.includes('pdf')) {
          filename = `shipping-labels-${sessionId}.pdf`
        } else if (contentType.includes('zip')) {
          filename = `shipping-labels-${sessionId}.zip`
        } else {
          filename = `shipping-labels-${sessionId}`
        }
      }

      // Create blob and download
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)

      toast.dismiss()
      toast.success('Labels downloaded successfully!')
    } catch (error) {
      toast.dismiss()
      toast.error('Failed to download labels. Please try again.')
      console.error('Download error:', error)
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

  if (purchaseComplete) {
    return (
      <div className="max-w-2xl mx-auto p-4 md:p-8 animate-fade-in">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 md:p-12 text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 md:w-20 md:h-20 rounded-full bg-green-100 mb-6 animate-bounce-slow">
            <CheckCircle className="w-10 h-10 md:w-12 md:h-12 text-green-600" />
          </div>
          <h2 className="text-xl md:text-2xl font-bold text-gray-900 mb-2">
            Labels Created Successfully!
          </h2>
          <p className="text-sm md:text-base text-gray-600 mb-6">
            Your shipping labels have been generated and are ready for download.
          </p>
          <div className="bg-gradient-to-br from-gray-50 to-gray-100 rounded-lg p-4 md:p-6 mb-8 text-left transform hover:scale-105 transition-transform duration-200">
            <h3 className="font-semibold text-gray-900 mb-2 text-sm md:text-base">Summary</h3>
            <ul className="space-y-1 text-xs md:text-sm text-gray-600">
              <li>• {shipments.length} label(s) created</li>
              <li>• Label format: {labelSize === '4x6' ? '4x6 inch' : 'Letter/A4'}</li>
              <li>• Total: {formatCurrency(totalPrice)}</li>
            </ul>
          </div>
          <div className="flex justify-center gap-4">
            <button
              onClick={handleDownloadLabels}
              className="px-6 py-2.5 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-all duration-200 hover:shadow-lg transform hover:-translate-y-0.5 flex items-center gap-2"
            >
              <Download className="w-5 h-5" />
              Download Labels
            </button>
            <button
              onClick={handleNewOrder}
              className="px-6 py-2.5 border border-gray-300 rounded-lg font-medium text-gray-700 hover:bg-gray-50"
            >
              Create New Order
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-2xl mx-auto p-4 md:p-8 animate-fade-in">
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 md:p-8">
        <h2 className="text-xl md:text-2xl font-bold text-gray-900 mb-6">
          Purchase Labels
        </h2>

        {/* Label Size Selection */}
        <div className="mb-8">
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Label Size
          </label>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 md:gap-4">
            <button
              onClick={() => setLabelSize('letter')}
              className={cn(
                'p-3 md:p-4 rounded-lg border-2 text-left transition-all duration-200 transform hover:scale-105',
                labelSize === 'letter'
                  ? 'border-blue-600 bg-blue-50 shadow-md'
                  : 'border-gray-200 hover:border-gray-300 hover:shadow-sm'
              )}
            >
              <div className="font-medium text-gray-900 text-sm md:text-base">Letter / A4</div>
              <div className="text-xs md:text-sm text-gray-500 mt-1">
                Standard paper (8.5x11 or A4)
              </div>
            </button>
            <button
              onClick={() => setLabelSize('4x6')}
              className={cn(
                'p-3 md:p-4 rounded-lg border-2 text-left transition-all duration-200 transform hover:scale-105',
                labelSize === '4x6'
                  ? 'border-blue-600 bg-blue-50 shadow-md'
                  : 'border-gray-200 hover:border-gray-300 hover:shadow-sm'
              )}
            >
              <div className="font-medium text-gray-900 text-sm md:text-base">4x6 inch</div>
              <div className="text-xs md:text-sm text-gray-500 mt-1">Thermal label format</div>
            </button>
          </div>
        </div>

        {/* Grand Total */}
        <div className="mb-8 p-4 md:p-6 bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg border border-blue-200 transform hover:scale-105 transition-transform duration-200">
          <div className="flex justify-between items-center">
            <span className="text-sm md:text-base text-blue-700 font-medium">Grand Total</span>
            <span className="text-xl md:text-2xl font-bold text-blue-900 animate-pulse-slow">
              {formatCurrency(totalPrice)}
            </span>
          </div>
        </div>

        {/* Terms */}
        <div className="mb-8">
          <label className="flex items-start gap-3 cursor-pointer">
            <input
              type="checkbox"
              checked={termsAccepted}
              onChange={(e) => setTermsAccepted(e.target.checked)}
              className="mt-1 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span className="text-sm text-gray-700">
              I accept the terms and conditions for purchasing shipping labels
            </span>
          </label>
        </div>

        {/* Navigation */}
        <div className="flex flex-col sm:flex-row justify-between items-stretch sm:items-center gap-3 pt-4 border-t border-gray-200">
          <button
            onClick={previousStep}
            className="px-4 md:px-6 py-2.5 border border-gray-300 rounded-lg font-medium text-gray-700 hover:bg-gray-50 transition-all duration-200 hover:shadow-md order-2 sm:order-1"
          >
            Back
          </button>
          <button
            onClick={handlePurchase}
            disabled={!canPurchase || purchasing}
            className={cn(
              'px-4 md:px-6 py-2.5 rounded-lg font-medium transition-all duration-200 flex items-center justify-center gap-2 order-1 sm:order-2',
              canPurchase && !purchasing
                ? 'bg-green-600 text-white hover:bg-green-700 hover:shadow-lg transform hover:-translate-y-0.5'
                : 'bg-gray-200 text-gray-400 cursor-not-allowed'
            )}
          >
            {purchasing ? (
              <>
                <span className="inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                Processing...
              </>
            ) : (
              'Confirm Purchase'
            )}
          </button>
        </div>
      </div>
    </div>
  )
}
