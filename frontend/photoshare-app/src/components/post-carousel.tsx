'use client'

import * as React from "react"
import Image from "next/image"
import { Card, CardContent } from "@/components/ui/card"
import {
  Carousel,
  CarouselContent,
  CarouselItem,
  CarouselNext,
  CarouselPrevious,
} from "@/components/ui/carousel"

interface Post {
    id: number
    cloudinary_url: string
    description: string
    created_at: string
    updated_at: string
    user_id: number
}  

interface PostsCarouselProps {
  posts: Post[]
  selectedPostId: number | null
  onSelectPost: (post: Post) => void
}

export function PostsCarousel({ posts, selectedPostId, onSelectPost }: PostsCarouselProps) {
  return (
    <Carousel className="w-full max-w-4xl mx-auto">
      <CarouselContent>
        {posts.map((post) => (
          <CarouselItem key={post.id} className="md:basis-1/2 lg:basis-1/3">
            <Card 
              className={`cursor-pointer transition-all ${
                selectedPostId === post.id ? 'ring-2 ring-primary' : ''
              }`}
              onClick={() => onSelectPost(post)}
            >
              <CardContent className="p-4">
                <div className="relative aspect-square mb-4">
                  <Image
                    src={post.cloudinary_url}
                    alt={post.description || 'Post image'}
                    fill
                    className="object-cover rounded-md"
                  />
                </div>
                {post.description && (
                  <p className="text-sm text-muted-foreground line-clamp-2">
                    {post.description}
                  </p>
                )}
              </CardContent>
            </Card>
          </CarouselItem>
        ))}
      </CarouselContent>
      <CarouselPrevious />
      <CarouselNext />
    </Carousel>
  )
}

