import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { Badge } from "@/components/ui/Badge"
import { getDailyValueColor } from "@/data/nutritionData"

export function MicronutrientSection({ micronutrients }) {
  const microData = [
    { key: "vitaminD", label: "Vitamin D" },
    { key: "calcium", label: "Calcium" },
    { key: "iron", label: "Iron" },
    { key: "potassium", label: "Potassium" },
    { key: "vitaminA", label: "Vitamin A" },
    { key: "vitaminC", label: "Vitamin C" },
    { key: "vitaminB12", label: "Vitamin B12" },
    { key: "phosphorus", label: "Phosphorus" },
  ].filter(m => micronutrients[m.key])

  return (
    <Card>
      <CardHeader>
        <CardTitle>Vitamins & Minerals</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid gap-3 sm:grid-cols-2">
          {microData.map(({ key, label }) => {
            const nutrient = micronutrients[key]
            const dv = nutrient.dailyValue
            const colorClass = getDailyValueColor(dv, false)
            
            let badgeVariant = "secondary"
            if (dv >= 20) badgeVariant = "success"
            else if (dv >= 10) badgeVariant = "default"
            else if (dv > 0) badgeVariant = "warning"
            
            return (
              <div 
                key={key}
                className="flex items-center justify-between rounded-lg border border-border bg-card p-3"
              >
                <div>
                  <p className="font-medium text-foreground">{label}</p>
                  <p className="text-sm text-muted-foreground">
                    {nutrient.amount}{nutrient.unit}
                  </p>
                </div>
                <Badge variant={badgeVariant}>
                  {dv}% DV
                </Badge>
              </div>
            )
          })}
        </div>
        
        {/* No significant micronutrients message */}
        {microData.filter(m => micronutrients[m.key]?.dailyValue > 0).length === 0 && (
          <p className="text-center text-muted-foreground">
            No significant vitamins or minerals detected
          </p>
        )}
      </CardContent>
    </Card>
  )
}
