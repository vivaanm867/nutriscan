import { useCallback, useEffect, useState } from "react"
import { ImageUploadSection } from "@/components/ImageUploadSection"
import { ResultsSection } from "@/components/ResultsSection"
import { GoalsPanel } from "@/components/GoalsPanel"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { defaultGoals } from "@/data/nutritionData"
import { useAuth, useAuthedFetch } from "@/context/AuthContext"

export function DashboardPage() {
  const { user, token, apiBaseUrl } = useAuth()
  const authedFetch = useAuthedFetch()
  const [currentView, setCurrentView] = useState("scan")
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [isSaving, setIsSaving] = useState(false)
  const [nutritionData, setNutritionData] = useState(null)
  const [goals, setGoals] = useState(defaultGoals)
  const [documents, setDocuments] = useState([])
  const [docError, setDocError] = useState("")

  const loadDocuments = useCallback(async () => {
    setDocError("")
    try {
      const data = await authedFetch("/api/docs")
      setDocuments(data)
    } catch (error) {
      setDocError(error.message)
    }
  }, [authedFetch])

  useEffect(() => {
    loadDocuments()
  }, [loadDocuments])

  const handleAnalyze = async ({ image, foodName }) => {
    setIsAnalyzing(true)

    try {
      const formData = new FormData()
      if (image) {
        formData.append("image", image)
      }
      formData.append("foodName", foodName)

      const response = await fetch(`${apiBaseUrl}/api/analyze`, {
        method: "POST",
        body: formData,
        headers: {
          Authorization: `Bearer ${token}`,
        },
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

  const handleSave = async () => {
    if (!nutritionData) {
      return
    }

    setIsSaving(true)
    try {
      await authedFetch("/api/docs", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title: nutritionData.productName,
          fileSize: null,
          thumbnailUrl: null,
          nutritionData,
        }),
      })
      await loadDocuments()
    } catch (error) {
      console.error(error)
      alert("Unable to save this scan right now.")
    } finally {
      setIsSaving(false)
    }
  }

  const handleBackToScan = () => {
    setCurrentView("scan")
    setNutritionData(null)
  }

  return (
    <div className="space-y-10">
      <section className="bg-muted/30 py-8">
        <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
          <h1 className="text-3xl font-bold text-foreground">
            Welcome back{user?.name ? `, ${user.name}` : ""}.
          </h1>
          <p className="mt-2 text-muted-foreground">
            Scan a new label or pick up where you left off in your history.
          </p>
        </div>
      </section>

      {currentView === "scan" ? (
        <>
          <ImageUploadSection onAnalyze={handleAnalyze} isAnalyzing={isAnalyzing} />
          <GoalsPanel goals={goals} setGoals={setGoals} />
        </>
      ) : (
        <ResultsSection
          nutritionData={nutritionData}
          onBack={handleBackToScan}
          onSave={handleSave}
          isSaving={isSaving}
        />
      )}

      <section className="bg-background pb-16">
        <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
          <Card>
            <CardHeader>
              <CardTitle>Saved scans</CardTitle>
            </CardHeader>
            <CardContent>
              {docError && (
                <p className="mb-4 rounded-lg bg-destructive/10 px-3 py-2 text-sm text-destructive">
                  {docError}
                </p>
              )}
              {documents.length === 0 ? (
                <p className="text-sm text-muted-foreground">
                  No scans yet. Save your first scan to build your history.
                </p>
              ) : (
                <div className="grid gap-4 sm:grid-cols-2">
                  {documents.map((doc) => (
                    <div
                      key={doc.id}
                      className="rounded-xl border border-border bg-muted/30 p-4"
                    >
                      <h3 className="text-base font-semibold text-foreground">
                        {doc.title}
                      </h3>
                      <p className="mt-2 text-xs text-muted-foreground">
                        Scanned {new Date(doc.createdAt).toLocaleString()}
                      </p>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </section>
    </div>
  )
}
