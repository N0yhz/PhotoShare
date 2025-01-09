"use client"

import { useState, useEffect } from 'react'
import Image from 'next/image'
import { useInView } from 'react-intersection-observer'
import { Card } from '@/components/ui/card'
import { PostModal } from '@/components/post-modal'
import { Skeleton } from '@/components/ui/skeleton'

interface Post {
  id: number
  cloudinary_url: string
  description: string
  user: {
    username: string
  }
  created_at: string
}

interface PostGridProps {
  initialPosts: Post[]
  loadMore: () => Promise<Post[]>
}

export function ProfilePostGrid({ initialPosts, loadMore }: PostGridProps) {
  const [posts, setPosts] = useState(initialPosts)
  const [selectedPost, setSelectedPost] = useState<Post | null>(null)
  const [loading, setLoading] = useState(false)
  const [hasMore, setHasMore] = useState(true)

  useEffect(() => {
    // Filter out duplicates from initialPosts
    if (Array.isArray(initialPosts)) {
      const uniquePosts = initialPosts.filter((post, index, self) => 
        index === self.findIndex(p => p.id === post.id)
      );
      setPosts(uniquePosts);
    } else {
      console.error('initialPosts is not an array:', initialPosts);
    }
  }, []);
  
  const { ref, inView } = useInView({
    threshold: 0,
    onChange: async (inView) => {
      if (inView && !loading && hasMore) {
        setLoading(true);
        const newPosts = await loadMore();
        if (newPosts.length === 0) {
          setHasMore(false);
        } else {
          setPosts([...posts, ...newPosts]); // Corrected spread operator
        }
        setLoading(false);
      }
    },
  })

  return (
    <>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-3">
        {posts.map((post) => (
          <Card
            key={post.id}
            className="overflow-hidden cursor-pointer transition-transform hover:scale-[1.02]"
            onClick={() => setSelectedPost(post)}
          >
            <div className="aspect-square relative">
              <Image
                src={post.cloudinary_url}
                alt={post.description || 'Post'}
                fill
                className="object-cover"
              />
            </div>
          </Card>
        ))}
      </div>
      {loading && (
        <div className="grid grid-cols-1 gap-4 mt-4 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-3">
          {[...Array(3)].map((_, i) => (
            <Skeleton key={i} className="aspect-square" />
          ))}
        </div>
      )}
      <div ref={ref} className="h-10" />
      {selectedPost && (
        <PostModal
          post={selectedPost}
          onClose={() => setSelectedPost(null)}
        />
      )}
    </>
  )
}