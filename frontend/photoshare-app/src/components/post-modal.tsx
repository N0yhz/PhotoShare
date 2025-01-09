"use client"

import { useState, useEffect } from 'react'
import Image from 'next/image'
import { formatDistanceToNow } from 'date-fns'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { useAuth } from '@/hooks/use-auth'
import { Heart, MessageCircle, Share, Trash2, Pencil } from 'lucide-react'
import { useToast } from '@/hooks/use-toast'
import { BACKEND_API_BASE_URL } from '@/app/constants'
import { DialogShareButton } from './share-button'

interface Post {
  id: number
  cloudinary_url: string
  description: string
  user: {
    username: string
  }
  created_at: string
}

interface PostModalProps {
  post: Post
  onClose: () => void
}

interface Comment {
  id: number
  content: string
  created_at: string
  user: {
    id: number
    username: string
    avatar: string
  }
  post_id: number
}

interface CommentCreate {
  content: string
}
interface CommentUpdate {
  content: string
}

export function PostModal({ post, onClose }: PostModalProps) {
  const { user, token} = useAuth()
  const { toast } = useToast()
  const [comment, setComment] = useState('')
  const [comments, setComments] = useState<Comment[]>([])
  const [isLiked, setIsLiked] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [editingComment, setEditingComment] = useState<{
    id: number
    content: string
  } | null>(null)
  const [tag, setTag] = useState("");
  const [tags, setTags] = useState<string[]>([]);

  if(!user) return null

  useEffect(() => {
    fetchComments()
  }, [post.id])

  useEffect(() => {
    console.log('Comments:', comments);
  }, [comments])

  useEffect(() => {
    fetchTags();
  }, [post.id]);

  const fetchComments = async () => {
    try {
      const response = await fetch(`${BACKEND_API_BASE_URL}/api/comments/${post.id}/comments`)
      if (!response.ok) throw new Error('Failed to fetch comments')
      const data = await response.json()
      setComments(data)
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load comments",
        variant: "destructive"
      })
    }
  }

  const fetchTags = async () => {
    try {
      const response = await fetch(`${BACKEND_API_BASE_URL}/api/tags/all`);
      if (!response.ok) throw new Error('Failed to fetch tags');
      const data = await response.json();
      setTags(data);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load tags",
        variant: "destructive"
      });
    }
  };

  const handleComment = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)

    try {
      const formData = new FormData()
      formData.append('content', comment)

      const response = await fetch(`${BACKEND_API_BASE_URL}/api/comments/${post.id}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
      },
        body: formData,
      })

      if (!response.ok) throw new Error('Failed to post comment')

      const newComment = await response.json()
      setComments(prev => [...prev, newComment])
      setComment('')
      toast({
        title: "Success",
        description: "Comment posted successfully",
      })
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to post comment",
        variant: "destructive"
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handleEditComment = async (commentId: number, content: string) => {
    try {
      const response = await fetch(`${BACKEND_API_BASE_URL}/api/comments/${commentId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ content }),
      })

      if (!response.ok) throw new Error('Failed to update comment')

      const updatedComment = await response.json()
      setComments(prev =>
        prev.map(c => (c.id === commentId ? updatedComment : c))
      )
      setEditingComment(null)
      toast({
        title: "Success",
        description: "Comment updated successfully",
      })
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to update comment",
        variant: "destructive"
      })
    }
  }

  const handleDeleteComment = async (commentId: number) => {
    try {
      const response = await fetch(`${BACKEND_API_BASE_URL}/api/comments/${commentId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        }
      })

      if (!response.ok) throw new Error('Failed to delete comment')

      setComments(prev => prev.filter(c => c.id !== commentId))
      toast({
        title: "Success",
        description: "Comment deleted successfully",
      })
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to delete comment",
        variant: "destructive"
      })
    }
  }

  const isAdmin = user?(user.role === 'admin' || user.role === 'moderator') : false;

  const handleAddTag = async () => {
    if (!tag.trim()) return; // Prevent empty tags
  
    try {
      const response = await fetch(`${BACKEND_API_BASE_URL}/api/posts/${post.id}/tags`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ name: tag }),
      });
  
      if (!response.ok) throw new Error('Failed to add tag');
  
      toast({
        title: "Success",
        description: "Tag added successfully",
      });
      setTag(''); // Clear the input
      fetchTags(); // Refresh tags
    } catch (error) {
      console.error(error);
      toast({
        title: "Error",
        description: "Failed to add tag",
        variant: "destructive"
      });
    }
  };

  return (
    <Dialog open onOpenChange={onClose}>
      <DialogContent className="max-w-5xl p-0 overflow-hidden">
        <div className="grid md:grid-cols-[1fr,400px]">
          <div className="relative aspect-square">
            <Image
              src={post.cloudinary_url}
              alt={post.description || 'Photo'}
              fill
              className="object-cover"
            />
          </div>
          <div className="flex flex-col h-[600px] p-4">
            <DialogHeader>
              <DialogTitle className="flex items-center gap-2">
                {post.user &&
                  <Avatar className="h-8 w-8">
                  <AvatarFallback>
                    {post.user.username.slice(0, 2).toUpperCase()}
                  </AvatarFallback>
                </Avatar>
                }
                {post.user &&
                <span>{post.user.username}</span>
                }
              </DialogTitle>
            </DialogHeader>
            <div className="flex-1 overflow-y-auto py-4">
              {post.description && (
                <p className="text-sm text-muted-foreground mb-4">
                  {post.description}
                </p>
              )}
              <div className="space-y-4">
                {comments.map((comment) => (
                  <div key={comment.id} className="flex gap-2 group">
                      <Avatar>
                        {comment.user && comment.user.avatar && comment.user.avatar !== null ? (
                          <AvatarImage src={comment.user.avatar} alt={comment.user.username} />
                        ) : (
                          <AvatarFallback>
                            {comment.user && comment.user.username ? comment.user.username.slice(0, 2).toUpperCase() : "AN"}
                          </AvatarFallback>
                        )}
                      </Avatar>
                    <div className="flex-1">
                      {editingComment?.id === comment.id ? (
                        <form
                          onSubmit={(e) => {
                            e.preventDefault()
                            handleEditComment(comment.id, editingComment.content)
                          }}
                          className="flex gap-2"
                        >
                          <Input
                            value={editingComment.content}
                            onChange={(e) =>
                              setEditingComment({
                                ...editingComment,
                                content: e.target.value,
                              })
                            }
                            className="text-sm"
                          />
                          <Button type="submit" size="sm">
                            Save
                          </Button>
                          <Button
                            type="button"
                            variant="ghost"
                            size="sm"
                            onClick={() => setEditingComment(null)}
                          >
                            Cancel
                          </Button>
                        </form>
                      ) : (
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center">
                              <span className="font-medium mr-2">
                                {comment.user ? comment.user.username : "Anonymous"}
                              </span>
                              <span className="text-xs text-muted-foreground">
                                {formatDistanceToNow(new Date(comment.created_at), { addSuffix: true })}
                              </span>
                            </div>
                            <p className="text-sm">
                              {comment.content || "No content"}
                            </p>
                          </div>
                          {(user?.id === comment?.user?.id || isAdmin) && (
                            <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                              {user?.id === comment.user?.id && (
                                <Button
                                  variant="ghost"
                                  size="icon"
                                  className="h-8 w-8"
                                  onClick={() =>
                                    setEditingComment({
                                      id: comment.id,
                                      content: comment.content,
                                    })
                                  }
                                >
                                  <Pencil className="h-4 w-4" />
                                </Button>
                              )}
                              <Button
                                variant="ghost"
                                size="icon"
                                className="h-8 w-8 text-destructive"
                                onClick={() => handleDeleteComment(comment.id)}
                              >
                                <Trash2 className="h-4 w-4" />
                              </Button>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
            <div className="border-t pt-4">
              <div className="flex gap-4 mb-4">
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => setIsLiked(!isLiked)}
                >
                  <Heart
                    className={`h-6 w-6 ${
                      isLiked ? 'fill-red-500 text-red-500' : ''
                    }`}
                  />
                </Button>
                <Button variant="ghost" size="icon">
                  <MessageCircle className="h-6 w-6" />
                </Button>
                <Input
                  placeholder="Add a tag..."
                  value={tag}
                  onChange={(e) => setTag(e.target.value)}
                  className="mr-2"
                />
                <Button type="button" onClick={handleAddTag}>
                  Add Tag
                </Button>
                <DialogShareButton />
              </div>
              {user && (
                <form onSubmit={handleComment} className="flex gap-2">
                  <Input
                    placeholder="Add a comment..."
                    value={comment}
                    onChange={(e) => setComment(e.target.value)}
                    disabled={isLoading}
                  />
                  <Button type="submit" disabled={!comment.trim() || isLoading}>
                    {isLoading ? 'Posting...' : 'Post'}
                  </Button>
                </form>
              )}
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}