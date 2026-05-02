import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { Progress } from "@/components/ui/Progress"
import { getDailyValueColor } from "@/data/nutritionData"

export function DailyValueSection({ macros }) {
  const nutrients = [
    { key: "totalFat", label: "Total Fat", isInverse: true },
    { key: "saturatedFat", label: "Saturated Fat", isInverse: true },
    { key: "cholesterol", label: "Cholesterol", isInverse: true },
    { key: "sodium", label: "Sodium", isInverse: true },
    { key: "totalCarbohydrate", label: "Total Carbohydrate", isInverse: false },
    { key: "dietaryFiber", label: "Dietary Fiber", isInverse: false },
    { key: "protein", label: "Protein", isInverse: false },
  ].filter(n => macros[n.key]?.dailyValue !== null)

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>% Daily Value</span>
          <span className="text-sm font-normal text-muted-foreground">
            Based on 2,000 calorie diet
          </span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {nutrients.map(({ key, label, isInverse }) => {
            const nutrient = macros[key]
            if (!nutrient) return null
            
            const dv = nutrient.dailyValue || 0
            const colorClass = getDailyValueColor(dv, isInverse)
            
            return (
              <div key={key} className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="font-medium text-foreground">{label}</span>
                  <span className={colorClass}>
                    {nutrient.amount}{nutrient.unit} ({dv}%)
                  </span>
                </div>
                <Progress 
                  value={Math.min(dv, 100)} 
                  className="h-2"
                />
              </div>
            )
          })}
        </div>
        
        {/* Legend */}
        <div className="mt-6 flex flex-wrap gap-4 border-t border-border pt-4 text-xs">
          <div className="flex items-center gap-1.5">
            <div className="h-2 w-2 rounded-full bg-success" />
            <span className="text-muted-foreground">Excellent</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="h-2 w-2 rounded-full bg-primary" />
            <span className="text-muted-foreground">Good</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="h-2 w-2 rounded-full bg-warning" />
            <span className="text-muted-foreground">Moderate</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="h-2 w-2 rounded-full bg-destructive" />
            <span className="text-muted-foreground">High</span>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
