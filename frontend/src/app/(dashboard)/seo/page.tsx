"use client";
import { useState } from "react";
import useSWR from "swr";
import { seoApi } from "@/lib/api";
import { Plus, Search } from "lucide-react";

const fetcher = () => seoApi.keywords().then((r) => r.data);

export default function SEOPage() {
  const { data: keywords = [], mutate, isLoading } = useSWR("seo-keywords", fetcher);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ keyword: "", search_volume: "", difficulty: "", target_rank: "" });

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    await seoApi.addKeyword({
      keyword: form.keyword,
      search_volume: form.search_volume ? parseInt(form.search_volume) : undefined,
      difficulty: form.difficulty ? parseFloat(form.difficulty) : undefined,
      target_rank: form.target_rank ? parseInt(form.target_rank) : undefined,
    });
    await mutate();
    setShowForm(false);
    setForm({ keyword: "", search_volume: "", difficulty: "", target_rank: "" });
  };

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">SEO Keywords</h1>
          <p className="text-gray-500 text-sm mt-1">Track keywords and optimize your content rankings</p>
        </div>
        <button
          onClick={() => setShowForm(true)}
          className="bg-indigo-600 text-white px-4 py-2.5 rounded-lg text-sm font-semibold flex items-center gap-2"
        >
          <Plus size={16} /> Track Keyword
        </button>
      </div>

      {isLoading ? (
        <div className="text-gray-400 text-sm">Loading...</div>
      ) : keywords.length === 0 ? (
        <div className="bg-white rounded-xl border border-dashed border-gray-200 py-16 text-center">
          <Search size={40} className="text-gray-300 mx-auto mb-3" />
          <p className="text-gray-500 font-medium">No keywords tracked yet</p>
          <p className="text-gray-400 text-sm">Add keywords to monitor and optimize your content for</p>
        </div>
      ) : (
        <div className="bg-white rounded-xl border border-gray-100 overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-100 bg-gray-50">
                <th className="text-left px-4 py-3 text-gray-500 font-medium">Keyword</th>
                <th className="text-left px-4 py-3 text-gray-500 font-medium">Volume</th>
                <th className="text-left px-4 py-3 text-gray-500 font-medium">Difficulty</th>
                <th className="text-left px-4 py-3 text-gray-500 font-medium">Current Rank</th>
                <th className="text-left px-4 py-3 text-gray-500 font-medium">Target Rank</th>
              </tr>
            </thead>
            <tbody>
              {keywords.map((kw: any) => (
                <tr key={kw.id} className="border-b border-gray-50 hover:bg-gray-50">
                  <td className="px-4 py-3 font-medium text-gray-900">{kw.keyword}</td>
                  <td className="px-4 py-3 text-gray-500">{kw.search_volume?.toLocaleString() ?? "—"}</td>
                  <td className="px-4 py-3">
                    {kw.difficulty != null ? (
                      <span className={`text-xs font-medium px-2 py-0.5 rounded ${kw.difficulty <= 30 ? "bg-green-50 text-green-600" : kw.difficulty <= 60 ? "bg-yellow-50 text-yellow-600" : "bg-red-50 text-red-600"}`}>
                        {kw.difficulty}
                      </span>
                    ) : "—"}
                  </td>
                  <td className="px-4 py-3 text-gray-500">{kw.current_rank ?? "—"}</td>
                  <td className="px-4 py-3 text-gray-500">{kw.target_rank ?? "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {showForm && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl p-6 w-full max-w-md shadow-2xl">
            <h2 className="text-lg font-bold text-gray-900 mb-4">Track Keyword</h2>
            <form onSubmit={handleAdd} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Keyword *</label>
                <input className="input-field" required value={form.keyword} onChange={(e) => setForm({ ...form, keyword: e.target.value })} placeholder="e.g. email marketing automation" />
              </div>
              <div className="grid grid-cols-3 gap-3">
                <div>
                  <label className="block text-xs text-gray-500 mb-1">Volume</label>
                  <input type="number" className="input-field" value={form.search_volume} onChange={(e) => setForm({ ...form, search_volume: e.target.value })} placeholder="1000" />
                </div>
                <div>
                  <label className="block text-xs text-gray-500 mb-1">Difficulty (0-100)</label>
                  <input type="number" className="input-field" value={form.difficulty} onChange={(e) => setForm({ ...form, difficulty: e.target.value })} placeholder="45" />
                </div>
                <div>
                  <label className="block text-xs text-gray-500 mb-1">Target Rank</label>
                  <input type="number" className="input-field" value={form.target_rank} onChange={(e) => setForm({ ...form, target_rank: e.target.value })} placeholder="5" />
                </div>
              </div>
              <div className="flex gap-3 pt-2">
                <button type="button" onClick={() => setShowForm(false)} className="flex-1 border border-gray-200 py-2.5 rounded-lg text-sm text-gray-600">Cancel</button>
                <button type="submit" className="flex-1 bg-indigo-600 text-white py-2.5 rounded-lg text-sm font-semibold">Add Keyword</button>
              </div>
            </form>
          </div>
        </div>
      )}

      <style jsx>{`
        .input-field { width: 100%; border: 1px solid #e5e7eb; border-radius: 8px; padding: 8px 12px; font-size: 14px; outline: none; }
        .input-field:focus { border-color: #6366f1; }
      `}</style>
    </div>
  );
}
