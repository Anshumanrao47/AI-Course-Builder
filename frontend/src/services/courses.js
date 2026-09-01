/**
 * Course-related API calls, kept separate from the raw axios instance so
 * pages don't need to know endpoint shapes.
 */
import api from "./api.js";

export function createCourse(payload) {
  return api.post("/courses/create", payload).then((res) => res.data);
}

export function listCourses() {
  return api.get("/courses").then((res) => res.data);
}

export function getCourse(courseId) {
  return api.get(`/courses/${courseId}`).then((res) => res.data);
}
