'use client'

import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog"
import { useAuth } from "@/hooks/use-auth"
import { BACKEND_API_BASE_URL } from "@/app/constants"
import { useToast } from "@/hooks/use-toast"

interface Post {
  id: number
  description: string
  user_id: number
}

interface DeletePostDialogProps {
  post: Post | null
  onClose: () => void
  onDelete: () => void
}

export function DeletePostDialog({ post, onClose, onDelete }: DeletePostDialogProps) {
  const { token, user } = useAuth()
  const { toast } = useToast()

  const handleDelete = async () => {
    if (!post || !token || post.user_id !== user?.id) return

    try {
      const response = await fetch(`${BACKEND_API_BASE_URL}/api/posts/${post.id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (!response.ok) throw new Error('Failed to delete post')

      toast({
        title: "Success",
        description: "Post deleted successfully",
      })

      onDelete()
      onClose()
    } catch (error) {
      console.error('Error deleting post:', error)
      toast({
        title: "Error",
        description: "Failed to delete post",
        variant: "destructive",
      })
    }
  }

  return (
    <AlertDialog open={!!post} onOpenChange={() => onClose()}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Are you sure?</AlertDialogTitle>
          <AlertDialogDescription>
            This action cannot be undone. This will permanently delete your post.
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel onClick={onClose}>Cancel</AlertDialogCancel>
          <AlertDialogAction onClick={handleDelete}>Delete</AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  )
}