import { Sparkles, Shield, ArrowRight } from "lucide-react"
import { Button } from "@/components/ui/Button"

export function HeroSection({
  primaryLabel = "Get Started",
  secondaryLabel = "Log In",
  onPrimary,
  onSecondary,
}) {
  return (
    <section id="home" className="relative overflow-hidden bg-background py-16 sm:py-24">
      {/* Background gradient */}
      <div className="absolute inset-0 -z-10">
        <div className="absolute left-1/2 top-0 h-[500px] w-[500px] -translate-x-1/2 rounded-full bg-primary/5 blur-3xl" />
      </div>

      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full border border-emerald-500/20 bg-emerald-500/10 text-emerald-400 text-sm">
  <Sparkles className="h-4 w-4" />
  Built for smarter nutrition decisions
</div>

          {/* Headline */}
          <h1 className="mx-auto max-w-4xl text-balance text-4xl font-bold tracking-tight text-foreground sm:text-5xl lg:text-6xl">
            Scan, understand, and track your{" "}
            <span className="text-primary">nutrition</span>
          </h1>

          {/* Subheadline */}
          <p className="mx-auto mt-6 max-w-2xl text-pretty text-lg text-muted-foreground sm:text-xl">
            NutriScan turns labels into insights and keeps your scans organized in a personal
            dashboard so you can make faster, healthier choices.
          </p>

          <section className="grid items-center gap-12 lg:grid-cols-2">
  <div>
    {/* badge, heading, paragraph, buttons */}
  </div>

  <div>
    {/* sample scan result card */}
  </div>
</section>

          {/* CTA Buttons */}
          <div className="mt-10 flex flex-col items-center justify-center gap-4 sm:flex-row">
            <Button size="lg" onClick={onPrimary} className="gap-2">
              {primaryLabel}
              <ArrowRight className="h-4 w-4" />
            </Button>
            <Button variant="outline" size="lg" onClick={onSecondary}>
              {secondaryLabel}
            </Button>
          </div>

          {/* Trust indicators */}
          <div className="mt-12 flex flex-wrap items-center justify-center gap-8 text-muted-foreground">
            <div className="flex items-center gap-2">
              <Shield className="h-5 w-5 text-primary" />
              <span className="text-sm">Account Protected</span>
            </div>
            <div className="flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-primary" />
              <span className="text-sm">Smart Insights</span>
            </div>
            <div className="flex items-center gap-2">
              <ArrowRight className="h-5 w-5 text-primary" />
              <span className="text-sm">Organized History</span>
            </div>
          </div>
        </div>

        {/* Feature cards preview */}
        <div className="mt-16 grid gap-6 sm:grid-cols-3">
          <FeatureCard
            icon={<Shield className="h-6 w-6" />}
            title="📸 Label Scanning"
            description="Upload or snap a photo of any nutrition label and instantly extract clean, structured data without manual entry."
          />
          <FeatureCard
            icon={<Sparkles className="h-6 w-6" />}
            title="🧠 Nutrition Breakdown"
            description="Understand exactly what you're consuming with a detailed breakdown of calories, macros, and key nutrients in seconds."
          />
          <FeatureCard
            icon={<ArrowRight className="h-6 w-6" />}
            title="⚠️ Health Highlights"
            description="Quickly spot high sugar, sodium, or other concerns with smart highlights that help you make better food choices." 
          />
        </div>
      </div>
    </section>
  )
}

function FeatureCard({ icon, title, description }) {
  return (
    <div className="group rounded-2xl border border-border bg-card p-6 transition-all hover:border-primary/50 hover:shadow-lg">
      <div className="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10 text-primary transition-colors group-hover:bg-primary group-hover:text-primary-foreground">
        {icon}
      </div>
      <h3 className="mb-2 text-lg font-semibold text-card-foreground">{title}</h3>
      <p className="text-sm text-muted-foreground">{description}</p>
    </div>
  )
}
