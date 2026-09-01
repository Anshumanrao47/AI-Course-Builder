import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { getCourse } from "../services/courses.js";
import { getRoadmap, getProgress } from "../services/learning.js";
import {
  COURSE_STATUS_LABELS,
  skillLevelLabel,
  learningStyleLabel,
} from "../lib/courseOptions.js";

function formatDate(iso) {
  return new Date(iso).toLocaleDateString(undefined, {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
}

function formatStudyTime(minutes) {
  if (minutes < 60) return `${minutes} min/day`;
  const hrs = minutes / 60;
  return `${hrs % 1 === 0 ? hrs : hrs.toFixed(1)} hr${hrs === 1 ? "" : "s"}/day`;
}

const LESSON_STYLES = {
  completed: "text-growth",
  unlocked: "text-ink",
  locked: "text-ink/30",
};

function LessonRow({ lesson }) {
  const clickable = lesson.status !== "locked";
  const content = (
    <div className="flex items-center justify-between py-2.5">
      <span className={`text-sm ${LESSON_STYLES[lesson.status]}`}>
        {lesson.status === "completed" ? "✓ " : ""}
        {lesson.is_revision ? "↻ " : ""}
        {lesson.title}
      </span>
      <span className={`text-xs ${LESSON_STYLES[lesson.status]}`}>
        {lesson.estimated_minutes} min
      </span>
    </div>
  );
  return clickable ? (
    <Link to={`/lessons/${lesson.id}`} className="block hover:bg-ink/[0.03] rounded-lg px-2 -mx-2">
      {content}
    </Link>
  ) : (
    <div className="px-2 -mx-2">{content}</div>
  );
}

const MODULE_BADGE = {
  completed: "bg-growth/15 text-growth",
  unlocked: "bg-route/15 text-route",
  locked: "bg-ink/5 text-ink/40",
};

function ModuleBlock({ module, courseId }) {
  return (
    <div className="card overflow-hidden hover:shadow-lg transition-all">
      <div className="p-6 border-b border-slate-200 bg-gradient-to-r from-route/5 to-growth/5">
        <div className="flex items-start justify-between mb-2">
          <h3 className="font-display text-2xl text-ink">{module.title}</h3>
          <span className={`badge ${MODULE_BADGE[module.status]} text-xs font-bold`}>
            {module.status}
          </span>
        </div>
        <p className="text-xs text-ink/50 font-semibold">⏱️ {module.estimated_minutes} min total</p>
      </div>
      <div className="divide-y divide-slate-200">
        {module.lessons.map((lesson) => (
          <LessonRow key={lesson.id} lesson={lesson} />
        ))}
      </div>
      {module.status === "completed" && module.quiz_id && (
        <div className="p-4 bg-growth/5 border-t border-slate-200">
          <Link
            to={`/quizzes/${module.quiz_id}`}
            className="text-sm text-route font-semibold hover:text-route/80 transition-colors flex items-center gap-1"
          >
            Retake module quiz →
          </Link>
        </div>
      )}
    </div>
  );
}

export default function CourseDetail() {
  const { courseId } = useParams();
  const navigate = useNavigate();
  const [course, setCourse] = useState(null);
  const [roadmap, setRoadmap] = useState(null);
  const [progress, setProgress] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    getCourse(courseId)
      .then(setCourse)
      .catch(() => setError("Couldn't load this course."));
  }, [courseId]);

  useEffect(() => {
    if (!course || course.status === "pending_assessment") return;
    getRoadmap(courseId).then(setRoadmap).catch(() => {});
    getProgress(courseId).then(setProgress).catch(() => {});
  }, [course, courseId]);

  if (error) {
    return (
      <div className="max-w-2xl mx-auto px-6 py-16">
        <p className="text-red-600">{error}</p>
        <Link to="/dashboard" className="text-route font-medium">
          Back to dashboard
        </Link>
      </div>
    );
  }

  if (!course) {
    return <div className="max-w-2xl mx-auto px-6 py-16 text-ink/60">Loading...</div>;
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-paper to-white">
      <div className="max-w-4xl mx-auto px-6 py-12">
        <Link to="/dashboard" className="text-sm text-route font-semibold hover:text-route/80 mb-8 inline-block transition-colors">
          ← Dashboard
        </Link>

        <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-6 mb-10">
          <h1 className="font-display text-5xl text-ink">{course.topic}</h1>
          <span className="badge badge-warning text-sm font-bold">
            {COURSE_STATUS_LABELS[course.status] || course.status}
          </span>
        </div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-5 gap-4 mb-12">
          <div className="card p-5">
            <p className="text-xs uppercase tracking-wide text-ink/50 font-bold mb-2">Current level</p>
            <p className="font-display text-lg text-route">{skillLevelLabel(course.current_level)}</p>
          </div>
          <div className="card p-5">
            <p className="text-xs uppercase tracking-wide text-ink/50 font-bold mb-2">Target level</p>
            <p className="font-display text-lg text-route">{skillLevelLabel(course.target_level)}</p>
          </div>
          <div className="card p-5">
            <p className="text-xs uppercase tracking-wide text-ink/50 font-bold mb-2">Study time</p>
            <p className="font-display text-lg text-route">{formatStudyTime(course.study_minutes_per_day)}</p>
          </div>
          <div className="card p-5">
            <p className="text-xs uppercase tracking-wide text-ink/50 font-bold mb-2">Target date</p>
            <p className="font-display text-lg text-route">{formatDate(course.target_completion_date)}</p>
          </div>
          <div className="card p-5 sm:col-span-2 lg:col-span-1">
            <p className="text-xs uppercase tracking-wide text-ink/50 font-bold mb-2">Learning style</p>
            <p className="font-display text-lg text-route">{learningStyleLabel(course.preferred_learning_style)}</p>
          </div>
        </div>

      {course.status === "pending_assessment" && (
        <div className="card-soft p-10 text-center mb-10 rounded-3xl">
          <div className="text-6xl mb-4">🎯</div>
          <p className="font-display text-2xl mb-2 text-ink">Ready for your assessment?</p>
          <p className="text-ink/60 max-w-md mx-auto mb-8 leading-relaxed">
            A short diagnostic quiz on {course.topic} — your answers decide the whole roadmap, so take your time.
          </p>
          <button
            onClick={() => navigate(`/courses/${courseId}/assessment`)}
            className="btn-primary px-10 py-3 text-base font-semibold shadow-md hover:shadow-lg"
          >
            Start assessment →
          </button>
        </div>
      )}

      {course.status === "assessing" && !roadmap && (
        <div className="card-soft p-10 text-center mb-10 rounded-3xl">
          <div className="text-6xl mb-4 animate-pulse">⏳</div>
          <p className="text-ink/60 text-lg">We're building your roadmap...</p>
        </div>
      )}

      {roadmap && (
        <>
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-display text-2xl">Roadmap</h2>
            <div className="flex items-center gap-4 text-sm">
              {progress && (
                <span className="text-ink/60">
                  {progress.completion_percentage}% complete
                  {progress.streak_days > 0 && ` · 🔥 ${progress.streak_days} day streak`}
                </span>
              )}
              <Link to={`/courses/${courseId}/analytics`} className="text-route font-medium">
                View analytics →
              </Link>
            </div>
          </div>
          <div className="space-y-4">
            {roadmap.modules.map((module) => (
              <ModuleBlock key={module.id} module={module} courseId={courseId} />
            ))}
          </div>
        </>
      )}
      </div>
    </div>
  );
}
