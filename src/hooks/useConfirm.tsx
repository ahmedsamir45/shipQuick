import { useState, useCallback } from 'react'
import ConfirmDialog from '../components/ui/ConfirmDialog'

interface ConfirmOptions {
  title: string
  message: string
  confirmText?: string
  cancelText?: string
  variant?: 'danger' | 'warning' | 'info'
}

export function useConfirm() {
  const [confirmState, setConfirmState] = useState<{
    isOpen: boolean
    options: ConfirmOptions
    onConfirm: () => void
  } | null>(null)

  const confirm = useCallback((options: ConfirmOptions): Promise<boolean> => {
    return new Promise((resolve) => {
      setConfirmState({
        isOpen: true,
        options,
        onConfirm: () => {
          resolve(true)
          setConfirmState(null)
        },
      })

      // Auto-reject on close without confirm
      setTimeout(() => {
        if (confirmState?.isOpen) {
          resolve(false)
        }
      }, 100)
    })
  }, [confirmState])

  const handleClose = useCallback(() => {
    setConfirmState(null)
  }, [])

  const ConfirmComponent = confirmState ? (
    <ConfirmDialog
      isOpen={confirmState.isOpen}
      onClose={handleClose}
      onConfirm={confirmState.onConfirm}
      title={confirmState.options.title}
      message={confirmState.options.message}
      confirmText={confirmState.options.confirmText}
      cancelText={confirmState.options.cancelText}
      variant={confirmState.options.variant}
    />
  ) : null

  return { confirm, ConfirmComponent }
}
