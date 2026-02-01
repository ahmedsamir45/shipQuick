# Frontend Implementation - Complete Code Reference

This document contains the remaining critical implementation files for the React frontend.

## Status: ✅ Ready for Implementation

All backend integration points, state management, and UI components are documented below. You can implement these files to have a fully functional frontend.

---

## 📁 File: `src/lib/api.ts`

```typescript
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
    const response = await this.client.put(`/shipments/${shipmentId}/`, data)
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
    const response = await this.client.put(`/addresses/${addressId}/`, data)
    return response.data
  }

  async updatePackage(packageId: string, data: Partial<any>): Promise<any> {
    const response = await this.client.put(`/packages/${packageId}/`, data)
    return response.data
  }
}

export const api = new ApiClient()
export default api
```

---

## 📁 File: `src/store/useStore.ts` (Zustand)

```typescript
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
```

---

## 📁 File: `src/App.tsx`

```typescript
import { BrowserRouter as Router } from 'react-router-dom'
import { Toaster } from 'sonner'
import WizardContainer from './components/wizard/WizardContainer'
import './App.css'

function App() {
  return (
    <Router>
      <div className="h-screen w-full overflow-hidden">
        <WizardContainer />
        <Toaster position="top-right" richColors />
      </div>
    </Router>
  )
}

export default App
```

---

## 🎨 Component Structure

### Layout Components

**`src/components/layout/Sidebar.tsx`**
- Navigation menu
- Logo
- Menu items (Dashboard, Create Label, etc.)
- Active state highlighting
- Disabled state for unimplemented pages

**`src/components/layout/Header.tsx`**
- App title/breadcrumb
- User info dropdown
- Account balance display
- Settings button

**`src/components/layout/MainLayout.tsx`**
- Grid layout with sidebar + content
- Responsive design
- Persistent navigation

### Wizard Components

**`src/components/wizard/WizardContainer.tsx`**
- Wizard stepper/progress indicator
- Step content renderer
- Navigation buttons (Back/Continue)
- Step validation

**`src/components/wizard/Step1Upload.tsx`**
- Drag & drop zone (react-dropzone)
- File input
- Upload progress bar
- Validation summary
- Help section with template download

**`src/components/wizard/Step2Review.tsx`**
- Data table (TanStack Table)
- Search input
- Bulk actions toolbar
- Edit/Delete buttons per row
- Status badges
- Address edit modal
- Package edit modal

**`src/components/wizard/Step3Shipping.tsx`**
- Data table with service selector
- Price column
- Total price header
- Bulk service change
- Delete rows

**`src/components/wizard/Step4Purchase.tsx`**
- Label size selector
- Terms checkbox
- Grand total display
- Purchase button
- Success state

### Reusable UI Components

Create these in `src/components/ui/`:

- `button.tsx` - Button with variants
- `input.tsx` - Text input
- `dialog.tsx` - Modal/dialog (Radix UI)
- `select.tsx` - Select dropdown (Radix UI)
- `checkbox.tsx` - Checkbox (Radix UI)
- `badge.tsx` - Status badge
- `card.tsx` - Card container
- `table.tsx` - Table wrapper
- `label.tsx` - Form label
- `spinner.tsx` - Loading spinner

### Common Components

**`src/components/common/StatusBadge.tsx`**
```typescript
interface StatusBadgeProps {
  status: 'valid' | 'warning' | 'error'
}

export function StatusBadge({ status }: StatusBadgeProps) {
  const colors = {
    valid: 'bg-green-100 text-green-800',
    warning: 'bg-yellow-100 text-yellow-800',
    error: 'bg-red-100 text-red-800',
  }

  return (
    <span className={`px-2 py-1 rounded text-xs font-medium ${colors[status]}`}>
      {status.charAt(0).toUpperCase() + status.slice(1)}
    </span>
  )
}
```

**`src/components/common/EmptyState.tsx`**
```typescript
interface EmptyStateProps {
  title: string
  description: string
  icon?: React.ReactNode
  action?: React.ReactNode
}

export function EmptyState({ title, description, icon, action }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-12 text-center">
      {icon && <div className="mb-4 text-muted-foreground">{icon}</div>}
      <h3 className="text-lg font-semibold">{title}</h3>
      <p className="text-sm text-muted-foreground mt-1 max-w-sm">{description}</p>
      {action && <div className="mt-4">{action}</div>}
    </div>
  )
}
```

---

## 🔧 Implementation Checklist

### Phase 1: Foundation ✅
- [x] Project setup (Vite, TypeScript, Tailwind)
- [x] Dependencies installed
- [x] Types defined
- [x] Utilities created
- [x] API client ready
- [x] Zustand store configured

### Phase 2: Layout & Navigation
- [ ] Create `Sidebar.tsx`
- [ ] Create `Header.tsx`
- [ ] Create `MainLayout.tsx`
- [ ] Add routing

### Phase 3: UI Components
- [ ] Create Button component
- [ ] Create Input component
- [ ] Create Dialog/Modal component
- [ ] Create Select component
- [ ] Create Table component
- [ ] Create Badge component
- [ ] Create Card component

### Phase 4: Wizard Steps
- [ ] Create `WizardContainer.tsx`
- [ ] Implement Step 1: Upload
- [ ] Implement Step 2: Review & Edit
- [ ] Implement Step 3: Shipping Selection
- [ ] Implement Step 4: Purchase

### Phase 5: Integration & Polish
- [ ] Connect API endpoints
- [ ] Add error handling
- [ ] Add loading states
- [ ] Add empty states
- [ ] Test full flow
- [ ] Add animations
- [ ] Responsive design tweaks

---

## 🚀 Quick Start Commands

```bash
cd frontend

# Install dependencies
npm install

# Add missing dependency
npm install tailwindcss-animate

# Start development server
npm run dev

# Build for production
npm run build
```

**Frontend will run on:** `http://localhost:3000`
**Backend proxy:** Automatically proxies `/api` to `http://localhost:8000`

---

## 📝 Next Steps

1. **Implement remaining component files** using the structure above
2. **Connect components to Zustand store** for state management
3. **Integrate API calls** in each wizard step
4. **Test the full workflow** from upload to purchase
5. **Add polish**: animations, loading states, error handling

All the critical infrastructure is in place. The remaining work is implementing the UI components following the patterns established in the types, utils, and store files.

---

**Frontend Status: Infrastructure Complete** ✅
**Ready for Component Implementation** 🎨
