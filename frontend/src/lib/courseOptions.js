/**
 * Shared display labels for the enums defined on the backend
 * (app/models/enums.py). Keep these in sync with that file.
 */
export const SKILL_LEVELS = [
  { value: "beginner", label: "Beginner" },
  { value: "intermediate", label: "Intermediate" },
  { value: "advanced", label: "Advanced" },
];

export const LEARNING_STYLES = [
  { value: "visual", label: "Visual (diagrams, videos, illustrated examples)" },
  { value: "reading_writing", label: "Reading & writing (text explanations, notes)" },
  { value: "hands_on", label: "Hands-on (exercises and projects first)" },
  { value: "mixed", label: "Mixed" },
];

export const COURSE_STATUS_LABELS = {
  pending_assessment: "Awaiting skill assessment",
  assessing: "Assessment in progress",
  active: "In progress",
  completed: "Completed",
  archived: "Archived",
};

export function skillLevelLabel(value) {
  return SKILL_LEVELS.find((l) => l.value === value)?.label || value;
}

export function learningStyleLabel(value) {
  return LEARNING_STYLES.find((s) => s.value === value)?.label || value;
}
