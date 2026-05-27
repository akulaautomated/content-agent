"use client";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect } from "react";
import { useAuthStore } from "@/store/authStore";
import {
  LayoutDashboard, FileText, CalendarDays, Target,
  BarChart3, Search, Palette, Settings, LogOut, Sparkles
} from "lucide-react";

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/content", label: "Content", icon: FileText },
  { href: "/calendar", label: "Calendar", icon: CalendarDays },
  { href: "/campaigns", label: "Campaigns", icon: Target },
  { href: "/analytics", label: "Analytics", icon: BarChart3 },
  { href: "/seo", label: "SEO", icon: Search },
  { href: "/brands", label: "Brands", icon: Palette },
];

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const { isLoggedIn, logout } = useAuthStore();

  useEffect(() => {
    if (!isLoggedIn) router.replace("/login");
  }, [isLoggedIn, router]);

  if (!isLoggedIn) return null;

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <aside className="w-56 bg-white border-r border-gray-200 flex flex-col">
        <div className="p-5 border-b border-gray-100">
          <div className="flex items-center gap-2">
            <Sparkles className="text-indigo-600" size={20} />
            <span className="font-bold text-gray-900 text-lg">ContentAgent</span>
          </div>
          <p className="text-xs text-gray-400 mt-0.5">AI Marketing Platform</p>
        </div>

        <nav className="flex-1 p-3 space-y-0.5">
          {navItems.map(({ href, label, icon: Icon }) => {
            const active = pathname === href || pathname.startsWith(href + "/");
            return (
              <Link
                key={href}
                href={href}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                  active
                    ? "bg-indigo-50 text-indigo-700"
                    : "text-gray-600 hover:bg-gray-50 hover:text-gray-900"
                }`}
              >
                <Icon size={16} />
                {label}
              </Link>
            );
          })}
        </nav>

        <div className="p-3 border-t border-gray-100">
          <Link
            href="/settings"
            className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm text-gray-600 hover:bg-gray-50 transition-all"
          >
            <Settings size={16} />
            Settings
          </Link>
          <button
            onClick={() => { logout(); router.push("/login"); }}
            className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm text-gray-600 hover:bg-red-50 hover:text-red-600 transition-all w-full"
          >
            <LogOut size={16} />
            Sign Out
          </button>
        </div>
      </aside>

      {/* Main content area */}
      <main className="flex-1 overflow-auto">
        {children}
      </main>
    </div>
  );
}
