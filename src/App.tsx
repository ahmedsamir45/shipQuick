import { useEffect } from 'react'
import { useStore } from './store/useStore'
import { api } from './lib/api'
import { toast } from 'sonner'
import MainLayout from './components/layout/MainLayout'
import WizardContainer from './components/wizard/WizardContainer'

function App() {
  const { setSavedAddresses, setSavedPackages } = useStore()

  // Load saved presets on app start
  useEffect(() => {
    const loadPresets = async () => {
      try {
        const [addresses, packages] = await Promise.all([
          api.getSavedAddresses(),
          api.getSavedPackages(),
        ])
        setSavedAddresses(addresses)
        setSavedPackages(packages)
      } catch (error) {
        console.error('Failed to load presets:', error)
        toast.error('Failed to load saved presets')
      }
    }

    loadPresets()
  }, [setSavedAddresses, setSavedPackages])

  return (
    <div className="h-screen w-full bg-gray-50">
      <MainLayout>
        <WizardContainer />
      </MainLayout>
    </div>
  )
}

export default App
