'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent } from "@/components/ui/card"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
import { useToast } from "@/hooks/use-toast"
import { Loader2, ImageIcon } from 'lucide-react'
import Image from "next/image"
import { PostsCarousel } from "@/components/posts-carousel"
import { BACKEND_API_BASE_URL } from "@/app/constants"

interface TransformResponse {
  cloudinary_url: string
  qr_code_url: string
}

interface Post {
    id: number
    cloudinary_url: string
    description: string
    created_at: string
    updated_at: string
    user_id: number
}  

export default function TransformPage() {
  const [posts, setPosts] = useState<Post[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedPost, setSelectedPost] = useState<Post | null>(null)
  const [effect, setEffect] = useState<string>("")
  const [transforming, setTransforming] = useState(false)
  const [result, setResult] = useState<TransformResponse | null>(null)
  const { toast } = useToast()

  useEffect(() => {
    fetchPosts()
  }, [])

  const fetchPosts = async () => {
    try {
      const response = await fetch(`${BACKEND_API_BASE_URL}/api/posts/all_posts`)
      if (!response.ok) {
        throw new Error('Failed to fetch posts')
      }
      const data = await response.json()
      setPosts(data)
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load posts. Please refresh the page.",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  const handleTransform = async () => {
    if (!selectedPost || !effect) {
      toast({
        title: "Error",
        description: "Please select both a post and an effect",
        variant: "destructive",
      })
      return
    }

    setTransforming(true)
    try {
      const formData = new FormData()
      formData.append('effect', effect)

      const response = await fetch(`${BACKEND_API_BASE_URL}/api/transform/${selectedPost.id}`, {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        throw new Error('Transform failed')
      }

      const data = await response.json()
      setResult(data)
      toast({
        title: "Success",
        description: "Image transformed successfully!",
      })
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to transform image. Please try again.",
        variant: "destructive",
      })
    } finally {
      setTransforming(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    )
  }

  return (
    <div className="container mx-auto py-8">
      <h1 className="text-3xl font-bold mb-8">Transform Image</h1>

      {/* Posts Carousel */}
      <div className="mb-8">
        <h2 className="text-xl font-semibold mb-4">Select Image</h2>
        <PostsCarousel
          posts={posts}
          selectedPostId={selectedPost?.id ?? null}
          onSelectPost={setSelectedPost}
        />
      </div>

      {/* Effect Selection */}
      <div className="mb-8">
        <h2 className="text-xl font-semibold mb-4">Select Effect</h2>
        <RadioGroup value={effect} onValueChange={setEffect} className="grid grid-cols-2 gap-4">
          <div>
            <RadioGroupItem value="1" id="grayscale" className="peer sr-only" />
            <Label
              htmlFor="grayscale"
              className="flex flex-col items-center justify-between rounded-md border-2 border-muted bg-popover p-4 hover:bg-accent hover:text-accent-foreground peer-data-[state=checked]:border-primary [&:has([data-state=checked])]:border-primary"
            >
              <ImageIcon className="mb-3 h-6 w-6" />
              Grayscale
            </Label>
          </div>
          <div>
            <RadioGroupItem value="2" id="cartoon" className="peer sr-only" />
            <Label
              htmlFor="cartoon"
              className="flex flex-col items-center justify-between rounded-md border-2 border-muted bg-popover p-4 hover:bg-accent hover:text-accent-foreground peer-data-[state=checked]:border-primary [&:has([data-state=checked])]:border-primary"
            >
              <ImageIcon className="mb-3 h-6 w-6" />
              Cartoon
            </Label>
          </div>
        </RadioGroup>
      </div>

      {/* Transform Button */}
      <Button 
        onClick={handleTransform} 
        disabled={transforming || !selectedPost || !effect}
        className="w-full mb-8"
      >
        {transforming ? (
          <>
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            Transforming...
          </>
        ) : (
          'Transform Image'
        )}
      </Button>

      {/* Results */}
      {result && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <Card>
            <CardContent className="p-4">
              <h3 className="font-medium mb-4">Transformed Image</h3>
              <div className="relative aspect-square">
                <Image
                  src={result.cloudinary_url}
                  alt="Transformed image"
                  fill
                  className="object-cover rounded-md"
                />
              </div>
              <div>
                <a href={result.cloudinary_url}>{result.cloudinary_url}</a>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <h3 className="font-medium mb-4">QR Code</h3>
              <div className="relative aspect-square">
                <Image
                  src={result.qr_code_url}
                  alt="QR Code"
                  fill
                  className="object-cover rounded-md"
                />
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}