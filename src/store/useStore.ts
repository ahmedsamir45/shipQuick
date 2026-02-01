import { create } from 'zustand'
import type { UploadSession, Shipment, SavedAddress, SavedPackage } from '../lib/types'

export type WizardStep = 1 | 2 | 3 | 4

interface StoreState {
  // Wizard state
  currentStep: WizardStep
  setCurrentStep: (step: WizardStep) => void
  nextStep: () => void
  previousStep: () => void

  // Session state
  session: UploadSession | null
  setSession: (session: UploadSession | null) => void

  // Shipments state
  shipments: Shipment[]
  setShipments: (shipments: Shipment[]) => void
  updateShipment: (shipmentId: string, data: Partial<Shipment>) => void
  removeShipment: (shipmentId: string) => void

  // Selection state
  selectedShipmentIds: string[]
  setSelectedShipmentIds: (ids: string[]) => void
  toggleShipmentSelection: (id: string) => void
  selectAllShipments: () => void
  clearSelection: () => void

  // Saved presets
  savedAddresses: SavedAddress[]
  setSavedAddresses: (addresses: SavedAddress[]) => void

  savedPackages: SavedPackage[]
  setSavedPackages: (packages: SavedPackage[]) => void

  // Loading state
  isLoading: boolean
  setIsLoading: (loading: boolean) => void

  // Upload state
  uploadProgress: number
  setUploadProgress: (progress: number) => void

  // Reset
  reset: () => void
}

export const useStore = create<StoreState>((set) => ({
  // Wizard
  currentStep: 1,
  setCurrentStep: (step) => set({ currentStep: step }),
  nextStep: () => set((state) => ({ currentStep: Math.min(4, state.currentStep + 1) as WizardStep })),
  previousStep: () => set((state) => ({ currentStep: Math.max(1, state.currentStep - 1) as WizardStep })),

  // Session
  session: null,
  setSession: (session) => set({ session }),

  // Shipments
  shipments: [],
  setShipments: (shipments) => set({ shipments }),
  updateShipment: (shipmentId, data) =>
    set((state) => ({
      shipments: state.shipments.map((s) =>
        s.id === shipmentId ? { ...s, ...data } : s
      ),
    })),
  removeShipment: (shipmentId) =>
    set((state) => ({
      shipments: state.shipments.filter((s) => s.id !== shipmentId),
    })),

  // Selection
  selectedShipmentIds: [],
  setSelectedShipmentIds: (ids) => set({ selectedShipmentIds: ids }),
  toggleShipmentSelection: (id) =>
    set((state) => ({
      selectedShipmentIds: state.selectedShipmentIds.includes(id)
        ? state.selectedShipmentIds.filter((i) => i !== id)
        : [...state.selectedShipmentIds, id],
    })),
  selectAllShipments: () =>
    set((state) => ({
      selectedShipmentIds: state.shipments.map((s) => s.id),
    })),
  clearSelection: () => set({ selectedShipmentIds: [] }),

  // Saved presets
  savedAddresses: [],
  setSavedAddresses: (addresses) => set({ savedAddresses: addresses }),

  savedPackages: [],
  setSavedPackages: (packages) => set({ savedPackages: packages }),

  // Loading
  isLoading: false,
  setIsLoading: (loading) => set({ isLoading: loading }),

  // Upload progress
  uploadProgress: 0,
  setUploadProgress: (progress) => set({ uploadProgress: progress }),

  // Reset
  reset: () =>
    set({
      currentStep: 1,
      session: null,
      shipments: [],
      selectedShipmentIds: [],
      uploadProgress: 0,
    }),
}))
