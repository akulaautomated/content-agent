"use client";
import useSWR from "swr";
import { analyticsApi } from "@/lib/api";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line } from "recharts";

export default function AnalyticsPage() {
  const { data, isLoading } = useSWR("analytics-dashboard", () =>
    analyticsApi.dashboard().then((r) => r.data)
  );

  const typeData = data
    ? Object.entries(data.content_by_type || {}).map(([k, v]) => ({ name: k.replace("_", " "), count: v }))
    : [];

  return (
    <div className="p-8">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Analytics</h1>
        <p className="text-gray-500 text-sm mt-1">Track your content performance across all channels</p>
      </div>

      {isLoading ? (
        <div className="text-gray-400 text-sm">Loading...</div>
      ) : (
        <>
          {/* KPI row */}
          <div className="grid grid-cols-4 gap-4 mb-8">
            {[
              { label: "Total Content", value: data?.total_content ?? 0 },
              { label: "Published This Month", value: data?.published_this_month ?? 0 },
              { label: "Scheduled", value: data?.scheduled_upcoming ?? 0 },
              { label: "Avg Engagement", value: `${data?.avg_engagement_rate ?? 0}%` },
            ].map(({ label, value }) => (
              <div key={label} className="bg-white rounded-xl p-5 border border-gray-100">
                <div className="text-2xl font-bold text-gray-900">{value}</div>
                <div className="text-sm text-gray-500 mt-1">{label}</div>
              </div>
            ))}
          </div>

          <div className="grid grid-cols-2 gap-6">
            <div className="bg-white rounded-xl p-6 border border-gray-100">
              <h3 className="font-semibold text-gray-700 mb-4">Content by Type</h3>
              {typeData.length > 0 ? (
                <ResponsiveContainer width="100%" height={220}>
                  <BarChart data={typeData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                    <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                    <YAxis tick={{ fontSize: 11 }} />
                    <Tooltip />
                    <Bar dataKey="count" fill="#6366f1" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <div className="h-[220px] flex items-center justify-center text-gray-300 text-sm">
                  Generate content to see analytics
                </div>
              )}
            </div>

            <div className="bg-white rounded-xl p-6 border border-gray-100">
              <h3 className="font-semibold text-gray-700 mb-4">Monthly Performance Report</h3>
              <div className="space-y-3 text-sm text-gray-600">
                <p>Connect your social media and email platforms to see live performance data here.</p>
                <p className="text-gray-400">Supported integrations coming soon: Google Analytics, Mailchimp, HubSpot, Buffer, Hootsuite</p>
                <div className="bg-indigo-50 rounded-lg p-4 mt-4">
                  <p className="text-indigo-700 font-medium text-sm">Generate AI Report</p>
                  <p className="text-indigo-600 text-xs mt-1">Use the Analytics Agent to generate a performance summary based on your content data.</p>
                </div>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
