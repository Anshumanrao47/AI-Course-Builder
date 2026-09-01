import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { createCourse } from "../services/courses.js";
import { SKILL_LEVELS, LEARNING_STYLES } from "../lib/courseOptions.js";

const STUDY_TIME_PRESETS = [
  { label: "30 min/day", minutes: 30 },
  { label: "1 hr/day", minutes: 60 },
  { label: "2 hrs/day", minutes: 120 },
  { label: "3+ hrs/day", minutes: 180 },
];

function defaultTargetDate() {
  const d = new Date();
  d.setMonth(d.getMonth() + 2);
  return d.toISOString().slice(0, 10);
}

export default function CourseCreate() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    topic: "",
    current_level: "beginner",
    target_level: "intermediate",
    study_minutes_per_day: 60,
    target_completion_date: defaultTargetDate(),
    preferred_learning_style: "mixed",
  });
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  function update(field, value) {
    setForm((f) => ({ ...f, [field]: value }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      const course = await createCourse(form);
      navigate(`/courses/${course.id}`);
    } catch (err) {
      const detail = err?.response?.data?.detail;
      setError(
        typeof detail === "string"
          ? detail
          : Array.isArray(detail)
          ? detail.map((d) => d.msg).join(", ")
          : "Couldn't create the course. Check your details and try again."
      );
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-paper to-white">
      <div className="max-w-2xl mx-auto px-6 py-12">
        <Link to="/dashboard" className="text-sm text-route font-semibold hover:text-route/80 mb-8 inline-block transition-colors">
          ← Back to dashboard
        </Link>

        <div className="mb-10">
          <div className="inline-block mb-4 px-4 py-2 bg-route/10 rounded-full">
            <p className="uppercase tracking-[0.2em] text-xs text-route font-bold">
              🎯 New course
            </p>
          </div>
          <h1 className="font-display text-4xl mb-3 text-ink">What do you want to learn?</h1>
          <p className="text-ink/60 text-lg">
            Be specific — the more precise your goal, the sharper your roadmap.
          </p>
        </div>

        <div className="card-soft p-8 sm:p-10">
          <form onSubmit={handleSubmit} className="space-y-7">
            {/* Topic */}
            <div className="space-y-2">
              <label className="block text-sm font-semibold text-ink" htmlFor="topic">
                Learning topic
              </label>
              <input
                id="topic"
                type="text"
                required
                placeholder="Python for Data Science"
                value={form.topic}
                onChange={(e) => update("topic", e.target.value)}
                className="input-lg"
              />
              <p className="text-xs text-ink/50">Be as specific as possible for better results.</p>
            </div>

            {/* Skill Levels */}
            <div className="grid sm:grid-cols-2 gap-6">
              <div className="space-y-2">
                <label className="block text-sm font-semibold text-ink" htmlFor="current_level">
                  Current level
                </label>
                <select
                  id="current_level"
                  value={form.current_level}
                  onChange={(e) => update("current_level", e.target.value)}
                  className="input-lg"
                >
                  {SKILL_LEVELS.map((l) => (
                    <option key={l.value} value={l.value}>
                      {l.label}
                    </option>
                  ))}
                </select>
              </div>
              <div className="space-y-2">
                <label className="block text-sm font-semibold text-ink" htmlFor="target_level">
                  Target level
                </label>
                <select
                  id="target_level"
                  value={form.target_level}
                  onChange={(e) => update("target_level", e.target.value)}
                  className="input-lg"
                >
                  {SKILL_LEVELS.map((l) => (
                    <option key={l.value} value={l.value}>
                      {l.label}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {/* Study Time */}
            <div className="space-y-3">
              <label className="block text-sm font-semibold text-ink">Study time per day</label>
              <div className="grid sm:grid-cols-2 gap-3">
                {STUDY_TIME_PRESETS.map((preset) => (
                  <button
                    type="button"
                    key={preset.minutes}
                    onClick={() => update("study_minutes_per_day", preset.minutes)}
                    className={`px-4 py-3 rounded-lg font-semibold transition-all ${
                      form.study_minutes_per_day === preset.minutes
                        ? "bg-route text-white shadow-md"
                        : "border-2 border-slate-200 text-ink hover:border-route hover:text-route"
                    }`}
                  >
                    {preset.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Target Completion Date */}
            <div className="space-y-2">
              <label className="block text-sm font-semibold text-ink" htmlFor="target_completion_date">
                Target completion date
              </label>
              <input
                id="target_completion_date"
                type="date"
                required
                value={form.target_completion_date}
                onChange={(e) => update("target_completion_date", e.target.value)}
                className="input-lg"
              />
            </div>

            {/* Learning Style */}
            <div className="space-y-2">
              <label className="block text-sm font-semibold text-ink" htmlFor="preferred_learning_style">
                Preferred learning style
              </label>
              <select
                id="preferred_learning_style"
                value={form.preferred_learning_style}
                onChange={(e) => update("preferred_learning_style", e.target.value)}
                className="input-lg"
              >
                {LEARNING_STYLES.map((s) => (
                  <option key={s.value} value={s.value}>
                    {s.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Error */}
            {error && (
              <div className="p-4 rounded-lg bg-red-50 border border-red-200">
                <p className="text-red-700 font-medium text-sm">{error}</p>
              </div>
            )}

            {/* Submit */}
            <button
              type="submit"
              disabled={submitting}
              className="btn-primary w-full py-3 text-base font-semibold shadow-md hover:shadow-lg"
            >
              {submitting ? (
                <span className="flex items-center justify-center gap-2">
                  <span className="animate-spin">⏳</span> Creating course...
                </span>
              ) : (
                "Create course"
              )}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
