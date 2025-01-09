"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import Image from "next/image"
import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import * as z from "zod"
import { useAuth } from "@/hooks/use-auth"
import { Button } from "@/components/ui/button"
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { useToast } from "@/hooks/use-toast"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { ImagePlus, Loader2 } from 'lucide-react'
import { BACKEND_API_BASE_URL } from "../constants"

interface UserSettings {
    username: string
    first_name: string
    last_name: string
    bio: string
    avatar: string
}
  
interface UpdateUserSettings {
    username: string
    first_name: string
    last_name: string
    bio: string
}

const settingsFormSchema = z.object({
  username: z.string()
    .min(3, "Username must be at least 3 characters")
    .max(30, "Username must not exceed 30 characters"),
  first_name: z.string()
    .min(1, "First name is required")
    .max(50, "First name must not exceed 50 characters"),
  last_name: z.string()
    .min(1, "Last name is required")
    .max(50, "Last name must not exceed 50 characters"),
  bio: z.string()
    .max(500, "Bio must not exceed 500 characters")
    .optional(),
})

export default function SettingsPage() {
  const router = useRouter()
  const { user, token} = useAuth()
  const { toast } = useToast()
  const [isLoading, setIsLoading] = useState(false)
  const [avatarFile, setAvatarFile] = useState<File | null>(null)
  const [avatarPreview, setAvatarPreview] = useState<string>("/placeholder.svg?height=200&width=200")

  const form = useForm<z.infer<typeof settingsFormSchema>>({
    resolver: zodResolver(settingsFormSchema),
    defaultValues: {
      username: "",
      first_name: "",
      last_name: "",
      bio: "",
    },
  })

  useEffect(() => {
    if (!user) {
      router.push("/login")
      return
    }

    // Load current user settings
    const fetchSettings = async () => {
      try {
        const response = await fetch(`${BACKEND_API_BASE_URL}/api/auth/me`, {
          headers: {
            "Authorization": `Bearer ${token}`
          }
        })
        if (!response.ok) throw new Error("Failed to fetch user settings")
        const data: UserSettings = await response.json()
        
        form.reset({
          username: data.username,
          first_name: data.first_name,
          last_name: data.last_name,
          bio: data.bio || "",
        })

        if (data.avatar) {
          setAvatarPreview(data.avatar)
        }
      } catch (error) {
        toast({
          title: "Error",
          description: "Failed to load user settings",
          variant: "destructive"
        })
      }
    }

    fetchSettings()
  }, [user, token])

  const handleAvatarChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      setAvatarFile(file)
      const reader = new FileReader()
      reader.onloadend = () => {
        setAvatarPreview(reader.result as string)
      }
      reader.readAsDataURL(file)
    }
  }

  const onSubmit = async (values: z.infer<typeof settingsFormSchema>) => {
    setIsLoading(true)

    try {
      // Upload avatar if changed
      if (avatarFile) {
        const formData = new FormData()
        formData.append("avatar", avatarFile)
        
        const avatarResponse = await fetch(`${BACKEND_API_BASE_URL}/api/auth/update-avatar`, {
          method: "POST",
          headers: {
            "Authorization": `Bearer ${token}`
          },
          body: formData,
        })

        if (!avatarResponse.ok) {
          throw new Error("Failed to upload avatar")
        }
      }

      // Update user settings
      const response = await fetch(`${BACKEND_API_BASE_URL}/api/auth/update-profile`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify(values),
      })

      if (!response.ok) {
        throw new Error("Failed to update settings")
      }

      const updatedUser = await response.json()
      setUser(updatedUser)

      toast({
        title: "Success",
        description: "Settings updated successfully",
      })
    } catch (error) {
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to update settings",
        variant: "destructive"
      })
    } finally {
      setIsLoading(false)
    }
  }

  if (!user) return null

  return (
    <div className="container max-w-2xl py-10">
      <Card>
        <CardHeader>
          <CardTitle>Settings</CardTitle>
          <CardDescription>
            Manage your account settings and profile information
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8">
              <div className="flex flex-col items-center space-y-4">
                <div className="relative h-32 w-32">
                  <Image
                    src={avatarPreview}
                    alt="Avatar preview"
                    fill
                    className="rounded-full object-cover"
                  />
                  <label
                    htmlFor="avatar-upload"
                    className="absolute inset-0 flex cursor-pointer items-center justify-center rounded-full bg-black/50 opacity-0 hover:opacity-100 transition-opacity"
                  >
                    <ImagePlus className="h-8 w-8 text-white" />
                    <Input
                      id="avatar-upload"
                      type="file"
                      name="file"
                      accept="image/*" 
                      onChange={handleAvatarChange}
                      className="sr-only"
                    />
                  </label>
                </div>
                <p className="text-sm text-muted-foreground">
                  Click to upload new avatar
                </p>
              </div>

              <FormField
                control={form.control}
                name="username"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Username</FormLabel>
                    <FormControl>
                      <Input {...field} />
                    </FormControl>
                    <FormDescription>
                      This is your public display name
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <div className="grid gap-4 md:grid-cols-2">
                <FormField
                  control={form.control}
                  name="first_name"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>First Name</FormLabel>
                      <FormControl>
                        <Input {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="last_name"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Last Name</FormLabel>
                      <FormControl>
                        <Input {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>

              <FormField
                control={form.control}
                name="bio"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Bio</FormLabel>
                    <FormControl>
                      <Textarea
                        {...field}
                        placeholder="Tell us about yourself"
                        className="resize-none"
                        rows={4}
                      />
                    </FormControl>
                    <FormDescription>
                      Brief description for your profile
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <Button type="submit" disabled={isLoading}>
                {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                {isLoading ? "Saving..." : "Save Changes"}
              </Button>
            </form>
          </Form>
        </CardContent>
      </Card>
    </div>
  )
}

