import { Route, Routes } from "react-router-dom";
import Navbar from "./components/Navbar.jsx";
import ProtectedRoute from "./components/ProtectedRoute.jsx";
import Landing from "./pages/Landing.jsx";
import Login from "./pages/Login.jsx";
import Register from "./pages/Register.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import CourseCreate from "./pages/CourseCreate.jsx";
import CourseDetail from "./pages/CourseDetail.jsx";
import Assessment from "./pages/Assessment.jsx";
import Lesson from "./pages/Lesson.jsx";
import Quiz from "./pages/Quiz.jsx";
import Analytics from "./pages/Analytics.jsx";

export default function App() {
  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-1">
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/courses/new"
            element={
              <ProtectedRoute>
                <CourseCreate />
              </ProtectedRoute>
            }
          />
          <Route
            path="/courses/:courseId"
            element={
              <ProtectedRoute>
                <CourseDetail />
              </ProtectedRoute>
            }
          />
          <Route
            path="/courses/:courseId/assessment"
            element={
              <ProtectedRoute>
                <Assessment />
              </ProtectedRoute>
            }
          />
          <Route
            path="/courses/:courseId/analytics"
            element={
              <ProtectedRoute>
                <Analytics />
              </ProtectedRoute>
            }
          />
          <Route
            path="/lessons/:lessonId"
            element={
              <ProtectedRoute>
                <Lesson />
              </ProtectedRoute>
            }
          />
          <Route
            path="/quizzes/:quizId"
            element={
              <ProtectedRoute>
                <Quiz />
              </ProtectedRoute>
            }
          />
        </Routes>
      </main>
    </div>
  );
}
