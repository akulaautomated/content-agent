import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDate(date: string | Date) {
  return new Date(date).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

export const STATUS_COLORS: Record<string, string> = {
  idea: "bg-gray-100 text-gray-700",
  draft: "bg-yellow-100 text-yellow-700",
  review: "bg-blue-100 text-blue-700",
  approved: "bg-purple-100 text-purple-700",
  scheduled: "bg-orange-100 text-orange-700",
  published: "bg-green-100 text-green-700",
  archived: "bg-gray-100 text-gray-500",
};

export const CONTENT_TYPE_COLORS: Record<string, string> = {
  blog_post: "bg-indigo-100 text-indigo-700",
  email: "bg-pink-100 text-pink-700",
  social_post: "bg-cyan-100 text-cyan-700",
  ad_copy: "bg-amber-100 text-amber-700",
  landing_page: "bg-violet-100 text-violet-700",
  case_study: "bg-teal-100 text-teal-700",
};

export const CONTENT_TYPE_LABELS: Record<string, string> = {
  blog_post: "Blog Post",
  email: "Email",
  social_post: "Social Post",
  ad_copy: "Ad Copy",
  landing_page: "Landing Page",
  case_study: "Case Study",
};
