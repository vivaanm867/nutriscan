import { ArrowLeft, Download, Share2 } from "lucide-react"
import { Button } from "@/components/ui/Button"
import { MacronutrientCards } from "@/components/MacronutrientCards"
import { DailyValueSection } from "@/components/DailyValueSection"
import { MicronutrientSection } from "@/components/MicronutrientSection"
import { IngredientCards } from "@/components/IngredientCards"
import { NutritionSummary } from "@/components/NutritionSummary"

export function ResultsSection({ nutritionData, onBack, onSave, isSaving }) {
  return (
    <section id="results" className="bg-background py-16 sm:py-24">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="icon" onClick={onBack} aria-label="Go back">
              <ArrowLeft className="h-5 w-5" />
            </Button>
            <div>
              <h2 className="text-2xl font-bold text-foreground sm:text-3xl">
                Analysis Results
              </h2>
              <p className="text-muted-foreground">
                {nutritionData.brand} - {nutritionData.servingSize}
              </p>
            </div>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" size="sm" className="gap-2">
              <Share2 className="h-4 w-4" />
              Share
            </Button>
            <Button variant="outline" size="sm" className="gap-2">
              <Download className="h-4 w-4" />
              Export
            </Button>
          </div>
        </div>

        {/* Summary Card */}
        <div className="mb-8">
          <NutritionSummary 
            insights={nutritionData.insights} 
            productName={nutritionData.productName}
          />
        </div>

        {/* Macro Cards */}
        <div className="mb-8">
          <h3 className="mb-4 text-lg font-semibold text-foreground">
            Macronutrients
          </h3>
          <MacronutrientCards macros={nutritionData.macronutrients} />
        </div>

        {/* Two Column Layout */}
        <div className="grid gap-8 lg:grid-cols-2">
          {/* Daily Values */}
          <DailyValueSection macros={nutritionData.macronutrients} />
          
          {/* Micronutrients */}
          <MicronutrientSection micronutrients={nutritionData.micronutrients} />
        </div>

        {/* Ingredients */}
        <div className="mt-8">
          <IngredientCards ingredients={nutritionData.ingredients} />
        </div>

        {/* Action Buttons */}
        <div className="mt-12 flex flex-col items-center gap-4 sm:flex-row sm:justify-center">
          <Button onClick={onBack} variant="outline" size="lg">
            Scan Another Label
          </Button>
          <Button size="lg" className="gap-2" onClick={onSave} disabled={isSaving}>
            {isSaving ? "Saving..." : "Save to History"}
          </Button>
        </div>
      </div>
    </section>
  )
}
