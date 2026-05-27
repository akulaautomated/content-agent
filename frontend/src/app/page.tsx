"use client";
import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/store/authStore";

export default function HomePage() {
  const router = useRouter();
  const { isLoggedIn } = useAuthStore();

  useEffect(() => {
    router.replace(isLoggedIn ? "/dashboard" : "/login");
  }, [isLoggedIn, router]);

  return null;
}
