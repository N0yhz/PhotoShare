"use client"

import { Avatar, AvatarImage, AvatarFallback } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { ProfilePostGrid } from "@/components/profile-post-grid"
import { useToast } from "@/hooks/use-toast"
import { useAuth } from "@/hooks/use-auth"
import { useEffect, useState } from "react"
import { BACKEND_API_BASE_URL } from "@/app/constants"


export default function UserProfile(){
  const [posts, setPosts] = useState([])
  const { user, token } = useAuth()
  const { toast } = useToast()
  const [page, setPage] = useState(1)

  if (!user) return null
  
  useEffect(() => {
    fetchPosts()
  }, [])

  const fetchPosts = async () => {
    try {
      const res = await fetch(`${BACKEND_API_BASE_URL}/api/posts`, {
        headers: {
          "Authorization": `Bearer ${token}`
        }
      })
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
    const res = await fetch(`${BACKEND_API_BASE_URL}/api/posts`, {
      headers: {
        "Authorization": `Bearer ${token}`
      }
    })
    const data = await res.json()
    return data
  }
  return(
    <div className="max-w-xl mx-auto flex flex-col gap-12 mt-4">
        <div className="flex gap-9">
          <Avatar className="size-40">
            <AvatarImage src={user.avatar} alt="User Name" />
            <AvatarFallback>{user.username.slice(0, 2).toUpperCase()}</AvatarFallback>
          </Avatar>
          <div>
            <h1 className="text-2xl font-bold">{user.username}</h1>
            <p className="font-medium mt-3">0 Posts</p>
            <p className="font-medium mt-3">{user.last_name} {user.first_name} </p>
          </div>
          <Button className="h-7">Edit Profile</Button>
        </div>


        <div>
          <h2 className="text-xl font-bold">About Me</h2>
          <p>{user.bio}</p>
        </div>
        <ProfilePostGrid initialPosts={posts} loadMore={loadMore} />
    </div>
  )
}