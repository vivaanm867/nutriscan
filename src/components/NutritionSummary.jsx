import { TrendingUp, TrendingDown, AlertCircle, CheckCircle } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { Badge } from "@/components/ui/Badge"

export function NutritionSummary({ insights, productName }) {
  const getScoreColor = (score) => {
    if (score >= 80) return "text-success"
    if (score >= 60) return "text-primary"
    if (score >= 40) return "text-warning"
    return "text-destructive"
  }

  const getScoreLabel = (score) => {
    if (score >= 80) return "Excellent"
    if (score >= 60) return "Good"
    if (score >= 40) return "Fair"
    return "Poor"
  }

  return (
    <Card className="overflow-hidden">
      <CardHeader className="bg-primary/5">
        <div className="flex items-start justify-between">
          <div>
            <CardTitle className="text-xl">{productName}</CardTitle>
            <p className="mt-1 text-sm text-muted-foreground">
              Nutrition Analysis Summary
            </p>
          </div>
          <div className="text-right">
            <div className={`text-4xl font-bold ${getScoreColor(insights.healthScore)}`}>
              {insights.healthScore}
            </div>
            <Badge variant={insights.healthScore >= 60 ? "success" : "warning"}>
              {getScoreLabel(insights.healthScore)}
            </Badge>
          </div>
        </div>
      </CardHeader>
      <CardContent className="pt-6">
        {/* Summary */}
        <p className="text-muted-foreground">{insights.summary}</p>
        
        {/* Highlights & Concerns */}
        <div className="mt-6 grid gap-6 sm:grid-cols-2">
          {/* Highlights */}
          <div>
            <h4 className="mb-3 flex items-center gap-2 font-semibold text-foreground">
              <TrendingUp className="h-4 w-4 text-success" />
              Highlights
            </h4>
            <ul className="space-y-2">
              {insights.highlights.map((highlight, index) => (
                <li 
                  key={index}
                  className="flex items-start gap-2 text-sm text-muted-foreground"
                >
                  <CheckCircle className="mt-0.5 h-4 w-4 flex-shrink-0 text-success" />
                  {highlight}
                </li>
              ))}
            </ul>
          </div>
          
          {/* Concerns */}
          <div>
            <h4 className="mb-3 flex items-center gap-2 font-semibold text-foreground">
              <TrendingDown className="h-4 w-4 text-warning" />
              Things to Consider
            </h4>
            <ul className="space-y-2">
              {insights.concerns.map((concern, index) => (
                <li 
                  key={index}
                  className="flex items-start gap-2 text-sm text-muted-foreground"
                >
                  <AlertCircle className="mt-0.5 h-4 w-4 flex-shrink-0 text-warning" />
                  {concern}
                </li>
              ))}
            </ul>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
