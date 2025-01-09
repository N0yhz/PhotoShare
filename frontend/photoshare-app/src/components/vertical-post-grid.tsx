"use client"

import { useState, useEffect } from 'react'
import Image from 'next/image'
import { useInView } from 'react-intersection-observer'
import { Card } from '@/components/ui/card'
import { PostModal } from '@/components/post-modal'
import { Skeleton } from '@/components/ui/skeleton'
import { Avatar, AvatarImage, AvatarFallback } from '@/components/ui/avatar'
import { Button} from '@/components/ui/button'
import { MessageCircle } from 'lucide-react'
import { Dot } from 'lucide-react'
import { DialogShareButton } from './share-button'
import { BACKEND_API_BASE_URL } from '@/app/constants'
import { formatDistanceToNow } from 'date-fns'

interface User {
    id: number
    username: string
    avatar: string
}

interface Post {
  id: number
  cloudinary_url: string
  description: string
  user_id: number
  created_at: string
  tags: string[]
}

interface PostGridProps {
  initialPosts: Post[]
  loadMore: () => Promise<Post[]>
}

export function VerticalPostGrid({ initialPosts, loadMore }: PostGridProps) {
  const [posts, setPosts] = useState(initialPosts)
  const [selectedPost, setSelectedPost] = useState<Post | null>(null)
  const [loading, setLoading] = useState(false)
  const [hasMore, setHasMore] = useState(true)
  const [users, setUsers] = useState<{ [key: number]: User }>({})

  useEffect(() => {
    async function fetchUsers() {
        try {
          const response = await fetch(`${BACKEND_API_BASE_URL}/api/auth/users`)
          if (!response.ok) {
            throw new Error('Failed to fetch users')
          }
          const userList: User[] = await response.json()
          const userMap = userList.reduce((acc, user) => {
            acc[user.id] = user
            return acc
          }, {} as { [key: number]: User })
          setUsers(userMap)
        } catch (error) {
          console.error('Error fetching users:', error)
        }
      }
      fetchUsers()
    }, [])

  const { ref, inView } = useInView({
    threshold: 0,
    onChange: async (inView) => {
      if (inView && !loading && hasMore) {
        setLoading(true)
        const newPosts = await loadMore()
        if (newPosts.length === 0) {
          setHasMore(false)
        } else {
          setPosts([...posts, ...newPosts])
        }
        setLoading(false)
      }
    },
  })

  return (
    <div className="max-w-md mx-auto flex flex-col gap-12">
      {posts.map((post) => {
        const user = users[post.user_id]
        return (
          <Card
            key={post.id}
            className="overflow-hidden cursor-pointer transition-transform hover:scale-[1.02]"
            onClick={() => setSelectedPost(post)}
          >
            <div className="flex items-center ml-2 mt-1.5 mb-1.5">
              <Button className="h-9 w-9 rounded-full">
                {user && (
                  <Avatar className="h-9 w-9">
                    <AvatarImage src={user.avatar} alt={user.username} />
                    <AvatarFallback>{user.username.slice(0, 2).toUpperCase()}</AvatarFallback>
                  </Avatar>
                )}
              </Button>
              <div className="ml-3">
                <span className="font-medium">{user ? user.username : 'Loading...'}</span>
              </div>
              <Dot size={22} />
              <div>
                <span className="text-gray-600 text-sm">{formatDistanceToNow(new Date(post.created_at), { addSuffix: true })}</span>
              </div>
            </div>
            <div className="aspect-square relative">
              <Image
                src={post.cloudinary_url}
                alt={post.description || 'Post'}
                fill
                className="object-cover"
              />
            </div>
            <div className="mt-1.1 ml-2">
              <div>
                <Button variant="ghost" size="icon">
                  <MessageCircle size={45} />
                </Button>
                <DialogShareButton />
              </div>
              <div className="flex items-center ml-2 gap-3 mb-1.5">
                <span className="font-medium">{user ? user.username : 'Loading...'}</span>
                <span className="text-gray-600 text-sm"> {post.description}</span>
              </div>
              <div className="text-sm ml-2">
                {post.tags.length > 0 ? (
                    post.tags.map((tag, index) => (
                    <span key={index} className="tag">
                        #{tag.name}
                    </span>
                    ))
                ) : (
                    <span>No tags available</span>
                )}
                </div>
            </div>
          </Card>
        )
      })}
      {selectedPost && (
        <PostModal
          post={selectedPost}
          onClose={() => setSelectedPost(null)}
        />
      )}
      {loading && (
        <div className="grid grid-cols-1 gap-2 mt-2">
          {[...Array(4)].map((_, i) => (
            <Skeleton key={i} className="aspect-square" />
          ))}
        </div>
      )}
      <div ref={ref} className="h-[10vh]" />
    </div>
    
  )
}