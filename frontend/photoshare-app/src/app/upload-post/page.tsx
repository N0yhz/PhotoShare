import { useState } from "react"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { BACKEND_API_BASE_URL } from "../constants"
import { useAuth } from "@/hooks/use-auth"
import { Textarea } from "@/components/ui/textarea"


export function DialogUploadPost() {
    const [isLoading, setIsLoading] = useState(false)
    const [file, setFile] = useState<File | null>(null)
    const {user, token} = useAuth()
    const [description, setDescription] = useState<string>("");

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
        <Dialog>
        <DialogTrigger asChild>
            <Button>Upload File</Button>
        </DialogTrigger>
        <DialogContent className="sm:max-w-[425px]">
            <DialogHeader>
            <DialogTitle>Create a new post</DialogTitle>
            <DialogDescription>
                Fill the form bellow to create a new post
            </DialogDescription>
            </DialogHeader>
            <div className="grid gap-4 py-4">
                <form onSubmit={handleSubmit}>
                    <div className="grid grid-cols-4 items-center gap-4 mb-2">
                        <Label htmlFor="file" className="text-right">
                        Image
                        </Label>
                        <Input 
                            type="file"
                            id="file"
                            name="file"
                            accept="image/*" 
                            onChange={handleFileChange} 
                            className="col-span-3" 
                        />
                    </div>
                    <div className="grid grid-cols-4 items-center gap-4 mb-2">
                        <Label htmlFor="descriptiion" className="text-right">
                        Description
                        </Label>
                        <Textarea
                            id="description"
                            name="description"
                            value={description}
                            onChange={handleDescriptionChange} 
                            placeholder="description" 
                            className="col-span-3" 
                        />
                    </div>
                    <Button type="submit" className="w-full mt-2" disabled={isLoading}>
                        {isLoading ? 'Creating...' : 'Creat'}
                    </Button>
                </form>
            </div>
        </DialogContent>
        </Dialog>
    )
}
