import { useCallback, useEffect, useState } from "react"
import { Trash2 } from "lucide-react"
import { ImageUploadSection } from "@/components/ImageUploadSection"
import { ResultsSection } from "@/components/ResultsSection"
import { GoalsPanel } from "@/components/GoalsPanel"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { Button } from "@/components/ui/Button"
import { defaultGoals } from "@/data/nutritionData"
import { useAuth, useAuthedFetch } from "@/context/AuthContext"

export function DashboardPage() {
  const { user, token, apiBaseUrl } = useAuth()
  const authedFetch = useAuthedFetch()
  const [currentView, setCurrentView] = useState("scan")
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [isSaving, setIsSaving] = useState(false)
  const [nutritionData, setNutritionData] = useState(null)
  // ID of the saved scan being shown (null = not saved yet). Prevents saving the same scan twice.
  const [savedDocId, setSavedDocId] = useState(null)
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

  const showResults = (data, docId = null) => {
    setNutritionData(data)
    setSavedDocId(docId)
    setCurrentView("results")
    window.scrollTo({ top: 0, behavior: "smooth" })
  }

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

      showResults(await response.json())
    } catch (error) {
      console.error(error)
      alert("Something went wrong while trying to analyze the nutrition label.")
    } finally {
      setIsAnalyzing(false)
    }
  }

  const handleSave = async () => {
    if (!nutritionData || savedDocId) {
      return
    }

    setIsSaving(true)
    try {
      const saved = await authedFetch("/api/docs", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title: nutritionData.productName,
          nutritionData,
        }),
      })
      setSavedDocId(saved.id)
      await loadDocuments()
    } catch (error) {
      console.error(error)
      alert("Unable to save this scan right now.")
    } finally {
      setIsSaving(false)
    }
  }

  const handleOpenDoc = async (doc) => {
    setDocError("")
    try {
      const fullDoc = await authedFetch(`/api/docs/${doc.id}`)
      showResults(fullDoc.nutritionData, fullDoc.id)
    } catch (error) {
      setDocError(error.message)
    }
  }

  const handleDeleteDoc = async (doc) => {
    if (!window.confirm(`Delete "${doc.title}" from your history?`)) {
      return
    }

    setDocError("")
    try {
      await authedFetch(`/api/docs/${doc.id}`, { method: "DELETE" })
      setDocuments((prev) => prev.filter((d) => d.id !== doc.id))
      // If the deleted scan is open on screen, allow it to be saved again
      if (savedDocId === doc.id) {
        setSavedDocId(null)
      }
    } catch (error) {
      setDocError(error.message)
    }
  }

  const handleBackToScan = () => {
    setCurrentView("scan")
    setNutritionData(null)
    setSavedDocId(null)
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
          isSaved={Boolean(savedDocId)}
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
                      className={`flex items-center gap-2 rounded-xl border bg-muted/30 p-4 transition-colors hover:border-primary/50 ${
                        doc.id === savedDocId ? "border-primary" : "border-border"
                      }`}
                    >
                      <button
                        type="button"
                        onClick={() => handleOpenDoc(doc)}
                        className="min-w-0 flex-1 text-left"
                      >
                        <h3 className="truncate text-base font-semibold text-foreground">
                          {doc.title}
                        </h3>
                        <p className="mt-2 text-xs text-muted-foreground">
                          {doc.calories != null && `${doc.calories} kcal · `}
                          {doc.healthScore != null && `Score ${doc.healthScore} · `}
                          Scanned {new Date(doc.createdAt).toLocaleString()}
                        </p>
                      </button>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => handleDeleteDoc(doc)}
                        aria-label={`Delete ${doc.title}`}
                      >
                        <Trash2 className="h-4 w-4 text-muted-foreground" />
                      </Button>
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
