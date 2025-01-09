import { PostList } from "@/components/post-list"
import { CreatePostButton } from "@/components/create-post-button"

export default function PostsPage() {
  return (
    <div className="container py-8">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold">Posts</h1>
        <CreatePostButton />
      </div>
      <PostList />
    </div>
  )
}