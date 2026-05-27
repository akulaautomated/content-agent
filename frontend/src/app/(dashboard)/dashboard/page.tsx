"use client";
import useSWR from "swr";
import { analyticsApi } from "@/lib/api";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import Link from "next/link";
import { FileText, CalendarDays, TrendingUp, Sparkles } from "lucide-react";

const fetcher = () => analyticsApi.dashboard().then((r) => r.data);

export default function DashboardPage() {
  const { data, isLoading } = useSWR("dashboard", fetcher, { refreshInterval: 30000 });

  const chartData = data
    ? Object.entries(data.content_by_type || {}).map(([type, count]) => ({
        name: type.replace("_", " "),
        count,
      }))
    : [];

  const statusData = data
    ? Object.entries(data.content_by_status || {}).map(([status, count]) => ({
        name: status,
        count,
      }))
    : [];

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-500 text-sm mt-1">Your content performance at a glance</p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-4 gap-4 mb-8">
        <StatCard
          label="Total Content"
          value={isLoading ? "—" : data?.total_content ?? 0}
          icon={<FileText size={20} className="text-indigo-500" />}
          color="indigo"
        />
        <StatCard
          label="Published This Month"
          value={isLoading ? "—" : data?.published_this_month ?? 0}
          icon={<TrendingUp size={20} className="text-green-500" />}
          color="green"
        />
        <StatCard
          label="Scheduled"
          value={isLoading ? "—" : data?.scheduled_upcoming ?? 0}
          icon={<CalendarDays size={20} className="text-orange-500" />}
          color="orange"
        />
        <StatCard
          label="Avg. Engagement"
          value={isLoading ? "—" : `${data?.avg_engagement_rate ?? 0}%`}
          icon={<Sparkles size={20} className="text-purple-500" />}
          color="purple"
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-2 gap-6 mb-8">
        <div className="bg-white rounded-xl p-6 border border-gray-100">
          <h3 className="font-semibold text-gray-700 mb-4">Content by Type</h3>
          {chartData.length > 0 ? (
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip />
                <Bar dataKey="count" fill="#6366f1" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <EmptyChart />
          )}
        </div>

        <div className="bg-white rounded-xl p-6 border border-gray-100">
          <h3 className="font-semibold text-gray-700 mb-4">Content by Status</h3>
          {statusData.length > 0 ? (
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={statusData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip />
                <Bar dataKey="count" fill="#10b981" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <EmptyChart />
          )}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-xl p-6 border border-gray-100">
        <h3 className="font-semibold text-gray-700 mb-4">Quick Actions</h3>
        <div className="flex gap-3">
          <Link
            href="/content/new"
            className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2.5 rounded-lg text-sm font-medium transition-colors flex items-center gap-2"
          >
            <Sparkles size={16} />
            Generate Content
          </Link>
          <Link
            href="/calendar"
            className="bg-white border border-gray-200 hover:border-indigo-300 text-gray-700 px-4 py-2.5 rounded-lg text-sm font-medium transition-colors"
          >
            View Calendar
          </Link>
          <Link
            href="/brands"
            className="bg-white border border-gray-200 hover:border-indigo-300 text-gray-700 px-4 py-2.5 rounded-lg text-sm font-medium transition-colors"
          >
            Manage Brand Voices
          </Link>
        </div>
      </div>
    </div>
  );
}

function StatCard({ label, value, icon, color }: any) {
  const bg: Record<string, string> = {
    indigo: "bg-indigo-50",
    green: "bg-green-50",
    orange: "bg-orange-50",
    purple: "bg-purple-50",
  };
  return (
    <div className="bg-white rounded-xl p-5 border border-gray-100">
      <div className={`inline-flex p-2 rounded-lg ${bg[color]} mb-3`}>{icon}</div>
      <div className="text-2xl font-bold text-gray-900">{value}</div>
      <div className="text-sm text-gray-500 mt-0.5">{label}</div>
    </div>
  );
}

function EmptyChart() {
  return (
    <div className="h-[200px] flex items-center justify-center text-gray-400 text-sm">
      No data yet — generate some content to see stats
    </div>
  );
}
