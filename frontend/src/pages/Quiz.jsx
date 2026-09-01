import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { getQuiz, submitQuiz } from "../services/learning.js";

export default function Quiz() {
  const { quizId } = useParams();
  const [quiz, setQuiz] = useState(null);
  const [answers, setAnswers] = useState({});
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState(null);
  const [currentQuestion, setCurrentQuestion] = useState(0);

  useEffect(() => {
    getQuiz(quizId)
      .then(setQuiz)
      .catch((err) => setError(err?.response?.data?.detail || "Couldn't load this quiz."));
  }, [quizId]);

  function setAnswer(questionId, value) {
    setAnswers((a) => ({ ...a, [questionId]: value }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    if (Object.keys(answers).length < quiz.questions.length) {
      setError("Answer every question before submitting.");
      return;
    }
    setSubmitting(true);
    try {
      const data = await submitQuiz(
        quizId,
        quiz.questions.map((q) => ({ question_id: q.id, answer: answers[q.id] }))
      );
      setResult(data);
    } catch (err) {
      setError(err?.response?.data?.detail || "Couldn't submit the quiz.");
    } finally {
      setSubmitting(false);
    }
  }

  if (error && !quiz) {
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

  if (!quiz) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-paper to-white flex items-center justify-center px-6 py-12">
        <div className="text-center">
          <div className="text-6xl mb-4 animate-pulse">📝</div>
          <p className="text-ink/60 text-lg">Generating your quiz...</p>
        </div>
      </div>
    );
  }

  if (result) {
    const passed = result.score >= 60;
    return (
      <div className="min-h-screen bg-gradient-to-b from-paper to-white flex items-center justify-center px-6 py-12">
        <div className="max-w-md w-full card-soft p-10 text-center">
          <div className={`text-7xl mb-6 ${passed ? 'text-growth' : 'text-amber-600'}`}>
            {passed ? '🎉' : '📊'}
          </div>
          <div className="uppercase tracking-[0.2em] text-xs text-route font-bold mb-4">
            {quiz.title}
          </div>
          <p className={`font-display text-6xl mb-6 font-bold ${passed ? "text-growth" : "text-amber-700"}`}>
            {result.score}%
          </p>
          <p className="text-ink/80 mb-8 text-lg leading-relaxed">{result.recommendation}</p>

          {result.weak_topics?.length > 0 && (
            <div className="mb-8">
              <p className="text-xs font-bold text-ink/60 uppercase tracking-wide mb-3">Topics to review</p>
              <div className="flex flex-wrap justify-center gap-2">
                {result.weak_topics.map((t) => (
                  <span key={t} className="badge badge-warning text-xs">
                    {t}
                  </span>
                ))}
              </div>
            </div>
          )}

          <div className="bg-route/5 border border-route/20 rounded-lg p-5 mb-8">
            <p className="text-sm text-ink/70">{result.adaptive_message}</p>
          </div>

          <Link
            to="/dashboard"
            className="btn-primary w-full py-3 font-semibold inline-block"
          >
            Back to dashboard
          </Link>
        </div>
      </div>
    );
  }

  const q = quiz.questions[currentQuestion];
  const progress = ((currentQuestion + 1) / quiz.questions.length) * 100;

  return (
    <div className="min-h-screen bg-gradient-to-b from-paper to-white">
      <div className="max-w-3xl mx-auto px-6 py-12">
        <Link to="/dashboard" className="text-sm text-route font-semibold hover:text-route/80 mb-8 inline-block transition-colors">
          ← Back to dashboard
        </Link>

        <div className="mb-10">
          <div className="inline-block mb-4 px-4 py-2 bg-route/10 rounded-full">
            <p className="uppercase tracking-[0.2em] text-xs text-route font-bold">
              📝 Quiz
            </p>
          </div>
          <h1 className="font-display text-4xl mb-3 text-ink">{quiz.title}</h1>
        </div>

        {/* Progress Bar */}
        <div className="mb-10">
          <div className="flex items-center justify-between mb-3">
            <span className="text-sm font-semibold text-ink">Question {currentQuestion + 1} of {quiz.questions.length}</span>
            <span className="text-sm font-semibold text-route">{Math.round(progress)}%</span>
          </div>
          <div className="h-2 rounded-full bg-slate-200 overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-route to-growth transition-all"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>

        <div className="card-soft p-8 sm:p-10">
          <form onSubmit={handleSubmit}>
            <fieldset className="space-y-6">
              <legend className="font-display text-2xl mb-8 text-ink">
                {q.question}
              </legend>

              {q.question_type === "multiple_choice" ? (
                <div className="space-y-3">
                  {q.options.map((option) => (
                    <label
                      key={option}
                      className={`flex items-center gap-4 p-4 rounded-xl border-2 cursor-pointer transition-all ${
                        answers[q.id] === option
                          ? "border-route bg-route/10"
                          : "border-slate-200 hover:border-route/50"
                      }`}
                    >
                      <input
                        type="radio"
                        name={q.id}
                        value={option}
                        checked={answers[q.id] === option}
                        onChange={() => setAnswer(q.id, option)}
                        className="w-5 h-5 accent-route"
                      />
                      <span className="text-base font-medium text-ink">{option}</span>
                    </label>
                  ))}
                </div>
              ) : (
                <textarea
                  rows={6}
                  value={answers[q.id] || ""}
                  onChange={(e) => setAnswer(q.id, e.target.value)}
                  placeholder={q.question_type === "coding" ? "Write your code here..." : "Write your answer here..."}
                  className="input font-mono text-sm"
                />
              )}
            </fieldset>

            {error && (
              <div className="p-4 rounded-lg bg-red-50 border border-red-200 mt-6">
                <p className="text-red-700 font-medium text-sm">{error}</p>
              </div>
            )}

            {/* Navigation Buttons */}
            <div className="flex gap-4 pt-8 border-t border-slate-200 mt-8">
              <button
                type="button"
                onClick={() => setCurrentQuestion(Math.max(0, currentQuestion - 1))}
                disabled={currentQuestion === 0}
                className="btn-outline px-6 py-3 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                ← Previous
              </button>
              {currentQuestion < quiz.questions.length - 1 ? (
                <button
                  type="button"
                  onClick={() => setCurrentQuestion(currentQuestion + 1)}
                  className="btn-primary px-6 py-3 ml-auto"
                >
                  Next →
                </button>
              ) : (
                <button
                  type="submit"
                  disabled={submitting || Object.keys(answers).length < quiz.questions.length}
                  className="btn-primary px-6 py-3 ml-auto"
                >
                  {submitting ? (
                    <span className="flex items-center gap-2">
                      <span className="animate-spin">⏳</span> Grading...
                    </span>
                  ) : (
                    "Submit quiz"
                  )}
                </button>
              )}
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
