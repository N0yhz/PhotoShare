"use client"

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Button } from "@/components/ui/button";
import { ModeToggle } from '@/components/mode-toggle';
import { UserNav } from '@/components/user-nav';
import { useAuth } from '@/hooks/use-auth';
import { Camera } from 'lucide-react';


export function Header() {
    const pathname = usePathname()
    const { user } = useAuth()
  
    return (
      <header className="border-b">
        <div className="container mx-auto flex h-16 items-center px-4">
          <Link href="/" className="flex items-center space-x-2">
            <Camera className="h-6 w-6" />
            <span className="font-bold">PhotoShare</span>
          </Link>
          <nav className="ml-6 flex gap-6">
            <Link 
              href="/gallery" 
              className={`text-sm font-medium ${
                pathname === '/gallery' ? 'text-primary' : 'text-muted-foreground'
              } transition-colors hover:text-primary`}
            >
              Gallery
            </Link>
            <Link 
              href="/explore" 
              className={`text-sm font-medium ${
                pathname === '/explore' ? 'text-primary' : 'text-muted-foreground'
              } transition-colors hover:text-primary`}
            >
              Explore
            </Link>
            <Link 
              href="/transformation" 
              className={`text-sm font-medium ${
                pathname === '/transformation' ? 'text-primary' : 'text-muted-foreground'
              } transition-colors hover:text-primary`}
            >
              Image Edit
            </Link>
            <Link 
              href="/post-edit-delete" 
              className={`text-sm font-medium ${
                pathname === '/post-edit-delete' ? 'text-primary' : 'text-muted-foreground'
              } transition-colors hover:text-primary`}
            >
              Post Edit
            </Link>
          </nav>
          <div className="ml-auto flex items-center space-x-4">
            <ModeToggle />
            {user ? (
              <UserNav />
            ) : (
              <div className="flex gap-4">
                <Button variant="ghost" asChild>
                  <Link href="/login">Login</Link>
                </Button>
                <Button asChild>
                  <Link href="/register">Register</Link>
                </Button>
              </div>
            )}
          </div>
        </div>
      </header>
    )
  }  
