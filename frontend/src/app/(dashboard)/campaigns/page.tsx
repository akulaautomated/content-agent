"use client";
import { useState } from "react";
import useSWR from "swr";
import { campaignsApi } from "@/lib/api";
import { Plus, Target } from "lucide-react";
import Link from "next/link";

const fetcher = () => campaignsApi.list().then((r) => r.data);

export default function CampaignsPage() {
  const { data: campaigns = [], mutate, isLoading } = useSWR("campaigns", fetcher);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ name: "", description: "" });

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    await campaignsApi.create(form);
    await mutate();
    setShowForm(false);
    setForm({ name: "", description: "" });
  };

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Campaigns</h1>
          <p className="text-gray-500 text-sm mt-1">Group related content together</p>
        </div>
        <button onClick={() => setShowForm(true)} className="bg-indigo-600 text-white px-4 py-2.5 rounded-lg text-sm font-semibold flex items-center gap-2">
          <Plus size={16} /> New Campaign
        </button>
      </div>

      {isLoading ? <div className="text-gray-400 text-sm">Loading...</div> : campaigns.length === 0 ? (
        <div className="bg-white rounded-xl border border-dashed border-gray-200 py-16 text-center">
          <Target size={40} className="text-gray-300 mx-auto mb-3" />
          <p className="text-gray-500 font-medium">No campaigns yet</p>
        </div>
      ) : (
        <div className="grid grid-cols-3 gap-4">
          {campaigns.map((c: any) => (
            <div key={c.id} className="bg-white rounded-xl p-5 border border-gray-100 hover:border-indigo-200 transition-colors">
              <div className="flex items-center gap-2 mb-2">
                <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${c.status === "active" ? "bg-green-50 text-green-600" : "bg-gray-100 text-gray-500"}`}>
                  {c.status}
                </span>
              </div>
              <h3 className="font-semibold text-gray-900 mb-1">{c.name}</h3>
              {c.description && <p className="text-sm text-gray-500 text-xs">{c.description}</p>}
            </div>
          ))}
        </div>
      )}

      {showForm && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl p-6 w-full max-w-md shadow-2xl">
            <h2 className="text-lg font-bold mb-4">New Campaign</h2>
            <form onSubmit={handleCreate} className="space-y-4">
              <input className="input-field" required placeholder="Campaign name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
              <input className="input-field" placeholder="Description (optional)" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
              <div className="flex gap-3 pt-2">
                <button type="button" onClick={() => setShowForm(false)} className="flex-1 border border-gray-200 py-2.5 rounded-lg text-sm">Cancel</button>
                <button type="submit" className="flex-1 bg-indigo-600 text-white py-2.5 rounded-lg text-sm font-semibold">Create</button>
              </div>
            </form>
          </div>
        </div>
      )}
      <style jsx>{`
        .input-field { width: 100%; border: 1px solid #e5e7eb; border-radius: 8px; padding: 9px 13px; font-size: 14px; outline: none; }
      `}</style>
    </div>
  );
}
