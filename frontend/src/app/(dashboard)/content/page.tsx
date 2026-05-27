"use client";
import useSWR from "swr";
import Link from "next/link";
import { contentApi } from "@/lib/api";
import { STATUS_COLORS, CONTENT_TYPE_COLORS, CONTENT_TYPE_LABELS, formatDate } from "@/lib/utils";
import { Plus, FileText } from "lucide-react";
import { useState } from "react";

const fetcher = (params: Record<string, string>) =>
  contentApi.list(params).then((r) => r.data);

const CONTENT_TYPES = ["blog_post", "email", "social_post", "ad_copy", "landing_page", "case_study"];
const STATUSES = ["idea", "draft", "review", "approved", "scheduled", "published", "archived"];

export default function ContentPage() {
  const [filters, setFilters] = useState<Record<string, string>>({});
  const { data: items = [], isLoading } = useSWR(
    ["content", filters],
    () => fetcher(filters),
    { revalidateOnFocus: false }
  );

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Content</h1>
          <p className="text-gray-500 text-sm mt-1">{items.length} items</p>
        </div>
        <Link
          href="/content/new"
          className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2.5 rounded-lg text-sm font-semibold flex items-center gap-2"
        >
          <Plus size={16} />
          Generate Content
        </Link>
      </div>

      {/* Filters */}
      <div className="flex gap-3 mb-5">
        <select
          className="filter-select"
          value={filters.content_type || ""}
          onChange={(e) => setFilters({ ...filters, content_type: e.target.value || "" })}
        >
          <option value="">All Types</option>
          {CONTENT_TYPES.map((t) => (
            <option key={t} value={t}>{CONTENT_TYPE_LABELS[t]}</option>
          ))}
        </select>
        <select
          className="filter-select"
          value={filters.status || ""}
          onChange={(e) => setFilters({ ...filters, status: e.target.value || "" })}
        >
          <option value="">All Statuses</option>
          {STATUSES.map((s) => (
            <option key={s} value={s}>{s.charAt(0).toUpperCase() + s.slice(1)}</option>
          ))}
        </select>
        {Object.keys(filters).some(Boolean) && (
          <button
            onClick={() => setFilters({})}
            className="text-sm text-indigo-600 hover:underline px-2"
          >
            Clear filters
          </button>
        )}
      </div>

      {/* Content table */}
      {isLoading ? (
        <div className="text-gray-400 text-sm py-12 text-center">Loading...</div>
      ) : items.length === 0 ? (
        <div className="bg-white rounded-xl border border-dashed border-gray-200 py-16 text-center">
          <FileText size={40} className="text-gray-300 mx-auto mb-3" />
          <p className="text-gray-500 font-medium">No content yet</p>
          <p className="text-gray-400 text-sm mt-1">Generate your first piece of content with AI</p>
          <Link
            href="/content/new"
            className="mt-4 inline-flex items-center gap-2 bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-medium"
          >
            <Plus size={14} /> Generate Content
          </Link>
        </div>
      ) : (
        <div className="bg-white rounded-xl border border-gray-100 overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-100 bg-gray-50">
                <th className="text-left px-4 py-3 text-gray-500 font-medium">Title</th>
                <th className="text-left px-4 py-3 text-gray-500 font-medium">Type</th>
                <th className="text-left px-4 py-3 text-gray-500 font-medium">Status</th>
                <th className="text-left px-4 py-3 text-gray-500 font-medium">Words</th>
                <th className="text-left px-4 py-3 text-gray-500 font-medium">Updated</th>
              </tr>
            </thead>
            <tbody>
              {items.map((item: any) => (
                <tr key={item.id} className="border-b border-gray-50 hover:bg-gray-50 transition-colors">
                  <td className="px-4 py-3">
                    <Link href={`/content/${item.id}`} className="font-medium text-gray-900 hover:text-indigo-600">
                      {item.title || "(Untitled)"}
                    </Link>
                    {item.platform && (
                      <span className="ml-2 text-xs text-gray-400">{item.platform}</span>
                    )}
                  </td>
                  <td className="px-4 py-3">
                    <span className={`text-xs px-2 py-1 rounded-full font-medium ${CONTENT_TYPE_COLORS[item.content_type] || "bg-gray-100 text-gray-600"}`}>
                      {CONTENT_TYPE_LABELS[item.content_type] || item.content_type}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`text-xs px-2 py-1 rounded-full font-medium ${STATUS_COLORS[item.status] || "bg-gray-100"}`}>
                      {item.status}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-gray-500">{item.word_count || "—"}</td>
                  <td className="px-4 py-3 text-gray-400">{formatDate(item.updated_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <style jsx>{`
        .filter-select {
          border: 1px solid #e5e7eb;
          border-radius: 8px;
          padding: 6px 12px;
          font-size: 13px;
          color: #374151;
          background: white;
          outline: none;
        }
        .filter-select:focus {
          border-color: #6366f1;
        }
      `}</style>
    </div>
  );
}
