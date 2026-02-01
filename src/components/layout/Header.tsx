import { User, Wallet, Menu } from 'lucide-react'
import { useStore } from '../../store/useStore'

interface HeaderProps {
  onMenuClick?: () => void
}

export default function Header({ onMenuClick }: HeaderProps) {
  const { currentStep } = useStore()

  const stepTitles = {
    1: 'Upload Spreadsheet (Step 1 of 4)',
    2: 'Review and Edit File (Step 2 of 4)',
    3: 'Select Shipping Provider (Step 3 of 4)',
    4: 'Purchase Labels (Step 4 of 4)',
  }

  const mobileStepTitles = {
    1: 'Upload (1/4)',
    2: 'Review (2/4)',
    3: 'Shipping (3/4)',
    4: 'Purchase (4/4)',
  }

  return (
    <header className="h-14 md:h-16 bg-white border-b border-gray-200 flex items-center justify-between px-3 md:px-6">
      <div className="flex items-center space-x-3">
        {/* Hamburger Menu - Mobile Only */}
        <button
          onClick={onMenuClick}
          className="lg:hidden p-2 hover:bg-gray-100 rounded-lg transition-colors"
          aria-label="Toggle menu"
        >
          <Menu className="w-5 h-5 text-gray-700" />
        </button>

        {/* Breadcrumb / Title */}
        <div>
          <h1 className="text-base md:text-xl font-semibold text-gray-900">
            <span className="hidden sm:inline">{stepTitles[currentStep as keyof typeof stepTitles]}</span>
            <span className="sm:hidden">{mobileStepTitles[currentStep as keyof typeof mobileStepTitles]}</span>
          </h1>
        </div>
      </div>

      {/* User Info */}
      <div className="flex items-center space-x-2 md:space-x-6">
        {/* Account Balance - Hidden on small mobile */}
        <div className="hidden xs:flex items-center space-x-2 px-2 md:px-4 py-1.5 md:py-2 bg-green-50 rounded-lg">
          <Wallet className="w-3.5 h-3.5 md:w-4 md:h-4 text-green-600" />
          <div>
            <p className="text-xs text-green-600 font-medium hidden sm:block">Balance</p>
            <p className="text-xs md:text-sm font-bold text-green-700">$1,250.00</p>
          </div>
        </div>

        {/* User Avatar */}
        <div className="flex items-center space-x-2 md:space-x-3">
          <div className="text-right hidden md:block">
            <p className="text-sm font-medium text-gray-900">Demo User</p>
            <p className="text-xs text-gray-500">demo@shipquick.com</p>
          </div>
          <div className="w-8 h-8 md:w-10 md:h-10 bg-blue-600 rounded-full flex items-center justify-center">
            <User className="w-4 h-4 md:w-5 md:h-5 text-white" />
          </div>
        </div>
      </div>
    </header>
  )
}
