import { useEffect } from "react"
import { useLocation, useNavigate } from "react-router-dom"
import { ShieldCheck, ScanLine, Sparkles, Layers } from "lucide-react"
import { Button } from "@/components/ui/Button"
import { HeroSection } from "@/components/HeroSection"

export function LandingPage() {
  const location = useLocation()
  const navigate = useNavigate()

  useEffect(() => {
    if (location.hash) {
      const target = document.querySelector(location.hash)
      if (target) {
        target.scrollIntoView({ behavior: "smooth" })
      }
    }
  }, [location.hash])

  return (
    <div>
      <HeroSection
        primaryLabel="Get Started"
        secondaryLabel="Log In"
        onPrimary={() => navigate("/signup")}
        onSecondary={() => navigate("/login")}
      />

      <section id="features" className="bg-muted/40 py-16 sm:py-24">
        <div className="mx-auto grid max-w-6xl gap-6 px-4 sm:px-6 lg:grid-cols-3 lg:px-8">
          <FeatureCard
            icon={<ScanLine className="h-5 w-5" />}
            title="Smart Label Capture"
            description="Upload a photo and get a clean, structured breakdown of nutrition data."
          />
          <FeatureCard
            icon={<Sparkles className="h-5 w-5" />}
            title="Actionable Insights"
            description="See what matters most with highlights, warnings, and goal alignment."
          />
          <FeatureCard
            icon={<ShieldCheck className="h-5 w-5" />}
            title="Private by Default"
            description="Your scans are secured behind your account with access controls."
          />
        </div>
      </section>

      <section id="benefits" className="bg-background py-16 sm:py-24">
        <div className="mx-auto grid max-w-6xl gap-10 px-4 sm:px-6 lg:grid-cols-2 lg:items-center lg:px-8">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.2em] text-primary">
              Why NutriScan
            </p>
            <h2 className="mt-3 text-3xl font-bold text-foreground sm:text-4xl">
              Stop guessing. Start scanning.
            </h2>
            <p className="mt-4 text-lg text-muted-foreground">
              NutriScan turns complex labels into insights you can actually use. Create an
              account to unlock a personal dashboard, track your scans, and keep your nutrition
              story in one place.
            </p>
            <div className="mt-8 flex flex-wrap gap-4">
              <Button size="lg" onClick={() => navigate("/signup")}>Get Started</Button>
              <Button variant="outline" size="lg" onClick={() => navigate("/login")}>Log In</Button>
            </div>
          </div>
          <div className="grid gap-4 sm:grid-cols-2">
            <BenefitCard
              title="Saved Scan Library"
              description="Keep a searchable history of every label you've analyzed."
            />
            <BenefitCard
              title="Goal Tracking"
              description="Match nutrition data to your health goals automatically."
            />
            <BenefitCard
              title="Faster Decisions"
              description="Spot ingredients and red flags before you buy."
            />
            <BenefitCard
              title="Built for Mobile"
              description="Scan on the go without sacrificing clarity."
            />
          </div>
        </div>
      </section>

      <section id="cta" className="bg-primary py-16 text-primary-foreground sm:py-20">
        <div className="mx-auto flex max-w-5xl flex-col items-center gap-6 px-4 text-center sm:px-6">
          <Layers className="h-10 w-10" />
          <h2 className="text-3xl font-semibold sm:text-4xl">
            Ready to see what’s in your food?
          </h2>
          <p className="text-lg text-primary-foreground/80">
            Create your account and unlock your personal scanning dashboard.
          </p>
          <Button size="lg" variant="secondary" onClick={() => navigate("/signup")}
          >
            Create Free Account
          </Button>
        </div>
      </section>
    </div>
  )
}

function FeatureCard({ icon, title, description }) {
  return (
    <div className="rounded-2xl border border-border bg-card p-6 shadow-sm">
      <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10 text-primary">
        {icon}
      </div>
      <h3 className="mt-4 text-lg font-semibold text-card-foreground">{title}</h3>
      <p className="mt-2 text-sm text-muted-foreground">{description}</p>
    </div>
  )
}

function BenefitCard({ title, description }) {
  return (
    <div className="rounded-2xl border border-border bg-muted/40 p-5">
      <h3 className="text-base font-semibold text-foreground">{title}</h3>
      <p className="mt-2 text-sm text-muted-foreground">{description}</p>
    </div>
  )
}
