export const keywordMap = {
  admission: 'https://applynow.niet.co.in/',
  admissions: 'https://applynow.niet.co.in/',
  fee: 'https://www.niet.co.in/fees/',
  fees: 'https://www.niet.co.in/fees/',
  course: 'https://www.niet.co.in/courses/',
  courses: 'https://www.niet.co.in/courses/',
  cse: 'https://www.niet.co.in/course/b-tech-in-cse',
  cse_r: 'https://www.niet.co.in/course/b-tech-in-cse-regional',
  ds: 'https://www.niet.co.in/course/b-tech-in-cse-data-science',
  ece: 'https://www.niet.co.in/course/btech-ece',
  ai: 'https://www.niet.co.in/course/btech-in-cse-artificial-intelligence',
  aiml: 'https://www.niet.co.in/course/btech-aiml',
  placement: 'https://www.niet.co.in/placement/placement-records'
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