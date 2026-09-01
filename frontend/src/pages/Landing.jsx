import { Link } from "react-router-dom";

const milestones = [
  { label: "Set a goal", detail: "\"Python for Data Science in 2 months.\"" },
  { label: "Get assessed", detail: "A short adaptive check finds your real starting point." },
  { label: "Follow the route", detail: "Modules and lessons ordered for how you actually learn." },
  { label: "Adjust as you go", detail: "Every quiz reshapes what comes next." },
];

const features = [
  {
    title: "Skill assessment",
    body: "A quick, adaptive quiz places you accurately instead of guessing your level.",
    icon: "📊",
  },
  {
    title: "Personalized roadmap",
    body: "Modules ordered around your goal, pace, and available study time.",
    icon: "🗺️",
  },
  {
    title: "Generated lessons",
    body: "Explanations, worked examples, and exercises pitched at your level.",
    icon: "📚",
  },
  {
    title: "Adaptive difficulty",
    body: "Struggle with a topic and the plan slows down and adds revision automatically.",
    icon: "⚙️",
  },
];

export default function Landing() {
  return (
    <div className="bg-gradient-to-b from-paper via-paper to-white">
      {/* Hero */}
      <section className="max-w-7xl mx-auto px-6 pt-20 pb-32">
        <div className="grid md:grid-cols-2 gap-16 items-center mb-16">
          <div className="animate-slide-up">
            <div className="inline-block mb-6 px-4 py-2 bg-route/10 rounded-full">
              <p className="uppercase tracking-[0.2em] text-xs text-route font-bold">
                🚀 Multi-agent learning system
              </p>
            </div>
            <h1 className="font-display text-6xl leading-[1.1] mb-8 text-gradient bg-gradient-to-r from-ink to-route bg-clip-text text-transparent">
              Tell it your goal.
              <br />
              It plots the route.
            </h1>
            <p className="text-ink/70 text-lg mb-10 max-w-md leading-relaxed">
              AI Course Builder assesses what you already know, drafts a roadmap toward your goal, and keeps re-routing it as you learn.
            </p>
            <div className="flex flex-wrap gap-4">
              <Link
                to="/register"
                className="btn-primary text-lg px-8 py-3 shadow-lg hover:shadow-xl"
              >
                Start a course
              </Link>
              <Link
                to="/login"
                className="btn-secondary text-lg px-8 py-3"
              >
                I have an account
              </Link>
            </div>
          </div>

          {/* Animated illustration */}
          <div className="relative animate-fade-in">
            <div className="absolute inset-0 bg-gradient-to-r from-route/20 to-growth/20 rounded-3xl blur-3xl"></div>
            <svg viewBox="0 0 400 420" className="w-full h-auto relative z-10" fill="none">
              <defs>
                <linearGradient id="routeGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="#2A4B8D" />
                  <stop offset="100%" stopColor="#2E7D5B" />
                </linearGradient>
              </defs>
              <path
                d="M40 40 C 140 40, 20 140, 100 160 S 260 210, 200 260 S 60 330, 140 380"
                stroke="url(#routeGradient)"
                strokeWidth="3"
                strokeDasharray="1 10"
                strokeLinecap="round"
              />
              {[
                [40, 40],
                [100, 160],
                [200, 260],
                [140, 380],
              ].map(([cx, cy], i) => (
                <g key={i}>
                  <circle cx={cx} cy={cy} r="12" fill="white" stroke="#2A4B8D" strokeWidth="3" />
                  <circle cx={cx} cy={cy} r="5" fill="#2A4B8D" />
                </g>
              ))}
            </svg>
            <div className="absolute inset-0 flex flex-col justify-between py-8 pointer-events-none">
              {milestones.map((m, i) => (
                <div
                  key={m.label}
                  className={`max-w-[13rem] ${i % 2 === 1 ? "self-end text-right" : "self-start"}`}
                  style={{ marginTop: i === 0 ? 0 : undefined }}
                >
                  <p className="font-display text-lg font-bold text-ink">{m.label}</p>
                  <p className="text-sm text-ink/60">{m.detail}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* How it works */}
      <section className="border-t border-slate-200 bg-gradient-to-b from-white to-slate-50">
        <div className="max-w-7xl mx-auto px-6 py-24">
          <div className="mb-16">
            <h2 className="font-display text-4xl mb-4 text-ink">How it works</h2>
            <p className="text-ink/60 text-lg max-w-2xl">
              Six agents hand off to each other behind the scenes so the plan stays personal from your first answer to your last quiz.
            </p>
          </div>
          <div className="grid md:grid-cols-4 gap-8">
            {["Assess", "Plan", "Teach", "Adapt"].map((step, i) => (
              <div
                key={step}
                className="card p-8 hover:shadow-lg group cursor-default"
              >
                <div className="mb-6 inline-block">
                  <span className="font-display text-5xl bg-gradient-to-br from-route to-route/60 bg-clip-text text-transparent">
                    {String(i + 1).padStart(2, "0")}
                  </span>
                </div>
                <p className="font-display text-2xl text-ink group-hover:text-route transition-colors">{step}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="max-w-7xl mx-auto px-6 py-24">
        <h2 className="font-display text-4xl mb-16 text-ink">Built to keep up with you</h2>
        <div className="grid md:grid-cols-2 gap-12">
          {features.map((f, i) => (
            <div
              key={f.title}
              className="card-soft p-8 border-l-4 border-l-route hover:shadow-lg transition-all"
              style={{
                animation: `slideUp 0.5s ease-out ${i * 0.1}s both`,
              }}
            >
              <div className="text-4xl mb-4">{f.icon}</div>
              <h3 className="font-display text-2xl mb-3 text-ink">{f.title}</h3>
              <p className="text-ink/70 leading-relaxed">{f.body}</p>
            </div>
          ))}
        </div>
      </section>

      {/* CTA */}
      <section className="border-t border-slate-200">
        <div className="max-w-7xl mx-auto px-6 py-24 text-center">
          <h2 className="font-display text-4xl mb-8 text-ink">
            Where do you want to be in a month?
          </h2>
          <p className="text-ink/60 text-lg mb-10 max-w-xl mx-auto">
            Start your personalized learning journey now and achieve your goals faster.
          </p>
          <Link
            to="/register"
            className="btn-primary text-lg px-10 py-4 shadow-lg hover:shadow-xl inline-flex"
          >
            Build my course
          </Link>
        </div>
      </section>
    </div>
  );
}
