import { useStore } from '../../store/useStore'
import { Check } from 'lucide-react'
import { cn } from '../../lib/utils'
import Step1Upload from './Step1Upload'
import Step2Review from './Step2Review'
import Step3Shipping from './Step3Shipping'
import Step4Purchase from './Step4Purchase'

export default function WizardContainer() {
  const { currentStep } = useStore()

  const steps = [
    { number: 1, title: 'Upload' },
    { number: 2, title: 'Review' },
    { number: 3, title: 'Shipping' },
    { number: 4, title: 'Purchase' },
  ]

  return (
    <div className="h-full flex flex-col">
      {/* Stepper */}
      <div className="bg-white border-b border-gray-200 px-4 md:px-8 py-4 md:py-6">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center justify-between">
            {steps.map((step, index) => (
              <div key={step.number} className="flex items-center flex-1">
                <div className="flex items-center">
                  <div
                    className={cn(
                      'w-8 h-8 md:w-10 md:h-10 rounded-full flex items-center justify-center font-semibold transition-all duration-200 text-sm md:text-base',
                      currentStep > step.number
                        ? 'bg-green-600 text-white'
                        : currentStep === step.number
                        ? 'bg-blue-600 text-white animate-pulse-slow'
                        : 'bg-gray-200 text-gray-600'
                    )}
                  >
                    {currentStep > step.number ? (
                      <Check className="w-4 h-4 md:w-5 md:h-5" />
                    ) : (
                      step.number
                    )}
                  </div>
                  <span
                    className={cn(
                      'ml-2 md:ml-3 font-medium text-xs md:text-base hidden sm:inline',
                      currentStep >= step.number
                        ? 'text-gray-900'
                        : 'text-gray-500'
                    )}
                  >
                    {step.title}
                  </span>
                </div>
                {index < steps.length - 1 && (
                  <div
                    className={cn(
                      'flex-1 h-0.5 md:h-1 mx-2 md:mx-4 rounded transition-all duration-200',
                      currentStep > step.number
                        ? 'bg-green-600'
                        : 'bg-gray-200'
                    )}
                  />
                )}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Step Content */}
      <div className="flex-1 overflow-auto bg-gray-50">
        {currentStep === 1 && <Step1Upload />}
        {currentStep === 2 && <Step2Review />}
        {currentStep === 3 && <Step3Shipping />}
        {currentStep === 4 && <Step4Purchase />}
      </div>
    </div>
  )
}
