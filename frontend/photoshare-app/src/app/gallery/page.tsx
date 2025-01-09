"use client"

import { useEffect, useState } from 'react'
import { PostGrid } from '@/components/post-grid'
import { Button } from '@/components/ui/button'
import { useToast } from '@/hooks/use-toast'
import { Plus } from 'lucide-react'
import { useAuth } from '@/hooks/use-auth'
import { BACKEND_API_BASE_URL } from '@/app/constants'
import { DialogUploadPost } from '../upload-post/page'

export default function GalleryPage() {
  const [posts, setPosts] = useState([])
  const { user } = useAuth()
  const { toast } = useToast()
  const [page, setPage] = useState(1)
  const [isLoadingMoreEnabled, setIsLoadingMoreEnabled] = useState(true);

  useEffect(() => {
    fetchPosts()
  }, [])

  const fetchPosts = async () => {
    try {
      const res = await fetch(`${BACKEND_API_BASE_URL}/api/posts/all_posts?=${page}`)
      const data = await res.json()
      setPosts(data)
    } catch (error) {
      toast({
        variant: "destructive",
        title: "Error",
        description: "Failed to load posts.",
      })
    }
  }

  const loadMore = async () => {
    if (!isLoadingMoreEnabled) {
      return [];
    }

    const nextPage = page + 1
    setPage(nextPage)
    const res = await fetch(`http://localhost:8000/api/posts/all_posts?page=${nextPage}`)
    const data = await res.json()

    if (data.length === 0) {
      setIsLoadingMoreEnabled(false);
    }
  
    return data
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Post Gallery</h1>
        {user && (
            <DialogUploadPost />
        )}
      </div>
      <PostGrid initialPosts={posts} loadMore={loadMore} />
    </div>
  )
}