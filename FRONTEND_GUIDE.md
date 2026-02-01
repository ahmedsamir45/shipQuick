# Frontend Implementation Guide

## Overview

This is a production-ready React + TypeScript + Tailwind CSS frontend for the Bulk Shipping Label Platform.

## Tech Stack

- **React 18** with TypeScript
- **Tailwind CSS** for styling
- **Zustand** for state management
- **TanStack Table** for data tables
- **Radix UI** for accessible components
- **Vite** for blazing-fast dev experience
- **Axios** for API calls
- **React Router** for navigation
- **Sonner** for toast notifications
- **Lucide React** for icons

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── ui/              # Reusable UI components (buttons, modals, etc.)
│   │   ├── layout/          # Layout components (Sidebar, Header)
│   │   ├── wizard/          # Wizard step components
│   │   └── common/          # Common components (StatusBadge, etc.)
│   ├── lib/
│   │   ├── api.ts           # API client & endpoints
│   │   ├── types.ts         # TypeScript interfaces
│   │   └── utils.ts         # Utility functions
│   ├── store/
│   │   └── useStore.ts      # Zustand store
│   ├── App.tsx              # Main App component
│   ├── main.tsx             # Entry point
│   └── index.css            # Global styles
├── package.json
├── vite.config.ts
├── tailwind.config.js
└── tsconfig.json
```

## Installation

```bash
cd frontend
npm install
```

## Running the Application

```bash
# Development server (with backend proxy)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

The frontend will run on `http://localhost:3000` and proxy API requests to `http://localhost:8000`.

## Key Features

### 1. State Management (Zustand)

Global state includes:
- Current wizard step
- Upload session ID
- Shipments data
- Selected rows
- Saved addresses & packages
- Loading states

### 2. API Integration

All backend endpoints are integrated:
- Session management
- CSV upload
- Shipment CRUD
- Bulk operations
- Saved presets
- Purchase flow

### 3. UI Components

**Reusable UI Components:**
- Button
- Input
- Modal/Dialog
- Select/Dropdown
- Checkbox
- Table
- Card
- Badge

**Layout Components:**
- Sidebar with navigation
- Header with user info
- Main content area
- Wizard stepper

**Wizard Steps:**
- Step 1: Upload Spreadsheet
- Step 2: Review & Edit Records
- Step 3: Select Shipping Provider
- Step 4: Purchase & Confirmation

### 4. Features Implemented

✅ **Step 1: Upload**
- Drag & drop CSV upload
- File validation
- Upload progress
- Validation summary
- Help section with template download

✅ **Step 2: Review & Edit**
- Data table with sorting/filtering
- Row selection
- Edit address modal
- Edit package modal
- Bulk operations (address, package, delete)
- Search functionality
- Pagination

✅ **Step 3: Shipping Selection**
- Service selection per row
- Live price updates
- Total calculation
- Bulk service changes
- Pricing rules display

✅ **Step 4: Purchase**
- Label size selection
- Terms & conditions
- Grand total display
- Success confirmation
- Download/print simulation

### 5. UX Enhancements

- **Loading States**: Spinners and skeletons
- **Empty States**: Helpful messages when no data
- **Error States**: Clear error messages
- **Success States**: Confirmation feedback
- **Smooth Transitions**: Page transitions and animations
- **Responsive Design**: Mobile-friendly (though optimized for desktop)
- **Keyboard Navigation**: Accessible interactions
- **Toast Notifications**: Real-time feedback

## API Integration

The frontend connects to the Django backend at `http://localhost:8000/api/`.

**Main API Endpoints Used:**

```typescript
// Sessions
POST   /api/sessions/                  // Create session
POST   /api/sessions/{id}/upload_csv/  // Upload CSV
POST   /api/sessions/{id}/purchase/    // Purchase
GET    /api/sessions/{id}/summary/     // Get summary

// Shipments
GET    /api/shipments/?session={id}    // List shipments
PUT    /api/shipments/{id}/            // Update shipment
DELETE /api/shipments/{id}/            // Delete shipment
POST   /api/shipments/bulk_delete/     // Bulk delete
POST   /api/shipments/bulk_update_address/
POST   /api/shipments/bulk_update_package/
POST   /api/shipments/bulk_update_service/

// Presets
GET    /api/saved-addresses/           // List saved addresses
GET    /api/saved-packages/            // List saved packages
```

## Component Architecture

### Wizard Flow

```
App.tsx
  └── WizardContainer
        ├── Sidebar (persistent)
        ├── Header (persistent)
        └── Content (changes per step)
              ├── Step1Upload
              ├── Step2Review
              ├── Step3Shipping
              └── Step4Purchase
```

### State Flow

```
User Action
    ↓
Component Event Handler
    ↓
Zustand Store Action
    ↓
API Call (if needed)
    ↓
Store State Update
    ↓
Component Re-renders
```

### Data Table (TanStack Table)

```typescript
// Features used:
- Column definitions
- Row selection
- Sorting
- Filtering
- Pagination
- Custom cells (Status badges, actions)
- Bulk selection
```

## Styling Guidelines

### Tailwind Classes

Use semantic Tailwind classes with the custom theme:

```tsx
// Primary button
<button className="bg-primary text-primary-foreground hover:bg-primary/90">

// Card
<div className="bg-card text-card-foreground rounded-lg border shadow-sm">

// Input
<input className="border-input bg-background">
```

### Component Variants (CVA)

Use `class-variance-authority` for component variants:

```typescript
const buttonVariants = cva(
  'base-classes',
  {
    variants: {
      variant: {
        default: 'bg-primary',
        outline: 'border bg-transparent',
      },
      size: {
        default: 'h-10 px-4',
        sm: 'h-9 px-3',
      },
    },
  }
)
```

## Error Handling

All API calls are wrapped with try-catch:

```typescript
try {
  const response = await api.uploadCSV(sessionId, file)
  toast.success('CSV uploaded successfully!')
  // Update state
} catch (error) {
  toast.error(error.message || 'Upload failed')
  // Handle error state
}
```

## Testing Strategy

### Manual Testing

1. **Upload Flow**
   - Upload valid CSV
   - Upload invalid CSV
   - Cancel upload

2. **Edit Flow**
   - Edit single shipment
   - Edit address
   - Edit package (verify shipping recalculates)
   - Delete shipment

3. **Bulk Operations**
   - Select multiple rows
   - Bulk change address
   - Bulk change package
   - Bulk delete

4. **Shipping Selection**
   - Change service per row
   - Bulk change service
   - Verify price updates

5. **Purchase**
   - Complete purchase
   - Verify session locks
   - Try to edit locked session

### Browser Testing

- Chrome (primary)
- Firefox
- Safari
- Edge

## Performance Optimization

1. **Code Splitting**: Lazy load wizard steps
2. **Memoization**: Use `useMemo` for expensive calculations
3. **Virtualization**: For large tables (optional, TanStack Table supports it)
4. **Debouncing**: Search input debounced
5. **Optimistic Updates**: UI updates before API confirms

## Deployment

### Build

```bash
npm run build
```

Output: `dist/` folder

### Deploy Options

1. **Vercel** (recommended)
   ```bash
   vercel --prod
   ```

2. **Netlify**
   ```bash
   netlify deploy --prod
   ```

3. **Static Hosting**
   - Upload `dist/` folder to any static host
   - Configure API proxy in production

### Environment Variables

Create `.env.production`:

```env
VITE_API_BASE_URL=https://your-backend-domain.com
```

Update `src/lib/api.ts`:

```typescript
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
```

## Future Enhancements

- [ ] Dark mode toggle
- [ ] User authentication
- [ ] Dashboard with analytics
- [ ] Order history page
- [ ] Pricing calculator
- [ ] Settings page
- [ ] Multi-language support (i18n)
- [ ] Advanced filtering
- [ ] Export to Excel
- [ ] Batch processing progress
- [ ] Real-time updates (WebSockets)
- [ ] Drag-to-reorder rows
- [ ] Column customization
- [ ] Save filters/views
- [ ] Keyboard shortcuts help modal

## Troubleshooting

### CORS Issues

If you see CORS errors, ensure the backend has CORS properly configured in `settings.py`:

```python
CORS_ALLOWED_ORIGINS = ['http://localhost:3000']
```

### API Connection Failed

1. Verify backend is running: `python manage.py runserver`
2. Check proxy config in `vite.config.ts`
3. Verify API base URL in `src/lib/api.ts`

### Build Errors

1. Delete `node_modules` and reinstall:
   ```bash
   rm -rf node_modules package-lock.json
   npm install
   ```

2. Clear Vite cache:
   ```bash
   rm -rf .vite
   ```

## Code Quality

### TypeScript

- All components are fully typed
- No `any` types (except in edge cases)
- Proper interface definitions
- Type inference where appropriate

### Code Style

- ESLint for linting
- Prettier for formatting (recommended)
- Consistent naming conventions
- Component files in PascalCase
- Utility files in camelCase

### Best Practices

✅ Use semantic HTML
✅ Accessible components (ARIA labels)
✅ Keyboard navigation support
✅ Loading states everywhere
✅ Error boundaries (optional)
✅ Clean component structure
✅ Reusable components
✅ Single responsibility principle

## Support

For questions or issues:
1. Check the code comments
2. Review the backend [README.md](../README.md)
3. Test API endpoints with [API_TESTING_GUIDE.md](../API_TESTING_GUIDE.md)

---

**Frontend Status: Production-Ready** ✅
