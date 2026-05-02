// Sample nutrition data for demonstration
export const sampleNutritionData = {
  productName: "Organic Greek Yogurt",
  brand: "Nature's Best",
  servingSize: "170g (1 container)",
  servingsPerContainer: 1,
  
  macronutrients: {
    calories: {
      amount: 150,
      unit: "kcal",
      dailyValue: 8,
    },
    totalFat: {
      amount: 4,
      unit: "g",
      dailyValue: 5,
    },
    saturatedFat: {
      amount: 2.5,
      unit: "g",
      dailyValue: 13,
    },
    transFat: {
      amount: 0,
      unit: "g",
      dailyValue: null,
    },
    cholesterol: {
      amount: 15,
      unit: "mg",
      dailyValue: 5,
    },
    sodium: {
      amount: 65,
      unit: "mg",
      dailyValue: 3,
    },
    totalCarbohydrate: {
      amount: 7,
      unit: "g",
      dailyValue: 3,
    },
    dietaryFiber: {
      amount: 0,
      unit: "g",
      dailyValue: 0,
    },
    totalSugars: {
      amount: 6,
      unit: "g",
      dailyValue: null,
    },
    addedSugars: {
      amount: 0,
      unit: "g",
      dailyValue: 0,
    },
    protein: {
      amount: 17,
      unit: "g",
      dailyValue: 34,
    },
  },

  micronutrients: {
    vitaminD: {
      amount: 0,
      unit: "mcg",
      dailyValue: 0,
    },
    calcium: {
      amount: 200,
      unit: "mg",
      dailyValue: 15,
    },
    iron: {
      amount: 0,
      unit: "mg",
      dailyValue: 0,
    },
    potassium: {
      amount: 240,
      unit: "mg",
      dailyValue: 5,
    },
    vitaminA: {
      amount: 80,
      unit: "mcg",
      dailyValue: 9,
    },
    vitaminC: {
      amount: 0,
      unit: "mg",
      dailyValue: 0,
    },
    vitaminB12: {
      amount: 1.2,
      unit: "mcg",
      dailyValue: 50,
    },
    phosphorus: {
      amount: 230,
      unit: "mg",
      dailyValue: 18,
    },
  },

  ingredients: [
    {
      name: "Cultured Pasteurized Organic Nonfat Milk",
      description: "Milk that has been heat-treated to kill harmful bacteria, then fermented with beneficial probiotic cultures.",
      isHealthy: true,
    },
    {
      name: "Organic Cream",
      description: "The fatty part of milk, adds richness and improves texture while providing fat-soluble vitamins.",
      isHealthy: true,
    },
    {
      name: "Live Active Cultures",
      description: "Beneficial bacteria including S. thermophilus and L. bulgaricus that support gut health and digestion.",
      isHealthy: true,
    },
  ],

  insights: {
    healthScore: 85,
    summary: "This is a nutrient-dense food with excellent protein content and beneficial probiotics. Low in added sugars and a good source of calcium.",
    highlights: [
      "High in protein (17g per serving)",
      "Excellent source of calcium",
      "Contains live active cultures for gut health",
      "No added sugars",
    ],
    concerns: [
      "Contains saturated fat (13% DV)",
      "Not suitable for lactose intolerant individuals",
    ],
  },
}

// Default user goals
export const defaultGoals = {
  calories: 2000,
  protein: 50,
  carbs: 275,
  fat: 78,
  fiber: 28,
  sodium: 2300,
  sugar: 50,
}

// Nutrition rating thresholds
export const nutritionRatings = {
  excellent: { min: 20, color: "success" },
  good: { min: 10, max: 19, color: "primary" },
  moderate: { min: 5, max: 9, color: "warning" },
  low: { max: 4, color: "muted" },
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

// Calculate macro distribution
export function calculateMacroDistribution(macros) {
  const proteinCals = macros.protein.amount * 4
  const carbsCals = macros.totalCarbohydrate.amount * 4
  const fatCals = macros.totalFat.amount * 9
  const total = proteinCals + carbsCals + fatCals

  return {
    protein: Math.round((proteinCals / total) * 100),
    carbs: Math.round((carbsCals / total) * 100),
    fat: Math.round((fatCals / total) * 100),
  }
}
