import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { getLesson, completeLesson } from "../services/learning.js";

export default function Lesson() {
  const { lessonId } = useParams();
  const navigate = useNavigate();
  const [lesson, setLesson] = useState(null);
  const [error, setError] = useState("");
  const [completing, setCompleting] = useState(false);
  const [result, setResult] = useState(null);

  useEffect(() => {
    setLesson(null);
    setResult(null);
    getLesson(lessonId)
      .then(setLesson)
      .catch((err) => setError(err?.response?.data?.detail || "Couldn't load this lesson."));
  }, [lessonId]);

  async function handleComplete() {
    setCompleting(true);
    try {
      const data = await completeLesson(lessonId);
      setResult(data);
    } catch (err) {
      setError(err?.response?.data?.detail || "Couldn't mark this lesson complete.");
    } finally {
      setCompleting(false);
    }
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-paper to-white flex items-center justify-center px-6 py-12">
        <div className="card-soft p-10 max-w-md text-center">
          <div className="text-6xl mb-4">❌</div>
          <p className="text-red-700 font-semibold mb-6">{error}</p>
          <Link to="/dashboard" className="btn-primary">
            Back to dashboard
          </Link>
        </div>
      </div>
    );
  }

  if (!lesson) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-paper to-white flex items-center justify-center px-6 py-12">
        <div className="text-center">
          <div className="text-6xl mb-4 animate-pulse">📚</div>
          <p className="text-ink/60 text-lg">Generating your lesson...</p>
        </div>
      </div>
    );
  }

  const isDone = result || lesson.status === "completed";

  return (
    <div className="min-h-screen bg-gradient-to-b from-paper to-white">
      <div className="max-w-3xl mx-auto px-6 py-12">
        <Link to="/dashboard" className="text-sm text-route font-semibold hover:text-route/80 mb-8 inline-block transition-colors">
          ← Back to dashboard
        </Link>

        <div className="mb-8">
          <div className="inline-flex gap-2 mb-4">
            <span className="badge badge-primary text-xs font-bold">
              {lesson.is_revision ? "↻ Revision" : "📚 Lesson"}
            </span>
          </div>
          <h1 className="font-display text-4xl mb-4 text-ink">{lesson.title}</h1>
        </div>

        <div className="card-soft p-8 sm:p-10 space-y-8">
          {lesson.objectives?.length > 0 && (
            <div className="border-l-4 border-route pl-6">
              <h2 className="font-display text-xl mb-4 text-ink">You'll learn to</h2>
              <ul className="space-y-2">
                {lesson.objectives.map((o, i) => (
                  <li key={i} className="flex gap-3 text-ink/80">
                    <span className="text-route font-bold flex-shrink-0">✓</span>
                    <span>{o}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {lesson.explanation && (
            <div className="bg-white rounded-lg p-6 border border-slate-200">
              <h2 className="font-display text-lg mb-4 text-ink">Explanation</h2>
              <p className="text-ink/80 leading-relaxed whitespace-pre-line">{lesson.explanation}</p>
            </div>
          )}

          {lesson.examples?.length > 0 && (
            <div>
              <h2 className="font-display text-lg mb-4 text-ink">Examples</h2>
              <div className="space-y-4">
                {lesson.examples.map((ex, i) => (
                  <div key={i} className="rounded-lg border border-slate-200 bg-white p-5 font-mono text-sm text-ink/80 overflow-x-auto">
                    <pre className="whitespace-pre-wrap break-words">{ex}</pre>
                  </div>
                ))}
              </div>
            </div>
          )}

          {lesson.exercise && (
            <div className="border-l-4 border-amber bg-amber/5 pl-6 pr-6 py-6 rounded-r-lg">
              <h2 className="font-display text-lg mb-3 text-amber font-bold">Try it yourself</h2>
              <p className="text-amber/80">{lesson.exercise}</p>
            </div>
          )}

          {lesson.summary && (
            <div className="bg-gradient-to-r from-route/5 to-growth/5 border border-route/20 rounded-lg p-6">
              <p className="font-semibold text-ink/70">
                <span className="font-display">Summary — </span>
                {lesson.summary}
              </p>
            </div>
          )}

          {!isDone && (
            <button
              onClick={handleComplete}
              disabled={completing}
              className="btn-primary w-full py-3 text-base font-semibold shadow-md hover:shadow-lg mt-10"
            >
              {completing ? (
                <span className="flex items-center justify-center gap-2">
                  <span className="animate-spin">⏳</span> Saving...
                </span>
              ) : (
                "Mark complete ✓"
              )}
            </button>
          )}

          {result && (
            <div className="bg-gradient-to-br from-growth/10 to-growth/5 border-2 border-growth/30 rounded-2xl p-8 text-center">
              <div className="text-6xl mb-4">🎉</div>
              <p className="font-display text-2xl text-growth mb-4">Lesson complete</p>
              {result.quiz_id ? (
                <>
                  <p className="text-ink/60 mb-6">You've finished this module — take the quiz to keep going.</p>
                  <button
                    onClick={() => navigate(`/quizzes/${result.quiz_id}`)}
                    className="btn-primary px-8 py-3 font-semibold"
                  >
                    Take module quiz →
                  </button>
                </>
              ) : result.next_lesson_id ? (
                <button
                  onClick={() => navigate(`/lessons/${result.next_lesson_id}`)}
                  className="btn-primary px-8 py-3 font-semibold"
                >
                  Next lesson →
                </button>
              ) : (
                <Link to="/dashboard" className="text-route font-semibold hover:text-route/80 text-lg">
                  Back to dashboard →
                </Link>
              )}
            </div>
          )}

          {isDone && !result && (
            <div className="text-center p-6 bg-slate-50 rounded-lg">
              <p className="text-sm text-ink/50">You've already completed this lesson.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
