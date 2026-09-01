import { useEffect, useState } from "react";
import { useNavigate, useParams, Link } from "react-router-dom";
import { startAssessment, submitAssessment } from "../services/learning.js";

export default function Assessment() {
  const { courseId } = useParams();
  const navigate = useNavigate();

  const [assessmentToken, setAssessmentToken] = useState(null);
  const [questions, setQuestions] = useState(null);
  const [selections, setSelections] = useState({});
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [loadError, setLoadError] = useState("");
  const [currentQuestion, setCurrentQuestion] = useState(0);

  useEffect(() => {
    startAssessment(courseId)
      .then((data) => {
        setAssessmentToken(data.assessment_token);
        setQuestions(data.questions);
      })
      .catch((err) => {
        setLoadError(
          err?.response?.data?.detail || "Couldn't start the assessment. Try again from your course."
        );
      });
  }, [courseId]);

  function selectAnswer(questionIndex, option) {
    setSelections((s) => ({ ...s, [questionIndex]: option }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");

    if (Object.keys(selections).length < questions.length) {
      setError("Answer every question before submitting.");
      return;
    }

    setSubmitting(true);
    try {
      await submitAssessment({
        course_id: courseId,
        assessment_token: assessmentToken,
        answers: questions.map((q, i) => ({ question: q.question, selected_answer: selections[i] })),
      });
      navigate(`/courses/${courseId}`);
    } catch (err) {
      setError(
        err?.response?.data?.detail || "Couldn't submit your answers. Try again."
      );
    } finally {
      setSubmitting(false);
    }
  }

  if (loadError) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-paper to-white flex items-center justify-center px-6 py-12">
        <div className="card-soft p-10 max-w-md text-center">
          <div className="text-6xl mb-4">❌</div>
          <p className="text-red-700 font-semibold mb-6">{loadError}</p>
          <Link to={`/courses/${courseId}`} className="btn-primary">
            ← Back to course
          </Link>
        </div>
      </div>
    );
  }

  if (!questions) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-paper to-white flex items-center justify-center px-6 py-12">
        <div className="text-center">
          <div className="text-6xl mb-4 animate-pulse">⏳</div>
          <p className="text-ink/60 text-lg">Generating your assessment...</p>
        </div>
      </div>
    );
  }

  const progress = ((Object.keys(selections).length) / questions.length) * 100;

  return (
    <div className="min-h-screen bg-gradient-to-b from-paper to-white">
      <div className="max-w-3xl mx-auto px-6 py-12">
        {/* Header */}
        <Link to={`/courses/${courseId}`} className="text-sm text-route font-semibold hover:text-route/80 mb-8 inline-block transition-colors">
          ← Back to course
        </Link>

        <div className="mb-8">
          <div className="inline-block mb-4 px-4 py-2 bg-route/10 rounded-full">
            <p className="uppercase tracking-[0.2em] text-xs text-route font-bold">
              📋 Skill assessment
            </p>
          </div>
          <h1 className="font-display text-4xl mb-3 text-ink">Where are you starting from?</h1>
          <p className="text-ink/60 text-lg">
            Answer honestly — this shapes your whole roadmap, not just your grade.
          </p>
        </div>

        {/* Progress Bar */}
        <div className="mb-10">
          <div className="flex items-center justify-between mb-3">
            <span className="text-sm font-semibold text-ink">Question {currentQuestion + 1} of {questions.length}</span>
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
          <form onSubmit={handleSubmit} className="space-y-8">
            {questions.map((q, i) => (
              <fieldset key={i} className={`${i !== currentQuestion ? 'hidden' : ''}`}>
                <legend className="font-display text-2xl mb-6 text-ink">
                  {q.question}
                </legend>
                <div className="space-y-3">
                  {q.options.map((option) => (
                    <label
                      key={option}
                      className={`flex items-center gap-4 p-4 rounded-xl border-2 cursor-pointer transition-all ${
                        selections[i] === option
                          ? "border-route bg-route/10"
                          : "border-slate-200 hover:border-route/50"
                      }`}
                    >
                      <input
                        type="radio"
                        name={`q-${i}`}
                        value={option}
                        checked={selections[i] === option}
                        onChange={() => selectAnswer(i, option)}
                        className="w-5 h-5 accent-route"
                      />
                      <span className="text-base font-medium text-ink">{option}</span>
                    </label>
                  ))}
                </div>
              </fieldset>
            ))}

            {error && (
              <div className="p-4 rounded-lg bg-red-50 border border-red-200">
                <p className="text-red-700 font-medium text-sm">{error}</p>
              </div>
            )}

            {/* Navigation Buttons */}
            <div className="flex gap-4 pt-6 border-t border-slate-200">
              <button
                type="button"
                onClick={() => setCurrentQuestion(Math.max(0, currentQuestion - 1))}
                disabled={currentQuestion === 0}
                className="btn-outline px-6 py-3 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                ← Previous
              </button>
              {currentQuestion < questions.length - 1 ? (
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
                  disabled={submitting || Object.keys(selections).length < questions.length}
                  className="btn-primary px-6 py-3 ml-auto"
                >
                  {submitting ? (
                    <span className="flex items-center gap-2">
                      <span className="animate-spin">⏳</span> Submitting...
                    </span>
                  ) : (
                    "Submit assessment"
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
