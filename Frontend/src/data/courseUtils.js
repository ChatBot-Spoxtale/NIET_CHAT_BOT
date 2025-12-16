import baseKnowledge from "../../RAG/data/base_knowledge.json";

export const getCoursesByCategory = (type) => {
  const courses = Object.values(baseKnowledge.courses || {});

  if (type === "UG") {
    return courses.filter(c =>
      c.course_name.startsWith("B.") ||
      c.course_name.startsWith("Bachelor")
    );
  }

  if (type === "PG") {
    return courses.filter(c =>
      c.course_name.startsWith("M.") ||
      c.course_name.startsWith("Master")
    );
  }

  if (type === "TWINNING") {
    return courses.filter(c =>
      c.course_name.toLowerCase().includes("twinning")
    );
  }

  return [];
};

export const getFeesByCourse = (courseName) =>
  baseKnowledge.fees?.[courseName] || null;
