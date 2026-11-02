// Shared nutrition helpers used by the dashboard components.

export const defaultGoals = {
  calories: 2000,
  protein: 50,
  carbs: 275,
  fat: 78,
  fiber: 28,
  sodium: 2300,
  sugar: 50,
}

// Get color class based on daily value percentage
export function getDailyValueColor(percentage, isInverse = false) {
  if (isInverse) {
    // For nutrients where lower is better (sodium, saturated fat, etc.)
    if (percentage <= 5) return "text-success"
    if (percentage <= 15) return "text-primary"
    if (percentage <= 25) return "text-warning"
    return "text-destructive"
  }
  // For nutrients where higher is better (protein, fiber, vitamins, etc.)
  if (percentage >= 20) return "text-success"
  if (percentage >= 10) return "text-primary"
  if (percentage >= 5) return "text-warning"
  return "text-muted-foreground"
}

// Calculate the share of calories from protein / carbs / fat (null-safe)
// Returns {} if any macro is missing, so the cards don't show misleading percentages.
export function calculateMacroDistribution(macros) {
  const protein = macros.protein?.amount
  const carbs = macros.totalCarbohydrate?.amount
  const fat = macros.totalFat?.amount
  if (protein == null || carbs == null || fat == null) return {}

  const proteinCals = protein * 4
  const carbsCals = carbs * 4
  const fatCals = fat * 9
  const total = proteinCals + carbsCals + fatCals

  if (!total) return {}

  return {
    protein: Math.round((proteinCals / total) * 100),
    carbs: Math.round((carbsCals / total) * 100),
    fat: Math.round((fatCals / total) * 100),
  }
}
