# AI Course Builder

A full-stack, multi-agent AI system that turns a learning goal ("Python for
Data Science in 2 months") into a personalized, adaptive course: skill
assessment, roadmap, lessons, quizzes, and continuous re-planning based on
performance.

**All 8 phases are implemented** — auth, course creation, skill assessment,
roadmap planning, lesson content generation, quizzes, evaluation, adaptive
re-planning, and an analytics dashboard — and the full pipeline has been
run end-to-end against a live server as part of building it (see
"Testing notes" below).

## Stack

| Layer      | Tech                                                        |
|------------|--------------------------------------------------------------|
| Frontend   | React, Vite, Tailwind CSS, React Router, Recharts             |
| Backend    | FastAPI, Pydantic, SQLAlchemy                                 |
| Database   | PostgreSQL                                                    |
| AI system  | LangGraph (orchestration) + OpenAI (generation)                |
| Auth       | JWT (python-jose + bcrypt)                                     |

## How the multi-agent system works

Six agents, each a focused function that asks the OpenAI API for a
Pydantic-validated JSON response (`app/core/ai_client.py` — never trusts
raw LLM output; retries once on a validation failure, then raises):

| # | Agent | File | Triggered by |
|---|-------|------|---------------|
| 1 | Skill Assessment | `app/agents/assessment_agent.py` | `POST /assessment/start`, then evaluated inside `POST /assessment/submit` |
| 2 | Course Planning | `app/agents/planner_agent.py` | Runs right after assessment, in the same graph invocation |
| 3 | Content Generation | `app/agents/content_agent.py` | `GET /lessons/{id}` — lazily, on first open |
| 4 | Quiz Generation | `app/agents/quiz_agent.py` | `GET /quizzes/{id}` — lazily, on first open |
| 5 | Evaluation | `app/agents/evaluation_agent.py` | Inside `POST /quizzes/{id}/submit` |
| 6 | Adaptive Learning | `app/agents/adaptive_agent.py` | Same call, right after evaluation; also callable directly via `POST /roadmap/adapt` |

Two of these pairs always run back-to-back with no user input in between,
so they're wired as small **LangGraph** graphs (`app/agents/graphs.py`)
sharing one `CourseState` (`app/agents/state.py`):

- **planning_graph**: `evaluate_assessment → plan_roadmap`
- **adaptive_graph**: `evaluate_quiz → adapt_roadmap`

Content and quiz generation are each a single agent call triggered by a
`GET` request, so they're called directly rather than wrapped in a
one-node graph.

### Mock mode — run the whole thing without an OpenAI key

Every agent has a deterministic mock fallback. Set `USE_MOCK_AI=true` (or
just leave `OPENAI_API_KEY` unset) and the entire pipeline — assessment,
roadmap generation, lesson content, quizzes, grading, adaptive
re-planning — works end-to-end with no network calls. This is how the
pipeline was tested while building it, and it's a genuinely useful way to
demo or develop the app without spending API credits.

## Project structure

```text
ai-course-builder/
├── frontend/
│   └── src/
│       ├── pages/         Landing, Login, Register, Dashboard,
│       │                  CourseCreate, CourseDetail, Assessment,
│       │                  Lesson, Quiz, Analytics
│       ├── components/    Navbar, ProtectedRoute
│       ├── services/      api.js, courses.js, learning.js
│       ├── context/       AuthContext
│       └── lib/           courseOptions.js (shared enum labels)
│
├── backend/
│   └── app/
│       ├── agents/        state.py, ai_schemas.py, graphs.py,
│       │                  assessment_agent.py, planner_agent.py,
│       │                  content_agent.py, quiz_agent.py,
│       │                  evaluation_agent.py, adaptive_agent.py
│       ├── api/           auth, users, courses, assessment, lessons,
│       │                  quizzes, progress, analytics, roadmap
│       ├── core/          config.py, security.py, ai_client.py
│       ├── database/      base.py, session.py
│       ├── models/        user, course, preference, module, lesson,
│       │                  quiz, quiz_question, quiz_attempt,
│       │                  progress, analytics, enums
│       ├── schemas/       Pydantic request/response models
│       └── main.py
│
└── README.md
```

## Database models

`User`, `Course`, `UserLearningPreference`, `Module`, `Lesson`, `Quiz`,
`QuizQuestion`, `QuizAttempt`, `UserProgress`, `LearningAnalytics` — all
in `backend/app/models/`. Tables auto-create on backend startup via
`Base.metadata.create_all` (swap for Alembic migrations before any real
production use — the model layout is stable enough now to make that
worthwhile).

A few deliberate design choices:
- **Lesson content and quiz questions are generated lazily**, on first
  `GET`, not upfront when the roadmap is created — so creating a course
  stays fast and you never pay for content the learner never opens.
- **Assessment questions aren't stored in a table.** They're generated,
  then packaged (with their correct answers) into a short-lived signed
  JWT returned to the client and echoed back unopened at submit time —
  avoids a schema for what's inherently a single-use, two-request
  exchange.
- **`QuizQuestion.correct_answer` is never sent to the client** before
  grading — see `schemas/quiz.py`'s `QuizQuestionPublic`.

## API endpoints

```text
POST   /auth/register
POST   /auth/login
GET    /users/me
GET    /users/me/preferences
PUT    /users/me/preferences

POST   /courses/create
GET    /courses
GET    /courses/{course_id}
GET    /courses/{course_id}/roadmap

POST   /assessment/start          ?course_id=...
POST   /assessment/submit

GET    /lessons/{lesson_id}
POST   /lessons/{lesson_id}/complete

GET    /quizzes/{quiz_id}
POST   /quizzes/{quiz_id}/submit

GET    /progress/{course_id}
GET    /analytics/{course_id}

POST   /roadmap/adapt
```

## Running it locally

### 1. Database

```bash
docker run --name course-builder-db \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=ai_course_builder \
  -p 5432:5432 -d postgres:16
```

### 2. Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env: set DATABASE_URL, a real SECRET_KEY, and (optionally)
# OPENAI_API_KEY + OPENAI_MODEL. Leave USE_MOCK_AI=true (or leave
# OPENAI_API_KEY blank) to run the whole app without calling OpenAI.

uvicorn app.main:app --reload --port 8000
```

API docs: `http://localhost:8000/docs`.

### 3. Frontend

```bash
cd frontend
npm install
cp .env.example .env      # defaults to VITE_API_URL=http://localhost:8000
npm run dev
```

App: `http://localhost:5173`.

### 4. Walk through it

1. Register an account, land on the dashboard.
2. **+ New course** — set a topic, levels, study time, target date, and
   learning style.
3. On the course page, **Start assessment** — answer the diagnostic
   questions. Submitting runs the Planning Agent immediately and
   generates your full module/lesson roadmap.
4. Open the first lesson — its content is generated on the spot (or
   served from cache if you've opened it before).
5. Complete every lesson in a module — the module's quiz is created, and
   you're prompted to take it.
6. Submit the quiz. Score below 60% adds revision lessons back into the
   module and reopens it; above 85% unlocks fast-tracking; in between,
   you just move on. Try both — worth reloading the roadmap after each to
   see the change.
7. Check **View analytics** on the course page: quiz scores over time,
   daily lesson/quiz activity, and strong/weak topics, all via Recharts.

## Testing notes

There's no formal test suite (not asked for), but the backend pipeline
was exercised end-to-end with `USE_MOCK_AI=true` against a live running
server — register → create course → assessment start/submit → roadmap
generation → lazy lesson content generation → complete every lesson in a
module → lazy quiz generation → submit (both a failing and a passing
attempt, to hit both the `revise` and `fast_track` adaptive paths) →
progress → analytics → manual `/roadmap/adapt`. The frontend was verified
with `npm run build` after every phase. A few real bugs were caught and
fixed this way (not just left as "should work"):

- A mock roadmap generator could produce a per-lesson time estimate over
  the schema's 180-minute cap when the study budget was large.
- `model_dump()` on an agent's Pydantic output kept live enum members,
  which don't JSON-serialize — needed `model_dump(mode="json")` before
  writing to a JSON column.
- A freshly-constructed `LearningAnalytics` row's `lessons_completed`
  column default isn't applied until the session flushes, so `row.x += 1`
  on a brand-new row raised a `TypeError` — fixed by setting the field
  explicitly at construction time.
- The original `passlib` + `bcrypt` pairing (Phase 1) is broken on
  current `bcrypt` releases; swapped to calling `bcrypt` directly.

## What's next

The app is functionally complete against the original spec. Natural next
steps if you keep building: Alembic migrations instead of
`create_all`, pgvector-backed search over past lesson content, WebSocket
or polling-based "generating your roadmap..." progress instead of a
blocking request, and an LLM-graded path for descriptive/coding quiz
answers (currently graded with a text-similarity heuristic rather than a
second model call per answer).
