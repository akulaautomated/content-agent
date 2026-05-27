"use client";
import { useState } from "react";
import useSWR from "swr";
import { brandsApi } from "@/lib/api";
import { Plus, Palette } from "lucide-react";

const fetcher = () => brandsApi.list().then((r) => r.data);

const TONES = ["conversational", "technical", "formal", "casual", "persuasive", "educational"];

export default function BrandsPage() {
  const { data: brands = [], mutate, isLoading } = useSWR("brands", fetcher);
  const [showForm, setShowForm] = useState(false);
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState({
    name: "",
    description: "",
    tone: "conversational",
    preferred_terms: "",
    banned_terms: "",
    is_default: false,
  });

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    await brandsApi.create({
      name: form.name,
      description: form.description,
      tone: form.tone,
      vocabulary: {
        preferred: form.preferred_terms.split(",").map((t) => t.trim()).filter(Boolean),
        banned: form.banned_terms.split(",").map((t) => t.trim()).filter(Boolean),
      },
      is_default: form.is_default,
    });
    await mutate();
    setShowForm(false);
    setSaving(false);
    setForm({ name: "", description: "", tone: "conversational", preferred_terms: "", banned_terms: "", is_default: false });
  };

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Brand Voices</h1>
          <p className="text-gray-500 text-sm mt-1">Define how your content should sound for each client</p>
        </div>
        <button
          onClick={() => setShowForm(true)}
          className="bg-indigo-600 text-white px-4 py-2.5 rounded-lg text-sm font-semibold flex items-center gap-2"
        >
          <Plus size={16} /> Add Brand Voice
        </button>
      </div>

      {isLoading ? (
        <div className="text-gray-400 text-sm">Loading...</div>
      ) : brands.length === 0 && !showForm ? (
        <div className="bg-white rounded-xl border border-dashed border-gray-200 py-16 text-center">
          <Palette size={40} className="text-gray-300 mx-auto mb-3" />
          <p className="text-gray-500 font-medium">No brand profiles yet</p>
          <p className="text-gray-400 text-sm mt-1">Create your first brand voice to guide AI content generation</p>
          <button
            onClick={() => setShowForm(true)}
            className="mt-4 bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-medium"
          >
            Create Brand Voice
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-3 gap-4">
          {brands.map((brand: any) => (
            <div key={brand.id} className="bg-white rounded-xl p-5 border border-gray-100">
              <div className="flex items-start justify-between mb-3">
                <div>
                  <h3 className="font-semibold text-gray-900">{brand.name}</h3>
                  {brand.is_default && (
                    <span className="text-xs bg-indigo-50 text-indigo-600 px-2 py-0.5 rounded font-medium mt-1 inline-block">Default</span>
                  )}
                </div>
                <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded capitalize">{brand.tone}</span>
              </div>
              {brand.description && <p className="text-sm text-gray-500 mb-3">{brand.description}</p>}
              {brand.vocabulary?.preferred?.length > 0 && (
                <div className="mb-2">
                  <div className="text-xs text-gray-400 mb-1">Preferred terms</div>
                  <div className="flex flex-wrap gap-1">
                    {brand.vocabulary.preferred.slice(0, 5).map((t: string) => (
                      <span key={t} className="text-xs bg-green-50 text-green-700 px-1.5 py-0.5 rounded">{t}</span>
                    ))}
                  </div>
                </div>
              )}
              {brand.vocabulary?.banned?.length > 0 && (
                <div>
                  <div className="text-xs text-gray-400 mb-1">Banned terms</div>
                  <div className="flex flex-wrap gap-1">
                    {brand.vocabulary.banned.slice(0, 5).map((t: string) => (
                      <span key={t} className="text-xs bg-red-50 text-red-600 px-1.5 py-0.5 rounded">{t}</span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Create form */}
      {showForm && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl p-6 w-full max-w-lg shadow-2xl">
            <h2 className="text-lg font-bold text-gray-900 mb-4">Create Brand Voice</h2>
            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Brand Name *</label>
                <input className="input-field" required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="e.g. Acme Corp" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                <input className="input-field" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} placeholder="Brief description of this brand" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Tone</label>
                <select className="input-field" value={form.tone} onChange={(e) => setForm({ ...form, tone: e.target.value })}>
                  {TONES.map((t) => <option key={t} value={t}>{t.charAt(0).toUpperCase() + t.slice(1)}</option>)}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Preferred Terms (comma-separated)</label>
                <input className="input-field" value={form.preferred_terms} onChange={(e) => setForm({ ...form, preferred_terms: e.target.value })} placeholder="scalable, data-driven, results-focused" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Banned Terms (comma-separated)</label>
                <input className="input-field" value={form.banned_terms} onChange={(e) => setForm({ ...form, banned_terms: e.target.value })} placeholder="synergy, paradigm shift, utilize" />
              </div>
              <div className="flex items-center gap-2">
                <input type="checkbox" id="is_default" checked={form.is_default} onChange={(e) => setForm({ ...form, is_default: e.target.checked })} />
                <label htmlFor="is_default" className="text-sm text-gray-700">Set as default brand voice</label>
              </div>
              <div className="flex gap-3 pt-2">
                <button type="button" onClick={() => setShowForm(false)} className="flex-1 border border-gray-200 py-2.5 rounded-lg text-sm font-medium text-gray-600">Cancel</button>
                <button type="submit" disabled={saving} className="flex-1 bg-indigo-600 text-white py-2.5 rounded-lg text-sm font-semibold disabled:opacity-50">
                  {saving ? "Creating..." : "Create Brand Voice"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      <style jsx>{`
        .input-field { width: 100%; border: 1px solid #e5e7eb; border-radius: 8px; padding: 9px 13px; font-size: 14px; outline: none; }
        .input-field:focus { border-color: #6366f1; }
      `}</style>
    </div>
  );
}
