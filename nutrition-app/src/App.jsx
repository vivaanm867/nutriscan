import { useState, useEffect } from "react"
import { Navbar } from "@/components/Navbar"
import { HeroSection } from "@/components/HeroSection"
import { ImageUploadSection } from "@/components/ImageUploadSection"
import { ResultsSection } from "@/components/ResultsSection"
import { GoalsPanel } from "@/components/GoalsPanel"
import { Footer } from "@/components/Footer"
import { sampleNutritionData, defaultGoals } from "@/data/nutritionData"

function App() {
  const [darkMode, setDarkMode] = useState(false)
  const [currentView, setCurrentView] = useState("home") // "home" | "results"
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [nutritionData, setNutritionData] = useState(null)
  const [goals, setGoals] = useState(defaultGoals)

  // Apply dark mode class to html element
  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add("dark")
    } else {
      document.documentElement.classList.remove("dark")
    }
  }, [darkMode])

  // Check system preference on mount
  useEffect(() => {
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches
    setDarkMode(prefersDark)
  }, [])

  const handleStartScan = () => {
    const scanSection = document.getElementById("scan")
    if (scanSection) {
      scanSection.scrollIntoView({ behavior: "smooth" })
    }
  }

  const handleAnalyze = async ({ image, foodName }) => {
    setIsAnalyzing(true)
    
    // Simulate API call with delay
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    // Use sample data (in a real app, this would be the API response)
    setNutritionData({
      ...sampleNutritionData,
      productName: foodName || sampleNutritionData.productName,
    })
    
    setIsAnalyzing(false)
    setCurrentView("results")
    
    // Scroll to top of results
    window.scrollTo({ top: 0, behavior: "smooth" })
  }

  const handleBackToHome = () => {
    setCurrentView("home")
    setNutritionData(null)
  }

  return (
    <div className="min-h-screen bg-background">
      <Navbar darkMode={darkMode} setDarkMode={setDarkMode} />
      
      {currentView === "home" ? (
        <>
          <main>
            <HeroSection onStartScan={handleStartScan} />
            <ImageUploadSection 
              onAnalyze={handleAnalyze} 
              isAnalyzing={isAnalyzing} 
            />
            <GoalsPanel goals={goals} setGoals={setGoals} />
          </main>
        </>
      ) : (
        <main>
          <ResultsSection 
            nutritionData={nutritionData} 
            onBack={handleBackToHome}
          />
        </main>
      )}
      
      <Footer />
    </div>
  )
}

export default App
