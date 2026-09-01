/**
 * Assessment / roadmap / lesson / quiz / progress / analytics API calls.
 */
import api from "./api.js";

export function startAssessment(courseId) {
  return api.post("/assessment/start", null, { params: { course_id: courseId } }).then((r) => r.data);
}

export function submitAssessment(payload) {
  return api.post("/assessment/submit", payload).then((r) => r.data);
}

export function getRoadmap(courseId) {
  return api.get(`/courses/${courseId}/roadmap`).then((r) => r.data);
}

export function getLesson(lessonId) {
  return api.get(`/lessons/${lessonId}`).then((r) => r.data);
}

export function completeLesson(lessonId) {
  return api.post(`/lessons/${lessonId}/complete`).then((r) => r.data);
}

export function getQuiz(quizId) {
  return api.get(`/quizzes/${quizId}`).then((r) => r.data);
}

export function submitQuiz(quizId, answers) {
  return api.post(`/quizzes/${quizId}/submit`, { answers }).then((r) => r.data);
}

export function getProgress(courseId) {
  return api.get(`/progress/${courseId}`).then((r) => r.data);
}

export function getAnalytics(courseId) {
  return api.get(`/analytics/${courseId}`).then((r) => r.data);
}

export function adaptRoadmap(courseId) {
  return api.post("/roadmap/adapt", { course_id: courseId }).then((r) => r.data);
}
