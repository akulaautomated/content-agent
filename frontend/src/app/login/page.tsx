"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { authApi } from "@/lib/api";
import { useAuthStore } from "@/store/authStore";

export default function LoginPage() {
  const router = useRouter();
  const login = useAuthStore((s) => s.login);
  const [mode, setMode] = useState<"login" | "register">("login");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [form, setForm] = useState({
    org_name: "",
    email: "",
    password: "",
    full_name: "",
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      let res;
      if (mode === "login") {
        res = await authApi.login(form.email, form.password);
      } else {
        res = await authApi.register(form);
      }
      login(res.data.access_token, res.data.user_id, res.data.org_id);
      router.push("/dashboard");
    } catch (err: any) {
      setError(err.response?.data?.detail || "Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="bg-white rounded-2xl shadow-xl p-8 w-full max-w-md">
        <div className="text-center mb-8">
          <div className="text-3xl font-bold text-indigo-600 mb-1">✦ ContentAgent</div>
          <p className="text-gray-500 text-sm">AI-powered content for marketing agencies</p>
        </div>

        <div className="flex rounded-lg bg-gray-100 p-1 mb-6">
          {(["login", "register"] as const).map((m) => (
            <button
              key={m}
              onClick={() => setMode(m)}
              className={`flex-1 py-2 text-sm font-medium rounded-md transition-all ${
                mode === m ? "bg-white shadow text-indigo-600" : "text-gray-500"
              }`}
            >
              {m === "login" ? "Sign In" : "Create Account"}
            </button>
          ))}
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {mode === "register" && (
            <>
              <input
                type="text"
                placeholder="Agency / Organization Name"
                required
                className="input-field"
                value={form.org_name}
                onChange={(e) => setForm({ ...form, org_name: e.target.value })}
              />
              <input
                type="text"
                placeholder="Your Full Name"
                className="input-field"
                value={form.full_name}
                onChange={(e) => setForm({ ...form, full_name: e.target.value })}
              />
            </>
          )}
          <input
            type="email"
            placeholder="Email address"
            required
            className="input-field"
            value={form.email}
            onChange={(e) => setForm({ ...form, email: e.target.value })}
          />
          <input
            type="password"
            placeholder="Password"
            required
            className="input-field"
            value={form.password}
            onChange={(e) => setForm({ ...form, password: e.target.value })}
          />

          {error && (
            <div className="bg-red-50 text-red-600 text-sm px-4 py-2 rounded-lg">{error}</div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-indigo-600 hover:bg-indigo-700 text-white py-3 rounded-lg font-semibold transition-colors disabled:opacity-50"
          >
            {loading ? "Please wait..." : mode === "login" ? "Sign In" : "Create Account"}
          </button>
        </form>
      </div>

      <style jsx>{`
        .input-field {
          width: 100%;
          border: 1px solid #e5e7eb;
          border-radius: 8px;
          padding: 10px 14px;
          font-size: 14px;
          outline: none;
          transition: border-color 0.2s;
        }
        .input-field:focus {
          border-color: #6366f1;
          box-shadow: 0 0 0 3px rgba(99,102,241,0.1);
        }
      `}</style>
    </div>
  );
}
