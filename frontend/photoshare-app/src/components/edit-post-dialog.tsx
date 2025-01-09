'use client'

import { useState } from "react"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { useAuth } from "@/hooks/use-auth"
import { BACKEND_API_BASE_URL } from "@/app/constants"
import { useToast } from "@/hooks/use-toast"

interface Post {
  id: number
  description: string
  cloudinary_url: string
  user_id: number
}

interface EditPostDialogProps {
  post: Post | null
  onClose: () => void
  onUpdate: () => void
}

export function EditPostDialog({ post, onClose, onUpdate }: EditPostDialogProps) {
  const [description, setDescription] = useState(post?.description || "")
  const [loading, setLoading] = useState(false)
  const { token, user } = useAuth()
  const { toast } = useToast()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!post || !token || post.user_id !== user?.id) return

    setLoading(true)
    try {
      const response = await fetch(`${BACKEND_API_BASE_URL}/api/posts/${post.id}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ description }),
      })

      if (!response.ok) throw new Error('Failed to update post')

      toast({
        title: "Success",
        description: "Post updated successfully",
      })

      onUpdate()
      onClose()
    } catch (error) {
      console.error('Error updating post:', error)
      toast({
        title: "Error",
        description: "Failed to update post",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <Dialog open={!!post} onOpenChange={() => onClose()}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Edit Post</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <Textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Write a description..."
          />
          <div className="flex justify-end">
            <Button type="submit" disabled={loading}>
              {loading ? "Updating..." : "Update Post"}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  )
}