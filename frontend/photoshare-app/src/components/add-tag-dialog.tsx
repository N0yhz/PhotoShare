"use client"

import { useState } from "react"
import { useAuth } from "@/hooks/use-auth"
import { useToast } from "@/hooks/use-toast"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Plus, Loader2 } from 'lucide-react'
import { BACKEND_API_BASE_URL } from "@/app/constants"

interface AddTagDialogProps {
  onTagAdded: () => void
}

export function AddTagDialog({ onTagAdded }: AddTagDialogProps) {
  const { token } = useAuth()
  const { toast } = useToast()
  const [tagName, setTagName] = useState("")
  const [isOpen, setIsOpen] = useState(false)
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!tagName.trim()) return

    setIsLoading(true)
    try {
      const response = await fetch(`${BACKEND_API_BASE_URL}/api/tags/create`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({ name: tagName.trim() })
      })

      if (!response.ok) {
        throw new Error("Failed to create tag")
      }

      toast({
        title: "Success",
        description: "Tag created successfully"
      })
      setTagName("")
      setIsOpen(false)
      onTagAdded()
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to create tag",
        variant: "destructive"
      })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" size="sm">
          <Plus className="h-4 w-4 mr-2" />
          Create Tag
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[425px]">
        <form onSubmit={handleSubmit}>
          <DialogHeader>
            <DialogTitle>Create New Tag</DialogTitle>
            <DialogDescription>
              Create a new tag to categorize posts
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <Input
              placeholder="Enter tag name..."
              value={tagName}
              onChange={(e) => setTagName(e.target.value)}
              disabled={isLoading}
            />
          </div>
          <DialogFooter>
            <Button type="submit" disabled={!tagName.trim() || isLoading}>
              {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Create Tag
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}

