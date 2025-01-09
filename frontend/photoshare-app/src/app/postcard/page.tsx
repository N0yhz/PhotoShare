"use client"

import { useEffect, useState } from 'react'
import { useToast } from '@/hooks/use-toast'
import { BACKEND_API_BASE_URL } from '@/app/constants'
import { VerticalPostGrid } from '@/components/vertical-post-grid'

export default function PostCard(){
    const [posts, setPosts] = useState([])
    const { toast } = useToast()
    const [page, setPage] = useState(1)

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
        const nextPage = page + 1
        setPage(nextPage)
        const res = await fetch(`http://localhost:8000/api/posts/all_posts?page=${nextPage}`)
        const data = await res.json()
        return data
    }


    return(
    <div>
       <VerticalPostGrid initialPosts={posts} loadMore={loadMore} />
    </div>
    )
}