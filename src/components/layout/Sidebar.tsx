import {
  LayoutDashboard,
  Tag,
  Upload,
  History,
  DollarSign,
  CreditCard,
  Settings,
  HelpCircle,
  X
} from 'lucide-react'
import { cn } from '../../lib/utils'

const menuItems = [
  { icon: LayoutDashboard, label: 'Dashboard', active: false, disabled: true },
  { icon: Tag, label: 'Create a Label', active: false, disabled: true },
  { icon: Upload, label: 'Upload Spreadsheet', active: true, disabled: false },
  { icon: History, label: 'Order History', active: false, disabled: true },
  { icon: DollarSign, label: 'Pricing', active: false, disabled: true },
  { icon: CreditCard, label: 'Billing', active: false, disabled: true },
  { icon: Settings, label: 'Settings', active: false, disabled: true },
  { icon: HelpCircle, label: 'Support & Help', active: false, disabled: true },
]

interface SidebarProps {
  isOpen?: boolean
  onClose?: () => void
}

export default function Sidebar({ isOpen = false, onClose }: SidebarProps) {
  return (
    <>
      {/* Mobile Overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 lg:hidden animate-fade-in"
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <div
        className={cn(
          'fixed lg:static inset-y-0 left-0 z-50 w-64 bg-white border-r border-gray-200 flex flex-col transform transition-transform duration-300 ease-in-out lg:transform-none',
          isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
        )}
      >
        {/* Logo */}
        <div className="h-14 md:h-16 flex items-center justify-between px-4 md:px-6 border-b border-gray-200">
          <div className="flex items-center space-x-2">
            <div className="w-7 h-7 md:w-8 md:h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <Tag className="w-4 h-4 md:w-5 md:h-5 text-white" />
            </div>
            <span className="font-bold text-base md:text-lg text-gray-900">ShipQuick</span>
          </div>

          {/* Close button - Mobile Only */}
          <button
            onClick={onClose}
            className="lg:hidden p-1.5 hover:bg-gray-100 rounded-lg transition-colors"
            aria-label="Close menu"
          >
            <X className="w-5 h-5 text-gray-700" />
          </button>
        </div>

        {/* Menu Items */}
        <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
          {menuItems.map((item) => {
            const Icon = item.icon
            return (
              <button
                key={item.label}
                disabled={item.disabled}
                className={cn(
                  'w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors',
                  item.active
                    ? 'bg-blue-50 text-blue-700'
                    : item.disabled
                    ? 'text-gray-400 cursor-not-allowed opacity-50'
                    : 'text-gray-700 hover:bg-gray-100'
                )}
              >
                <Icon className="w-5 h-5 flex-shrink-0" />
                <span>{item.label}</span>
              </button>
            )
          })}
        </nav>

        {/* Footer */}
        <div className="p-4 border-t border-gray-200">
          <div className="text-xs text-gray-500 text-center">
            <p>© 2026 ShipQuick</p>
            <p className="mt-1">Version 1.0.0</p>
          </div>
        </div>
      </div>
    </>
  )
}
