import { useState, useEffect } from "react"
import { Navbar } from "@/components/Navbar"
import { HeroSection } from "@/components/HeroSection"
import { ImageUploadSection } from "@/components/ImageUploadSection"
import { ResultsSection } from "@/components/ResultsSection"
import { GoalsPanel } from "@/components/GoalsPanel"
import { Footer } from "@/components/Footer"
import { defaultGoals } from "@/data/nutritionData"

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
    
    try {
      const formData = new FormData()

      formData.append("image", image)
      formData.append("foodName", foodName)

      const response = await fetch("http://localhost:8000/api/analyze", {
        method: "POST",
        body: formData
      })

      if (!response.ok) {
        throw new Error("Failed to analyze nutrition label")
      }

      const data = await response.json()

      setNutritionData(data)
      setCurrentView("results")

      window.scrollTo({ top: 0, behavior: "smooth" })
    } catch (error) {
      console.error(error)
      alert("Something went wrong while trying to analyze the nutrition label.")
    } finally {
      setIsAnalyzing(false)
    }
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
