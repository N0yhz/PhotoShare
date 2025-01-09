"use client"

import { useState, useEffect } from "react"
import Image from "next/image"
import Link from "next/link"
import { useAuth } from "@/hooks/use-auth"
import { useToast } from "@/hooks/use-toast"
import { Input } from "@/components/ui/input"
import { PostModal } from '@/components/post-modal'
import { Badge } from "@/components/ui/badge"
import { AddTagDialog } from "@/components/add-tag-dialog"
import { Search, Loader2 } from 'lucide-react'
import { BACKEND_API_BASE_URL } from "../constants"

interface Tag {
id: number
name: string
created_at: string
}

interface Post {
id: number
cloudinary_url: string
description: string
tags: Tag[]
user: {
    id: number
    username: string
}
created_at: string
}

export default function ExplorePage() {
  const { token } = useAuth()
  const { toast } = useToast()
  const [tags, setTags] = useState<Tag[]>([])
  const [posts, setPosts] = useState<Post[]>([])
  const [selectedTags, setSelectedTags] = useState<number[]>([])
  const [searchQuery, setSearchQuery] = useState("")
  const [isLoading, setIsLoading] = useState(true)
  const [selectedPost, setSelectedPost] = useState<Post | null>(null)

  const fetchTags = async () => {
    try {
      const response = await fetch(`${BACKEND_API_BASE_URL}/api/tags/all`, {
        headers: {
          "Authorization": `Bearer ${token}`
        }
      })
      if (!response.ok) throw new Error("Failed to fetch tags")
      const data = await response.json()
      setTags(data)
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load tags",
        variant: "destructive"
      })
    }
  }

  const fetchPosts = async () => {
    setIsLoading(true)
    try {
        let url = `${BACKEND_API_BASE_URL}/api/posts/`

      if (selectedTags.length > 0) {
        // Fetch posts by tag IDs
        url += `by-tags/${selectedTags.join(",")}`
      } else if (searchQuery) {
        // Fetch posts by tag name (search)
        url += `by-tags/${encodeURIComponent(searchQuery)}`
      } else {
        // Fetch all posts if no tags or search query is provided
        url += "all_posts"
      }
  
        const response = await fetch(url, {
          headers: {
            "Authorization": `Bearer ${token}`
          }
        })
        if (!response.ok) throw new Error("Failed to fetch posts")
        const data = await response.json()
        setPosts(data)
      } catch (error) {
        toast({
          title: "Error",
          description: "Failed to load posts",
          variant: "destructive"
        })
      } finally {
        setIsLoading(false)
      }
    }

  useEffect(() => {
    fetchTags()
  }, [])

  useEffect(() => {
    fetchPosts()
  }, [selectedTags, searchQuery])

  const toggleTag = (tagId: number) => {
    setSelectedTags(prev =>
      prev.includes(tagId)
        ? prev.filter(id => id !== tagId)
        : [...prev, tagId]
    )
  }

  return (
    <div className="container py-10 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Explore</h1>
        <AddTagDialog onTagAdded={fetchTags} />
      </div>

      <div className="flex items-center space-x-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Search posts..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10"
          />
        </div>
      </div>

      <div className="flex flex-wrap gap-2">
        {tags.map((tag) => (
          <Badge
            key={tag.id}
            variant={selectedTags.includes(tag.id) ? "default" : "outline"}
            className="cursor-pointer"
            onClick={() => toggleTag(tag.id)}
          >
            {tag.name}
          </Badge>
        ))}
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center min-h-[200px]">
          <Loader2 className="h-8 w-8 animate-spin" />
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {posts.map((post) => (
            <Link
              key={post.id}
              href={`/posts/${post.id}`}
              className="group relative aspect-square overflow-hidden rounded-lg"
            >
              <Image
                src={post.cloudinary_url}
                alt={post.description || "Post image"}
                fill
                className="object-cover transition-transform group-hover:scale-105"
              />
               {selectedPost && (
                    <PostModal
                    post={selectedPost}
                    onClose={() => setSelectedPost(null)}
                    />
                )}
              <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-end p-4">
                <div className="space-y-2">
                  <div className="flex flex-wrap gap-1">
                    {post.tags.map((tag) => (
                      <Badge key={tag.id} variant="secondary" className="text-xs">
                        {tag.name}
                      </Badge>
                    ))}
                  </div>
                  {post.description && (
                    <p className="text-sm text-white line-clamp-2">
                      {post.description}
                    </p>
                  )}
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}

      {!isLoading && posts.length === 0 && (
        <div className="text-center py-10 text-muted-foreground">
          No posts found. Try adjusting your search or tags.
        </div>
      )}
    </div>
  )
}