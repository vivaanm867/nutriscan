import { Flame, Drumstick, Wheat, Droplets } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { calculateMacroDistribution } from "@/data/nutritionData"

export function MacronutrientCards({ macros }) {
  const distribution = calculateMacroDistribution(macros)

  const macroData = [
    {
      label: "Calories",
      value: macros.calories.amount,
      unit: "kcal",
      icon: Flame,
      color: "text-accent",
      bgColor: "bg-accent/10",
      dailyValue: macros.calories.dailyValue,
    },
    {
      label: "Protein",
      value: macros.protein.amount,
      unit: "g",
      icon: Drumstick,
      color: "text-chart-1",
      bgColor: "bg-chart-1/10",
      dailyValue: macros.protein.dailyValue,
      percentage: distribution.protein,
    },
    {
      label: "Carbs",
      value: macros.totalCarbohydrate.amount,
      unit: "g",
      icon: Wheat,
      color: "text-chart-2",
      bgColor: "bg-chart-2/10",
      dailyValue: macros.totalCarbohydrate.dailyValue,
      percentage: distribution.carbs,
    },
    {
      label: "Fat",
      value: macros.totalFat.amount,
      unit: "g",
      icon: Droplets,
      color: "text-chart-3",
      bgColor: "bg-chart-3/10",
      dailyValue: macros.totalFat.dailyValue,
      percentage: distribution.fat,
    },
  ]

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      {macroData.map((macro) => (
        <MacroCard key={macro.label} {...macro} />
      ))}
    </div>
  )
}

function MacroCard({ label, value, unit, icon: Icon, color, bgColor, dailyValue, percentage }) {
  return (
    <Card className="relative overflow-hidden">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="text-sm font-medium text-muted-foreground">
            {label}
          </CardTitle>
          <div className={`rounded-lg p-2 ${bgColor}`}>
            <Icon className={`h-4 w-4 ${color}`} />
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="flex items-baseline gap-1">
          <span className="text-3xl font-bold text-foreground">{value}</span>
          <span className="text-lg text-muted-foreground">{unit}</span>
        </div>
        <div className="mt-2 flex items-center gap-3 text-sm">
          {dailyValue !== null && (
            <span className="text-muted-foreground">
              {dailyValue}% Daily Value
            </span>
          )}
          {percentage !== undefined && (
            <span className={`font-medium ${color}`}>
              {percentage}% of total
            </span>
          )}
        </div>
      </CardContent>
      {/* Decorative accent bar */}
      <div className={`absolute bottom-0 left-0 h-1 w-full ${bgColor}`} />
    </Card>
  )
}
