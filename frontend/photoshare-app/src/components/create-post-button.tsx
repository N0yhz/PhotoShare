'use client'

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Dialog, 
        DialogContent, 
        DialogHeader, 
        DialogTitle } from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Plus } from 'lucide-react'
import { useAuth } from "@/hooks/use-auth"
import { BACKEND_API_BASE_URL } from "@/app/constants"

export function CreatePostButton() {
  const [open, setOpen] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [file, setFile] = useState<File | null>(null)
  const [description, setDescription] = useState("")
  const { user, token } = useAuth()

  if (!user){
    return null
    }

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0];
    setFile(selectedFile || null);
  };

    const handleDescriptionChange = (event: React.ChangeEvent<HTMLTextAreaElement>) => {
        setDescription(event.target.value);
    }

    const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault()
        setIsLoading(true)
        
        if (!file) {
            alert('Please select a file to upload.');
            return;
        }

        const formData = new FormData();
        formData.append("file", file);
        formData.append('description', description);

        try {
            const res = await fetch(`${BACKEND_API_BASE_URL}/api/posts/create`, {
                method: "POST",
                headers: {
                    'Authorization': `Bearer ${token}`,
                },
                body: formData,
            });
            if (!res.ok) {
                throw new Error('Failed to upload post.');
            }

            const data = await res.json();
            console.log('Post created:', data);
            setIsLoading(false)
        } catch (err) {
            console.error(err);
        }
    }
   

  return (
    <>
      <Button onClick={() => setOpen(true)}>
        <Plus className="mr-2 h-4 w-4" />
        Create Post
      </Button>

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Create New Post</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <Input
                type="file"
                name="file"
                id="file"
                accept="image/*"
                onChange={handleFileChange}
                required
              />
            </div>
            <div>
              <Textarea
                id="description"
                 name="description"
                placeholder="Write a description..."
                value={description}
                onChange={handleDescriptionChange}
              />
            </div>
            <div className="flex justify-end">
              <Button type="submit" disabled={isLoading}>
                {isLoading ? "Creating..." : "Create Post"}
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
    </>
  )
}