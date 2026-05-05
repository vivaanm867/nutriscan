import { useState } from "react"
import { Link, useNavigate } from "react-router-dom"
import { Menu, X, Sun, Moon, Leaf } from "lucide-react"
import { Button } from "@/components/ui/Button"
import { cn } from "@/lib/utils"
import { useAuth } from "@/context/AuthContext"

export function Navbar({ darkMode, setDarkMode }) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const navigate = useNavigate()
  const { token, logout } = useAuth()

  const navLinks = [
    { label: "Home", href: "/" },
    { label: "Features", href: "/#features" },
    { label: "Benefits", href: "/#benefits" },
    { label: "Get Started", href: "/#cta" },
  ]

  return (
    <header className="sticky top-0 z-50 w-full border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <nav className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        {/* Logo */}
        <Link to="/" className="flex items-center gap-2">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary">
            <Leaf className="h-5 w-5 text-primary-foreground" />
          </div>
          <span className="text-xl font-bold text-foreground">NutriScan</span>
        </Link>

        {/* Desktop Navigation */}
        <div className="hidden md:flex md:items-center md:gap-8">
          {navLinks.map((link) => (
            <Link
              key={link.label}
              to={link.href}
              className="text-sm font-medium text-muted-foreground transition-colors hover:text-foreground"
            >
              {link.label}
            </Link>
          ))}
        </div>

        {/* Actions */}
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setDarkMode(!darkMode)}
            aria-label={darkMode ? "Switch to light mode" : "Switch to dark mode"}
          >
            {darkMode ? (
              <Sun className="h-5 w-5" />
            ) : (
              <Moon className="h-5 w-5" />
            )}
          </Button>
          
          {token ? (
            <>
              <Button
                variant="outline"
                className="hidden md:inline-flex"
                onClick={() => navigate("/dashboard")}
              >
                Dashboard
              </Button>
              <Button
                className="hidden md:inline-flex"
                onClick={logout}
              >
                Log Out
              </Button>
            </>
          ) : (
            <>
              <Button
                variant="outline"
                className="hidden md:inline-flex"
                onClick={() => navigate("/login")}
              >
                Log In
              </Button>
              <Button
                className="hidden md:inline-flex"
                onClick={() => navigate("/signup")}
              >
                Sign Up
              </Button>
            </>
          )}

          {/* Mobile menu button */}
          <Button
            variant="ghost"
            size="icon"
            className="md:hidden"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            aria-label={mobileMenuOpen ? "Close menu" : "Open menu"}
          >
            {mobileMenuOpen ? (
              <X className="h-5 w-5" />
            ) : (
              <Menu className="h-5 w-5" />
            )}
          </Button>
        </div>
      </nav>

      {/* Mobile Navigation */}
      <div
        className={cn(
          "md:hidden",
          mobileMenuOpen ? "block" : "hidden"
        )}
      >
        <div className="space-y-1 border-t border-border bg-background px-4 pb-4 pt-2">
          {navLinks.map((link) => (
            <Link
              key={link.label}
              to={link.href}
              className="block rounded-lg px-3 py-2 text-base font-medium text-muted-foreground transition-colors hover:bg-accent hover:text-foreground"
              onClick={() => setMobileMenuOpen(false)}
            >
              {link.label}
            </Link>
          ))}
          <div className="mt-4 grid gap-2">
            {token ? (
              <>
                <Button onClick={() => navigate("/dashboard")}>Dashboard</Button>
                <Button variant="outline" onClick={logout}>Log Out</Button>
              </>
            ) : (
              <>
                <Button onClick={() => navigate("/signup")}>Sign Up</Button>
                <Button variant="outline" onClick={() => navigate("/login")}>Log In</Button>
              </>
            )}
          </div>
        </div>
      </div>
    </header>
  )
}
