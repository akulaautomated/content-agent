"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import useSWR from "swr";
import { contentApi, brandsApi } from "@/lib/api";
import { Sparkles, ArrowLeft, Loader2 } from "lucide-react";

const CONTENT_TYPES = [
  { value: "blog_post", label: "Blog Post", desc: "SEO-optimized, 1500-2500 words", emoji: "📝" },
  { value: "email", label: "Email Campaign", desc: "Newsletter, nurture, promotional", emoji: "📧" },
  { value: "social_post", label: "Social Media", desc: "LinkedIn, X, Instagram, Facebook", emoji: "📱" },
  { value: "ad_copy", label: "Ad Copy", desc: "Google, Meta, LinkedIn ads", emoji: "🎯" },
  { value: "landing_page", label: "Landing Page", desc: "Conversion-optimized copy", emoji: "🏠" },
  { value: "case_study", label: "Case Study", desc: "Challenge/Solution/Results", emoji: "📊" },
];

const PLATFORMS: Record<string, string[]> = {
  social_post: ["linkedin", "twitter_x", "instagram", "facebook"],
  ad_copy: ["google_ads", "meta_ads", "linkedin_ads"],
  email: ["email"],
  blog_post: ["blog"],
  landing_page: ["website"],
  case_study: ["website"],
};

const TONES = ["conversational", "technical", "formal", "casual", "persuasive", "educational"];

export default function NewContentPage() {
  const router = useRouter();
  const { data: brands = [] } = useSWR("brands", () => brandsApi.list().then((r) => r.data));
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [form, setForm] = useState({
    content_type: "",
    platform: "",
    brief: "",
    tone: "conversational",
    target_audience: "",
    keywords: "",
    brand_id: "",
    word_count_target: "",
  });

  const platforms = PLATFORMS[form.content_type] || [];

  const handleGenerate = async () => {
    setLoading(true);
    setError("");
    try {
      const payload = {
        content_type: form.content_type,
        platform: form.platform || undefined,
        brief: form.brief,
        tone: form.tone,
        target_audience: form.target_audience || undefined,
        keywords: form.keywords ? form.keywords.split(",").map((k) => k.trim()).filter(Boolean) : [],
        brand_id: form.brand_id || undefined,
        word_count_target: form.word_count_target ? parseInt(form.word_count_target) : undefined,
      };
      const res = await contentApi.generate(payload);
      router.push(`/content/${res.data.id}`);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Generation failed. Please try again.");
      setLoading(false);
    }
  };

  return (
    <div className="p-8 max-w-3xl">
      <button
        onClick={() => router.push("/content")}
        className="flex items-center gap-2 text-gray-500 hover:text-gray-700 text-sm mb-6"
      >
        <ArrowLeft size={16} /> Back to Content
      </button>

      <h1 className="text-2xl font-bold text-gray-900 mb-1">Generate Content</h1>
      <p className="text-gray-500 text-sm mb-8">
        Tell the AI what you need and it will write it for you.
      </p>

      {/* Step indicator */}
      <div className="flex items-center gap-2 mb-8">
        {[1, 2, 3].map((s) => (
          <div key={s} className="flex items-center gap-2">
            <div className={`w-7 h-7 rounded-full flex items-center justify-center text-sm font-semibold transition-colors ${
              step >= s ? "bg-indigo-600 text-white" : "bg-gray-100 text-gray-400"
            }`}>{s}</div>
            {s < 3 && <div className={`h-0.5 w-12 ${step > s ? "bg-indigo-600" : "bg-gray-200"}`} />}
          </div>
        ))}
        <span className="text-sm text-gray-500 ml-2">
          {step === 1 ? "Choose type" : step === 2 ? "Write brief" : "Generate"}
        </span>
      </div>

      {/* Step 1: Choose content type */}
      {step === 1 && (
        <div>
          <h2 className="font-semibold text-gray-700 mb-4">What type of content do you need?</h2>
          <div className="grid grid-cols-2 gap-3">
            {CONTENT_TYPES.map((ct) => (
              <button
                key={ct.value}
                onClick={() => { setForm({ ...form, content_type: ct.value, platform: "" }); setStep(2); }}
                className={`p-4 rounded-xl border-2 text-left transition-all hover:border-indigo-400 ${
                  form.content_type === ct.value
                    ? "border-indigo-600 bg-indigo-50"
                    : "border-gray-200 bg-white"
                }`}
              >
                <div className="text-2xl mb-2">{ct.emoji}</div>
                <div className="font-semibold text-gray-900 text-sm">{ct.label}</div>
                <div className="text-xs text-gray-500 mt-0.5">{ct.desc}</div>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Step 2: Brief + settings */}
      {step === 2 && (
        <div className="space-y-5">
          <h2 className="font-semibold text-gray-700">Tell the AI what to write</h2>

          {platforms.length > 1 && (
            <div>
              <label className="label">Platform (optional)</label>
              <select
                className="input-field"
                value={form.platform}
                onChange={(e) => setForm({ ...form, platform: e.target.value })}
              >
                <option value="">All platforms</option>
                {platforms.map((p) => <option key={p} value={p}>{p.replace("_", " ")}</option>)}
              </select>
            </div>
          )}

          <div>
            <label className="label">Brief *</label>
            <textarea
              className="input-field min-h-[120px] resize-none"
              placeholder={`Example: Write a blog post about the top 5 email marketing strategies for SaaS companies in 2025. Target audience: SaaS founders and marketers. Include actionable tips.`}
              value={form.brief}
              onChange={(e) => setForm({ ...form, brief: e.target.value })}
              rows={5}
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="label">Tone</label>
              <select
                className="input-field"
                value={form.tone}
                onChange={(e) => setForm({ ...form, tone: e.target.value })}
              >
                {TONES.map((t) => <option key={t} value={t}>{t.charAt(0).toUpperCase() + t.slice(1)}</option>)}
              </select>
            </div>
            {brands.length > 0 && (
              <div>
                <label className="label">Brand Voice</label>
                <select
                  className="input-field"
                  value={form.brand_id}
                  onChange={(e) => setForm({ ...form, brand_id: e.target.value })}
                >
                  <option value="">Default</option>
                  {brands.map((b: any) => <option key={b.id} value={b.id}>{b.name}</option>)}
                </select>
              </div>
            )}
          </div>

          <div>
            <label className="label">Target Audience</label>
            <input
              className="input-field"
              placeholder="e.g. SaaS founders, e-commerce marketing managers"
              value={form.target_audience}
              onChange={(e) => setForm({ ...form, target_audience: e.target.value })}
            />
          </div>

          <div>
            <label className="label">Keywords (comma-separated)</label>
            <input
              className="input-field"
              placeholder="email marketing, email automation, email sequences"
              value={form.keywords}
              onChange={(e) => setForm({ ...form, keywords: e.target.value })}
            />
          </div>

          <div className="flex gap-3 pt-2">
            <button onClick={() => setStep(1)} className="btn-secondary">Back</button>
            <button
              onClick={() => form.brief.trim() && setStep(3)}
              disabled={!form.brief.trim()}
              className="btn-primary"
            >
              Continue
            </button>
          </div>
        </div>
      )}

      {/* Step 3: Review + Generate */}
      {step === 3 && (
        <div className="space-y-5">
          <h2 className="font-semibold text-gray-700">Ready to generate</h2>

          <div className="bg-gray-50 rounded-xl p-5 space-y-3 text-sm">
            <Row label="Type" value={CONTENT_TYPES.find((c) => c.value === form.content_type)?.label || form.content_type} />
            {form.platform && <Row label="Platform" value={form.platform} />}
            <Row label="Tone" value={form.tone} />
            {form.target_audience && <Row label="Audience" value={form.target_audience} />}
            {form.keywords && <Row label="Keywords" value={form.keywords} />}
            <div className="pt-1">
              <div className="text-gray-400 mb-1">Brief</div>
              <div className="text-gray-700">{form.brief}</div>
            </div>
          </div>

          {error && (
            <div className="bg-red-50 text-red-600 text-sm px-4 py-3 rounded-lg">{error}</div>
          )}

          <div className="flex gap-3">
            <button onClick={() => setStep(2)} className="btn-secondary" disabled={loading}>Back</button>
            <button
              onClick={handleGenerate}
              disabled={loading}
              className="btn-primary flex items-center gap-2 flex-1 justify-center"
            >
              {loading ? (
                <>
                  <Loader2 size={16} className="animate-spin" />
                  AI is writing... (this may take 30-60 seconds)
                </>
              ) : (
                <>
                  <Sparkles size={16} />
                  Generate with AI
                </>
              )}
            </button>
          </div>
        </div>
      )}

      <style jsx>{`
        .label { display: block; font-size: 13px; font-weight: 500; color: #374151; margin-bottom: 5px; }
        .input-field { width: 100%; border: 1px solid #e5e7eb; border-radius: 8px; padding: 9px 13px; font-size: 14px; outline: none; background: white; }
        .input-field:focus { border-color: #6366f1; box-shadow: 0 0 0 3px rgba(99,102,241,0.1); }
        .btn-primary { background: #4f46e5; color: white; padding: 10px 20px; border-radius: 8px; font-size: 14px; font-weight: 600; cursor: pointer; }
        .btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }
        .btn-secondary { border: 1px solid #e5e7eb; background: white; color: #374151; padding: 10px 20px; border-radius: 8px; font-size: 14px; font-weight: 500; cursor: pointer; }
      `}</style>
    </div>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex gap-4">
      <span className="text-gray-400 w-20 shrink-0">{label}</span>
      <span className="text-gray-700 font-medium">{value}</span>
    </div>
  );
}
