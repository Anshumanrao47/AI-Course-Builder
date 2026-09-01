import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";
import { listCourses } from "../services/courses.js";
import { getProgress } from "../services/learning.js";
import { COURSE_STATUS_LABELS, skillLevelLabel } from "../lib/courseOptions.js";

function formatStudyTime(minutes) {
  if (minutes < 60) return `${minutes} min/day`;
  const hrs = minutes / 60;
  return `${hrs % 1 === 0 ? hrs : hrs.toFixed(1)} hr${hrs === 1 ? "" : "s"}/day`;
}

const STATUS_COLORS = {
  pending_assessment: "badge-warning",
  assessing: "badge-neutral",
  in_progress: "badge-primary",
  completed: "badge-success",
};

const STATUS_ICONS = {
  pending_assessment: "🎯",
  assessing: "⏳",
  in_progress: "🚀",
  completed: "✅",
};

function CourseCard({ course, progress }) {
  const statusColor = STATUS_COLORS[course.status] || "badge-neutral";
  const statusIcon = STATUS_ICONS[course.status] || "📚";

  return (
    <Link
      to={`/courses/${course.id}`}
      className="card group overflow-hidden hover:shadow-xl transition-all"
    >
      <div className="relative h-32 bg-gradient-to-br from-route/10 to-growth/10 group-hover:from-route/20 group-hover:to-growth/20 transition-colors flex items-center justify-center">
        <span className="text-6xl opacity-50 group-hover:opacity-100 transition-opacity">
          {statusIcon}
        </span>
      </div>
      <div className="p-6">
        <div className="flex items-start justify-between mb-3">
          <h3 className="font-display text-xl text-ink group-hover:text-route transition-colors flex-1">
            {course.topic}
          </h3>
          <span className={`badge ${statusColor} text-xs font-bold whitespace-nowrap ml-3`}>
            {COURSE_STATUS_LABELS[course.status] || course.status}
          </span>
        </div>
        <p className="text-sm text-ink/60 mb-4">
          {skillLevelLabel(course.current_level)} → {skillLevelLabel(course.target_level)}
          {" · "}
          {formatStudyTime(course.study_minutes_per_day)}
        </p>
        {progress && (
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-bold text-ink/60">{progress.completion_percentage}%</span>
              {progress.streak_days > 0 && (
                <span className="text-xs font-bold text-growth">🔥 {progress.streak_days}d streak</span>
              )}
            </div>
            <div className="h-2 rounded-full bg-slate-200 overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-route to-growth transition-all"
                style={{ width: `${progress.completion_percentage}%` }}
              />
            </div>
          </div>
        )}
      </div>
    </Link>
  );
}

export default function Dashboard() {
  const { user } = useAuth();
  const [courses, setCourses] = useState(null);
  const [progressByCourse, setProgressByCourse] = useState({});
  const [error, setError] = useState("");

  useEffect(() => {
    listCourses()
      .then(async (list) => {
        setCourses(list);
        const active = list.filter((c) => c.status !== "pending_assessment");
        const entries = await Promise.all(
          active.map((c) => getProgress(c.id).then((p) => [c.id, p]).catch(() => null))
        );
        setProgressByCourse(Object.fromEntries(entries.filter(Boolean)));
      })
      .catch(() => setError("Couldn't load your courses."));
  }, []);

  const firstName = user?.full_name?.split(" ")[0] || "there";
  const activeCourses = courses?.filter((c) => c.status !== "pending_assessment") || [];
  const pendingCourses = courses?.filter((c) => c.status === "pending_assessment") || [];

  return (
    <div className="bg-gradient-to-b from-paper to-white min-h-screen">
      <div className="max-w-7xl mx-auto px-6 py-12">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-6 mb-12">
          <div>
            <h1 className="font-display text-4xl sm:text-5xl mb-3 text-ink">
              Welcome, <span className="text-route">{firstName}</span> 👋
            </h1>
            <p className="text-ink/60 text-lg">
              {courses?.length
                ? "Pick up where you left off, or start something new."
                : "Set a goal and get your first roadmap."}
            </p>
          </div>
          <Link
            to="/courses/new"
            className="btn-primary text-lg px-8 py-3 shadow-md hover:shadow-lg self-start sm:self-auto whitespace-nowrap"
          >
            + New course
          </Link>
        </div>

        {error && (
          <div className="mb-8 p-4 rounded-lg bg-red-50 border border-red-200">
            <p className="text-red-700 font-medium">{error}</p>
          </div>
        )}

        {courses === null && !error && (
          <div className="text-center py-12">
            <div className="inline-block animate-pulse">
              <p className="text-ink/60 text-lg">⏳ Loading your courses...</p>
            </div>
          </div>
        )}

        {/* Active Courses Section */}
        {courses && activeCourses.length > 0 && (
          <div className="mb-16">
            <div className="flex items-center gap-2 mb-6">
              <span className="text-2xl">📚</span>
              <h2 className="font-display text-2xl text-ink">Active Courses</h2>
            </div>
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {activeCourses.map((course) => (
                <CourseCard
                  key={course.id}
                  course={course}
                  progress={progressByCourse[course.id]}
                />
              ))}
            </div>
          </div>
        )}

        {/* Pending Assessment Section */}
        {pendingCourses.length > 0 && (
          <div className="mb-16">
            <div className="flex items-center gap-2 mb-6">
              <span className="text-2xl">🎯</span>
              <h2 className="font-display text-2xl text-ink">Awaiting Assessment</h2>
            </div>
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {pendingCourses.map((course) => (
                <CourseCard key={course.id} course={course} progress={null} />
              ))}
            </div>
          </div>
        )}

        {/* Empty State */}
        {courses?.length === 0 && (
          <div className="card-soft p-12 text-center rounded-3xl">
            <div className="text-6xl mb-4">🎓</div>
            <p className="font-display text-2xl mb-3 text-ink">No courses yet</p>
            <p className="text-ink/60 mb-8 max-w-md mx-auto">
              Tell us what you want to learn and we'll build a personalized roadmap for you.
            </p>
            <Link
              to="/courses/new"
              className="btn-primary inline-block px-8 py-3"
            >
              Create my first course
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}
