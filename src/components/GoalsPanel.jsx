import { useState } from "react"
import { Target, Save, RotateCcw } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/Card"
import { Button } from "@/components/ui/Button"
import { Input } from "@/components/ui/Input"
import { Label } from "@/components/ui/Label"
import { defaultGoals } from "@/data/nutritionData"

export function GoalsPanel({ goals, setGoals }) {
  const [editedGoals, setEditedGoals] = useState(goals)
  const [hasChanges, setHasChanges] = useState(false)

  const handleChange = (key, value) => {
    const numValue = parseInt(value) || 0
    setEditedGoals(prev => ({
      ...prev,
      [key]: numValue
    }))
    setHasChanges(true)
  }

  const handleSave = () => {
    setGoals(editedGoals)
    setHasChanges(false)
  }

  const handleReset = () => {
    setEditedGoals(defaultGoals)
    setGoals(defaultGoals)
    setHasChanges(false)
  }

  const goalFields = [
    { key: "calories", label: "Daily Calories", unit: "kcal", max: 5000 },
    { key: "protein", label: "Protein", unit: "g", max: 300 },
    { key: "carbs", label: "Carbohydrates", unit: "g", max: 500 },
    { key: "fat", label: "Fat", unit: "g", max: 200 },
    { key: "fiber", label: "Fiber", unit: "g", max: 100 },
    { key: "sodium", label: "Sodium", unit: "mg", max: 5000 },
    { key: "sugar", label: "Added Sugars", unit: "g", max: 150 },
  ]

  return (
    <section id="goals" className="bg-muted/30 py-16 sm:py-24">
      <div className="mx-auto max-w-3xl px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <h2 className="text-3xl font-bold tracking-tight text-foreground sm:text-4xl">
            Set Your Goals
          </h2>
          <p className="mt-4 text-lg text-muted-foreground">
            Customize your daily nutrition targets for personalized insights
          </p>
        </div>

        <Card className="mt-10">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Target className="h-5 w-5 text-primary" />
              Daily Nutrition Targets
            </CardTitle>
            <CardDescription>
              Adjust these values based on your dietary needs and health goals
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-6 sm:grid-cols-2">
              {goalFields.map(({ key, label, unit, max }) => (
                <div key={key} className="space-y-2">
                  <Label htmlFor={key} className="flex items-center justify-between">
                    <span>{label}</span>
                    <span className="text-xs text-muted-foreground">{unit}</span>
                  </Label>
                  <Input
                    id={key}
                    type="number"
                    min="0"
                    max={max}
                    value={editedGoals[key]}
                    onChange={(e) => handleChange(key, e.target.value)}
                    className="text-right"
                  />
                </div>
              ))}
            </div>

            {/* Action Buttons */}
            <div className="mt-8 flex flex-col gap-3 sm:flex-row sm:justify-end">
              <Button
                variant="outline"
                onClick={handleReset}
                className="gap-2"
              >
                <RotateCcw className="h-4 w-4" />
                Reset to Defaults
              </Button>
              <Button
                onClick={handleSave}
                disabled={!hasChanges}
                className="gap-2"
              >
                <Save className="h-4 w-4" />
                Save Changes
              </Button>
            </div>

            {/* Info text */}
            <p className="mt-6 text-center text-sm text-muted-foreground">
              Default values are based on a 2,000 calorie diet. Consult a healthcare 
              professional for personalized nutrition advice.
            </p>
          </CardContent>
        </Card>

        {/* Quick Presets */}
        <div className="mt-8">
          <h3 className="mb-4 text-center text-sm font-medium text-muted-foreground">
            Quick Presets
          </h3>
          <div className="flex flex-wrap justify-center gap-3">
            <PresetButton
              label="Weight Loss"
              onClick={() => {
                const preset = { ...defaultGoals, calories: 1500, carbs: 150, fat: 50 }
                setEditedGoals(preset)
                setGoals(preset)
              }}
            />
            <PresetButton
              label="Maintenance"
              onClick={() => {
                setEditedGoals(defaultGoals)
                setGoals(defaultGoals)
              }}
            />
            <PresetButton
              label="Muscle Gain"
              onClick={() => {
                const preset = { ...defaultGoals, calories: 2500, protein: 150, carbs: 300 }
                setEditedGoals(preset)
                setGoals(preset)
              }}
            />
            <PresetButton
              label="Low Carb"
              onClick={() => {
                const preset = { ...defaultGoals, carbs: 50, fat: 150, protein: 100 }
                setEditedGoals(preset)
                setGoals(preset)
              }}
            />
          </div>
        </div>
      </div>
    </section>
  )
}

function PresetButton({ label, onClick }) {
  return (
    <button
      onClick={onClick}
      className="rounded-full border border-border bg-background px-4 py-2 text-sm font-medium text-foreground transition-colors hover:bg-accent hover:text-accent-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
    >
      {label}
    </button>
  )
}
