export const keywordMap = {
  admission: 'https://www.niet.co.in/admissions/',
  admissions: 'https://www.niet.co.in/admissions/',
  fee: 'https://www.niet.co.in/fees/',
  fees: 'https://www.niet.co.in/fees/',
  contact: 'https://www.niet.co.in/contact/',
  course: 'https://www.niet.co.in/courses/',
  courses: 'https://www.niet.co.in/courses/',
  ai: 'https://www.niet.co.in/courses/ai-ml/',
  aiml: 'https://www.niet.co.in/courses/ai-ml/',
  hostel: 'https://www.niet.co.in/facilities/hostel/',
  placement: 'https://www.niet.co.in/placements/'
};

export function findLinkForText(text) {
  if (!text) return null;
  const t = text.toLowerCase();
  for (const key in keywordMap) {
    const re = new RegExp(`\\b${key}\\b`, 'i');
    if (re.test(t)) return keywordMap[key];
  }
  return null;
}