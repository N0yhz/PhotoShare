'use client'

import { useState, useEffect } from "react"
import { Card, CardContent, CardFooter } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Pencil, Trash2 } from 'lucide-react'
import { EditPostDialog } from "./edit-post-dialog"
import { DeletePostDialog } from "./delete-post-dialog"
import { useAuth } from "@/hooks/use-auth"
import { BACKEND_API_BASE_URL } from "@/app/constants"

interface Post {
  id: number
  description: string
  cloudinary_url: string
  created_at: string
  user_id: number
}

export function PostList() {
  const [posts, setPosts] = useState<Post[]>([])
  const [loading, setLoading] = useState(true)
  const [editingPost, setEditingPost] = useState<Post | null>(null)
  const [deletingPost, setDeletingPost] = useState<Post | null>(null)
  const { user, token } = useAuth()

  useEffect(() => {
    if (token && user) {
      fetchPosts()
    }
  }, [token, user])

  const fetchPosts = async () => {
    try {
      const response = await fetch(`${BACKEND_API_BASE_URL}/api/posts/`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      if (!response.ok) throw new Error('Failed to fetch posts')
      const data = await response.json()
      setPosts(data)
    } catch (error) {
      console.error('Error fetching posts:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="text-center">Loading posts...</div>
  }

  return (
    <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
      {posts.map((post) => (
        <Card key={post.id} className="overflow-hidden">
          {/* {console.log('Post user_id:', post.user_id, 'Current user:', user)} */}
          <CardContent className="p-0">
            <img
              src={post.cloudinary_url}
              alt={post.description || 'Post image'}
              className="w-full h-64 object-cover"
            />
            <div className="p-4">
              <p className="text-sm text-gray-600">{post.description}</p>
            </div>
          </CardContent>
          {user && (
            <CardFooter className="flex justify-end gap-2 p-4">
              <Button
                variant="outline"
                size="icon"
                onClick={() => setEditingPost(post)}
              >
                <Pencil className="h-4 w-4" />
              </Button>
              <Button
                variant="outline"
                size="icon"
                onClick={() => setDeletingPost(post)}
                className="text-destructive"
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            </CardFooter>
          )}
        </Card>
      ))}

      <EditPostDialog
        post={editingPost}
        onClose={() => setEditingPost(null)}
        onUpdate={fetchPosts}
      />
      <DeletePostDialog
        post={deletingPost}
        onClose={() => setDeletingPost(null)}
        onDelete={fetchPosts}
      />
    </div>
  )
}