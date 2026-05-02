import { Check, Info } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { Badge } from "@/components/ui/Badge"

export function IngredientCards({ ingredients }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          Ingredient Breakdown
          <Badge variant="secondary">{ingredients.length} items</Badge>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {ingredients.map((ingredient, index) => (
            <div 
              key={index}
              className="rounded-xl border border-border bg-muted/30 p-4"
            >
              <div className="flex items-start gap-3">
                <div className={`mt-0.5 flex h-6 w-6 flex-shrink-0 items-center justify-center rounded-full ${
                  ingredient.isHealthy 
                    ? "bg-success/10 text-success" 
                    : "bg-warning/10 text-warning"
                }`}>
                  {ingredient.isHealthy ? (
                    <Check className="h-4 w-4" />
                  ) : (
                    <Info className="h-4 w-4" />
                  )}
                </div>
                <div className="flex-1">
                  <h4 className="font-semibold text-foreground">
                    {ingredient.name}
                  </h4>
                  <p className="mt-1 text-sm text-muted-foreground">
                    {ingredient.description}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
