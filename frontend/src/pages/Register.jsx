import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";

export default function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      await register(fullName, email, password);
      navigate("/dashboard");
    } catch (err) {
      setError(err?.response?.data?.detail || "Couldn't create your account.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-paper to-white flex items-center justify-center px-6 py-12">
      <div className="w-full max-w-md animate-slide-up">
        <div className="card-soft p-8 sm:p-10">
          <div className="mb-8 text-center">
            <div className="inline-block mb-4 bg-gradient-to-br from-route to-route/80 text-white px-4 py-2 rounded-lg font-display font-bold">
              CB
            </div>
            <h1 className="font-display text-3xl mb-3 text-ink">Start your route</h1>
            <p className="text-ink/60">A minute of setup, then straight to your assessment.</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            <div className="space-y-2">
              <label className="block text-sm font-semibold text-ink" htmlFor="fullName">
                Full name
              </label>
              <input
                id="fullName"
                type="text"
                required
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                className="input-lg"
                placeholder="John Doe"
              />
            </div>

            <div className="space-y-2">
              <label className="block text-sm font-semibold text-ink" htmlFor="email">
                Email address
              </label>
              <input
                id="email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="input-lg"
                placeholder="you@example.com"
              />
            </div>

            <div className="space-y-2">
              <label className="block text-sm font-semibold text-ink" htmlFor="password">
                Password
              </label>
              <input
                id="password"
                type="password"
                required
                minLength={8}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="input-lg"
                placeholder="••••••••"
              />
              <p className="text-xs text-ink/50 font-medium">At least 8 characters.</p>
            </div>

            {error && (
              <div className="p-4 rounded-lg bg-red-50 border border-red-200">
                <p className="text-sm text-red-700 font-medium">{error}</p>
              </div>
            )}

            <button
              type="submit"
              disabled={submitting}
              className="btn-primary w-full py-3 text-base font-semibold shadow-md hover:shadow-lg"
            >
              {submitting ? (
                <span className="flex items-center gap-2">
                  <span className="animate-spin">⏳</span> Creating account...
                </span>
              ) : (
                "Create account"
              )}
            </button>
          </form>

          <div className="mt-6 pt-6 border-t border-slate-200">
            <p className="text-center text-sm text-ink/60">
              Already have an account?{" "}
              <Link to="/login" className="text-route font-semibold hover:text-route/80 transition-colors">
                Log in
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
