import { Leaf, Github } from "lucide-react"

export function Footer() {
  return (
    <footer className="border-t border-border bg-background">
      <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
        <div className="flex flex-col items-center justify-between gap-6 sm:flex-row">
          {/* Logo */}
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary">
              <Leaf className="h-4 w-4 text-primary-foreground" />
            </div>
            <span className="font-bold text-foreground">NutriScan</span>
          </div>

          {/* Links */}
          <p className="text-sm text-muted-foreground">
            Built by{" "}
            <a
              href="https://github.com/vivaanm867"
              target="_blank"
              rel="noreferrer"
              className="font-medium text-foreground hover:underline"
            >
              Vivaan Motwani
            </a>
          </p>

          <a
            href="https://github.com/vivaanm867/nutriscan"
            target="_blank"
            rel="noreferrer"
            className="flex items-center gap-2 text-sm text-muted-foreground transition-colors hover:text-foreground"
            aria-label="View source on GitHub"
          >
            <Github className="h-5 w-5" />
            Source code
          </a>
        </div>

        {/* Copyright */}
        <div className="mt-8 border-t border-border pt-8 text-center">
          <p className="text-sm text-muted-foreground">
            &copy; {new Date().getFullYear()} NutriScan
          </p>
          <p className="mt-2 text-xs text-muted-foreground">
            Nutrition information is for educational purposes only. Always consult healthcare professionals for dietary advice.
          </p>
        </div>
      </div>
    </footer>
  )
}
