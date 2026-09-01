import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Legend,
} from "recharts";
import { getAnalytics } from "../services/learning.js";
import { getCourse } from "../services/courses.js";

function formatShortDate(iso) {
  return new Date(iso).toLocaleDateString(undefined, { month: "short", day: "numeric" });
}

function StatCard({ label, value, icon, color = "route" }) {
  return (
    <div className={`card p-6 border-l-4 border-l-${color}`}>
      <div className="flex items-start justify-between mb-2">
        <p className="text-xs uppercase tracking-wide text-ink/50 font-bold">{label}</p>
        <span className="text-3xl">{icon}</span>
      </div>
      <p className="font-display text-3xl text-ink">{value}</p>
    </div>
  );
}

export default function Analytics() {
  const { courseId } = useParams();
  const [course, setCourse] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([getCourse(courseId), getAnalytics(courseId)])
      .then(([c, a]) => {
        setCourse(c);
        setAnalytics(a);
      })
      .catch(() => setError("Couldn't load analytics for this course."));
  }, [courseId]);

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-paper to-white flex items-center justify-center px-6 py-12">
        <div className="card-soft p-10 max-w-md text-center">
          <div className="text-6xl mb-4">❌</div>
          <p className="text-red-700 font-semibold mb-6">{error}</p>
          <Link to={`/courses/${courseId}`} className="btn-primary">
            Back to course
          </Link>
        </div>
      </div>
    );
  }

  if (!analytics || !course) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-paper to-white flex items-center justify-center px-6 py-12">
        <div className="text-center">
          <div className="text-6xl mb-4 animate-pulse">📊</div>
          <p className="text-ink/60 text-lg">Loading analytics...</p>
        </div>
      </div>
    );
  }

  const quizData = analytics.quiz_scores.map((q, i) => ({
    label: `#${i + 1}`,
    title: q.module_title,
    score: q.score,
  }));

  const dailyData = analytics.daily.map((d) => ({
    date: formatShortDate(d.date),
    Lessons: d.lessons_completed,
    Quizzes: d.quizzes_taken,
  }));

  const avgScore = quizData.length
    ? Math.round(quizData.reduce((s, q) => s + q.score, 0) / quizData.length)
    : 0;

  return (
    <div className="min-h-screen bg-gradient-to-b from-paper to-white">
      <div className="max-w-6xl mx-auto px-6 py-12">
        <Link to={`/courses/${courseId}`} className="text-sm text-route font-semibold hover:text-route/80 mb-8 inline-block transition-colors">
          ← {course.topic}
        </Link>

        <div className="mb-12">
          <div className="inline-block mb-4 px-4 py-2 bg-route/10 rounded-full">
            <p className="uppercase tracking-[0.2em] text-xs text-route font-bold">
              📊 Analytics
            </p>
          </div>
          <h1 className="font-display text-4xl text-ink">Your progress</h1>
        </div>

        {/* Key Stats */}
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-12">
          <StatCard
            label="Completion"
            value={`${analytics.completion_percentage}%`}
            icon="✅"
            color="green-500"
          />
          <StatCard
            label="Current Streak"
            value={`${analytics.current_streak_days}d`}
            icon="🔥"
            color="amber-500"
          />
          <StatCard
            label="Quizzes Taken"
            value={analytics.quiz_scores.length}
            icon="📝"
            color="blue-500"
          />
          <StatCard
            label="Avg Score"
            value={`${avgScore}%`}
            icon="⭐"
            color="yellow-500"
          />
        </div>

        {/* Quiz Performance */}
        <div className="mb-12">
          <h2 className="font-display text-2xl mb-6 text-ink">Quiz performance</h2>
          {quizData.length > 0 ? (
            <div className="card p-6 overflow-x-auto" style={{ height: 320 }}>
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={quizData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                  <XAxis dataKey="label" tick={{ fontSize: 12 }} />
                  <YAxis domain={[0, 100]} tick={{ fontSize: 12 }} />
                  <Tooltip
                    cursor={{ fill: "rgba(42, 75, 141, 0.1)" }}
                    contentStyle={{ backgroundColor: "#fff", border: "2px solid #2A4B8D", borderRadius: "8px" }}
                  />
                  <Line type="monotone" dataKey="score" stroke="#2A4B8D" strokeWidth={3} dot={{ r: 5, fill: "#2A4B8D" }} activeDot={{ r: 7 }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="card p-10 text-center bg-white/50">
              <p className="text-ink/50 text-base">Take a quiz to see your scores here.</p>
            </div>
          )}
        </div>

        {/* Learning Consistency */}
        <div className="mb-12">
          <h2 className="font-display text-2xl mb-6 text-ink">Learning consistency</h2>
          {dailyData.length > 0 ? (
            <div className="card p-6 overflow-x-auto" style={{ height: 320 }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={dailyData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                  <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                  <YAxis allowDecimals={false} tick={{ fontSize: 12 }} />
                  <Tooltip
                    cursor={{ fill: "rgba(42, 75, 141, 0.1)" }}
                    contentStyle={{ backgroundColor: "#fff", border: "2px solid #2A4B8D", borderRadius: "8px" }}
                  />
                  <Legend wrapperStyle={{ paddingTop: "20px" }} />
                  <Bar dataKey="Lessons" fill="#2A4B8D" radius={[8, 8, 0, 0]} />
                  <Bar dataKey="Quizzes" fill="#2E7D5B" radius={[8, 8, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="card p-10 text-center bg-white/50">
              <p className="text-ink/50 text-base">Complete a lesson to start building your activity history.</p>
            </div>
          )}
        </div>

        {/* Topics */}
        <div className="grid lg:grid-cols-2 gap-8">
          <div>
            <h2 className="font-display text-2xl mb-6 text-ink">Strong topics</h2>
            {analytics.strong_topics.length ? (
              <div className="flex flex-wrap gap-3">
                {analytics.strong_topics.map((t) => (
                  <span key={t} className="badge badge-success text-xs font-bold px-4 py-2">
                    ✓ {t}
                  </span>
                ))}
              </div>
            ) : (
              <div className="card p-6 bg-white/50 text-center">
                <p className="text-ink/50 text-sm">Not enough data yet.</p>
              </div>
            )}
          </div>
          <div>
            <h2 className="font-display text-2xl mb-6 text-ink">Topics to review</h2>
            {analytics.weak_topics.length ? (
              <div className="flex flex-wrap gap-3">
                {analytics.weak_topics.map((t) => (
                  <span key={t} className="badge badge-warning text-xs font-bold px-4 py-2">
                    ⚠ {t}
                  </span>
                ))}
              </div>
            ) : (
              <div className="card p-6 bg-white/50 text-center">
                <p className="text-ink/50 text-sm">Not enough data yet.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
