import { useState, useRef } from "react"
import { Upload, Camera, X, Image as ImageIcon } from "lucide-react"
import { Button } from "@/components/ui/Button"
import { Input } from "@/components/ui/Input"
import { Label } from "@/components/ui/Label"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/Card"
import { cn } from "@/lib/utils"

export function ImageUploadSection({ onAnalyze, isAnalyzing }) {
  const [image, setImage] = useState(null)
  const [imagePreview, setImagePreview] = useState(null)
  const [foodName, setFoodName] = useState("")
  const [dragActive, setDragActive] = useState(false)
  const fileInputRef = useRef(null)

  const handleDrag = (e) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true)
    } else if (e.type === "dragleave") {
      setDragActive(false)
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    
    const files = e.dataTransfer?.files
    if (files && files[0]) {
      handleFile(files[0])
    }
  }

  const handleFileInput = (e) => {
    const files = e.target.files
    if (files && files[0]) {
      handleFile(files[0])
    }
  }

  const handleFile = (file) => {
    if (file.type.startsWith("image/")) {
      setImage(file)
      const reader = new FileReader()
      reader.onload = (e) => {
        setImagePreview(e.target?.result)
      }
      reader.readAsDataURL(file)
    }
  }

  const clearImage = () => {
    setImage(null)
    setImagePreview(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ""
    }
  }

  const handleAnalyze = () => {
    if (image || foodName) {
      onAnalyze({ image, foodName })
    }
  }

  return (
    <section id="scan" className="bg-muted/30 py-16 sm:py-24">
      <div className="mx-auto max-w-3xl px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <h2 className="text-3xl font-bold tracking-tight text-foreground sm:text-4xl">
            Upload Your Nutrition Label
          </h2>
          <p className="mt-4 text-lg text-muted-foreground">
            Take a photo or upload an image of the nutrition facts panel
          </p>
        </div>

        <Card className="mt-10">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Camera className="h-5 w-5 text-primary" />
              Step 1: Upload Image
            </CardTitle>
            <CardDescription>
              Drag and drop an image or click to browse
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Upload Area */}
            {!imagePreview ? (
              <div
                className={cn(
                  "relative flex flex-col items-center justify-center rounded-xl border-2 border-dashed p-12 transition-all",
                  dragActive
                    ? "border-primary bg-primary/5"
                    : "border-border hover:border-primary/50 hover:bg-muted/50"
                )}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  className="absolute inset-0 cursor-pointer opacity-0"
                  onChange={handleFileInput}
                  aria-label="Upload nutrition label image"
                />
                <div className="flex h-16 w-16 items-center justify-center rounded-full bg-primary/10">
                  <Upload className="h-8 w-8 text-primary" />
                </div>
                <p className="mt-4 text-sm font-medium text-foreground">
                  Drop your image here or click to browse
                </p>
                <p className="mt-1 text-xs text-muted-foreground">
                  PNG, JPG, or HEIC up to 10MB
                </p>
              </div>
            ) : (
              <div className="relative overflow-hidden rounded-xl border border-border">
                <img
                  src={imagePreview}
                  alt="Uploaded nutrition label preview"
                  className="h-64 w-full object-contain bg-muted/20"
                />
                <Button
                  variant="destructive"
                  size="icon"
                  className="absolute right-2 top-2"
                  onClick={clearImage}
                  aria-label="Remove image"
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
            )}
          </CardContent>
        </Card>

        <Card className="mt-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <ImageIcon className="h-5 w-5 text-primary" />
              Step 2: Add Context (Optional)
            </CardTitle>
            <CardDescription>
              Help us provide better insights by adding food details
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="foodName">Food Name or Product</Label>
              <Input
                id="foodName"
                placeholder="e.g., Greek Yogurt, Protein Bar, Cereal..."
                value={foodName}
                onChange={(e) => setFoodName(e.target.value)}
              />
            </div>
          </CardContent>
        </Card>

        {/* Analyze Button */}
        <div className="mt-8 text-center">
          <Button
            size="lg"
            onClick={handleAnalyze}
            disabled={(!image && !foodName) || isAnalyzing}
            className="min-w-[200px]"
          >
            {isAnalyzing ? (
              <>
                <span className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-primary-foreground border-t-transparent" />
                Analyzing...
              </>
            ) : (
              "Analyze Nutrition"
            )}
          </Button>
          <p className="mt-3 text-sm text-muted-foreground">
            Your image is processed securely and never stored
          </p>
        </div>
      </div>
    </section>
  )
}
