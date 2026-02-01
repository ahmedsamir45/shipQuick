import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, FileText, Download, CheckCircle, AlertCircle } from 'lucide-react'
import { useStore } from '../../store/useStore'
import { api } from '../../lib/api'
import { toast } from 'sonner'
import { cn } from '../../lib/utils'
import templateCsv from '../../assets/Template.csv?raw'

export default function Step1Upload() {
  const { setSession, setShipments, nextStep, setIsLoading, setUploadProgress } = useStore()
  const [uploading, setUploading] = useState(false)
  const [uploadResult, setUploadResult] = useState<any>(null)

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return

    const file = acceptedFiles[0]

    // Validate file type
    if (!file.name.endsWith('.csv')) {
      toast.error('Please upload a CSV file')
      return
    }

    // Validate file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      toast.error('File size must be less than 10MB')
      return
    }

    setUploading(true)
    setIsLoading(true)
    setUploadProgress(0)

    try {
      // Create session
      toast.info('Creating upload session...')
      const session = await api.createSession()
      setSession(session)

      // Simulate upload progress
      setUploadProgress(30)

      // Upload CSV
      toast.info('Uploading CSV file...')
      const result = await api.uploadCSV(session.id, file)

      setUploadProgress(70)

      // Fetch shipments
      toast.info('Loading shipments...')
      const shipmentsData = await api.getShipments(session.id)
      setShipments(shipmentsData.results)

      setUploadProgress(100)

      // Update session
      const updatedSession = await api.getSession(session.id)
      setSession(updatedSession)

      setUploadResult(result)
      toast.success(`Successfully uploaded ${result.result.shipments_created} shipments!`)

    } catch (error: any) {
      console.error('Upload failed:', error)
      const res = error?.response?.data
      const msg = res?.details?.file || res?.error || 'Upload failed. Please try again.'
      toast.error(msg)
    } finally {
      setUploading(false)
      setIsLoading(false)
      setUploadProgress(0)
    }
  }, [setSession, setShipments, setIsLoading, setUploadProgress])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
    },
    multiple: false,
    disabled: uploading,
  })

  const handleContinue = () => {
    if (uploadResult) {
      nextStep()
    }
  }

  const downloadTemplate = () => {
    const blob = new Blob([templateCsv], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = 'Template.csv'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
    toast.success('Template downloaded!')
  }

  return (
    <div className="max-w-5xl mx-auto p-4 md:p-8 animate-fade-in">
      {/* Download Template Button - Mobile Only */}
      <div className="lg:hidden mb-4">
        <button
          onClick={downloadTemplate}
          className="w-full flex items-center justify-center space-x-2 px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-all duration-200 hover:shadow-lg transform hover:-translate-y-0.5"
        >
          <Download className="w-4 h-4" />
          <span className="text-sm font-medium">Download CSV Template</span>
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 md:gap-6">
        {/* Main Upload Area */}
        <div className="lg:col-span-2">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 md:p-6 lg:p-8">
            <h2 className="text-xl md:text-2xl font-bold text-gray-900 mb-2">
              Upload Spreadsheet
            </h2>
            <p className="text-sm md:text-base text-gray-600 mb-6 md:mb-8">
              Upload your CSV file containing shipping orders to get started
            </p>

            {/* Dropzone */}
            <div
              {...getRootProps()}
              className={cn(
                'border-2 border-dashed rounded-lg p-8 md:p-12 text-center transition-all cursor-pointer transform hover:scale-[1.02]',
                isDragActive
                  ? 'border-blue-500 bg-blue-50 scale-[1.02]'
                  : uploading
                  ? 'border-gray-300 bg-gray-50 cursor-not-allowed'
                  : 'border-gray-300 hover:border-blue-400 hover:bg-gray-50'
              )}
            >
              <input {...getInputProps()} />

              {uploading ? (
                <div className="space-y-4">
                  <div className="inline-block animate-spin rounded-full h-10 w-10 md:h-12 md:w-12 border-b-2 border-blue-600"></div>
                  <p className="text-xs md:text-sm text-gray-600">Uploading and processing...</p>
                </div>
              ) : (
                <>
                  <Upload className="w-12 h-12 md:w-16 md:h-16 mx-auto text-gray-400 mb-3 md:mb-4 animate-bounce-slow" />
                  <p className="text-base md:text-lg font-medium text-gray-900 mb-2">
                    {isDragActive ? 'Drop your file here' : 'Drag and drop your CSV file here'}
                  </p>
                  <p className="text-xs md:text-sm text-gray-500 mb-3 md:mb-4">or click to browse</p>
                  <p className="text-xs text-gray-400">CSV files only (max 10MB)</p>
                </>
              )}
            </div>

            {/* Upload Result - PRD 4.1.2: validation summary */}
            {uploadResult && (
              <div className="mt-4 md:mt-6 bg-green-50 border border-green-200 rounded-lg p-4 md:p-6 animate-fade-in transform hover:scale-105 transition-transform duration-200">
                <div className="flex items-start space-x-3">
                  <CheckCircle className="w-5 h-5 md:w-6 md:h-6 text-green-600 flex-shrink-0 mt-0.5" />
                  <div className="flex-1">
                    <h3 className="text-sm md:text-base font-semibold text-green-900 mb-2">
                      Upload Successful!
                    </h3>
                    <div className="space-y-1 text-xs md:text-sm text-green-800">
                      <p>✓ {uploadResult.result.shipments_created} shipments created</p>
                      <p>✓ {uploadResult.session.valid_shipments} validated, {uploadResult.session.warning_shipments} flagged for review</p>
                      {uploadResult.session.error_shipments > 0 && (
                        <p className="text-red-700">{uploadResult.session.error_shipments} errors</p>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Continue Button */}
            <div className="mt-6 md:mt-8 flex justify-end">
              <button
                onClick={handleContinue}
                disabled={!uploadResult}
                className={cn(
                  'w-full sm:w-auto px-4 md:px-6 py-2.5 rounded-lg font-medium text-sm md:text-base transition-all duration-200',
                  uploadResult
                    ? 'bg-blue-600 text-white hover:bg-blue-700 hover:shadow-lg transform hover:-translate-y-0.5'
                    : 'bg-gray-200 text-gray-400 cursor-not-allowed'
                )}
              >
                Continue to Review
              </button>
            </div>
          </div>
        </div>

        {/* Help Sidebar - Hidden on Mobile */}
        <div className="hidden lg:block space-y-4 md:space-y-6">
          {/* Download Template */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 md:p-6">
            <h3 className="text-sm md:text-base font-semibold text-gray-900 mb-3 flex items-center space-x-2">
              <FileText className="w-4 h-4 md:w-5 md:h-5 text-blue-600" />
              <span>CSV Template</span>
            </h3>
            <p className="text-xs md:text-sm text-gray-600 mb-4">
              Download the CSV template, then upload that file. Do not upload HTML files.
            </p>
            <button
              onClick={downloadTemplate}
              className="w-full flex items-center justify-center space-x-2 px-3 md:px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-all duration-200 hover:shadow-md transform hover:-translate-y-0.5"
            >
              <Download className="w-3.5 h-3.5 md:w-4 md:h-4" />
              <span className="text-xs md:text-sm font-medium">Download Template</span>
            </button>
          </div>

          {/* Instructions - compact */}
          <div className="bg-blue-50 rounded-lg border border-blue-200 p-3 md:p-4">
            <h3 className="text-sm md:text-base font-semibold text-blue-900 mb-2 flex items-center space-x-2">
              <AlertCircle className="w-3.5 h-3.5 md:w-4 md:h-4" />
              <span>Instructions</span>
            </h3>
            <p className="text-xs md:text-sm text-blue-800">Download template → Fill data → Upload → Review & continue.</p>
          </div>
        </div>
      </div>
    </div>
  )
}
