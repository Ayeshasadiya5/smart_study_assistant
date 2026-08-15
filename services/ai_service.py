from config import Config
from services.rag_service import rag_service


class AIService:
    """AI service using the Google Gemini SDK."""

    def __init__(self):
        self.enabled = bool(Config.GEMINI_API_KEY)
        self._client = None

    def _get_client(self):
        if self._client is None and self.enabled:
            try:
                from google import genai

                self._client = genai.Client(
                    api_key=Config.GEMINI_API_KEY
                )

                print("Gemini client created successfully.")

            except Exception as e:
                print(f"Gemini client initialization error: {e}")
                self.enabled = False

        return self._client

    def _build_rag_context(self, search_results):
        if not search_results:
            return ''

        parts = []

        for i, result in enumerate(search_results, 1):
            meta = result.get('metadata', {})

            title = meta.get('title', 'Unknown')
            page = meta.get('page', 'N/A')

            parts.append(
                f'[Source {i}: {title}, Page {page}]\n'
                f'{result["text"]}'
            )

        return '\n\n'.join(parts)

    def _generate(self, system_prompt, user_prompt):
        """Generate a response using Gemini."""

        client = self._get_client()

        if not client:
            return None

        prompt = f"""
SYSTEM INSTRUCTIONS:
{system_prompt}

USER REQUEST:
{user_prompt}
"""

        try:
            response = client.models.generate_content(
                model=Config.GEMINI_MODEL,
                contents=prompt,
            )

            if response and response.text:
                return response.text.strip()

            return ''

        except Exception as e:
            print(f"Gemini generation error: {e}")
            raise

    def chat(
        self,
        question,
        subject_context=None,
        material_id=None,
        web_context=None,
        db_session=None
    ):
        """Answer a student question using Gemini, RAG and web context."""

        if not self.enabled:
            return {
                'answer': (
                    'AI features are currently disabled. '
                    'Please configure GEMINI_API_KEY in your .env file.'
                ),
                'sources': [],
            }

        if not question or not str(question).strip():
            return {
                'answer': 'Please enter a question.',
                'sources': [],
            }

        if not self._get_client():
            return {
                'answer': (
                    'AI service is unavailable. '
                    'Please check your Gemini API configuration.'
                ),
                'sources': [],
            }

        rag_results = []

        if material_id:
            try:
                rag_results = rag_service.search(
                    question,
                    material_ids=[material_id],
                    k=4
                )
            except Exception as e:
                print(f"RAG search error: {e}")
                rag_results = []

        rag_context = self._build_rag_context(rag_results)

        subject_info = ''

        if subject_context:
            subject_info = (
                'Student is studying:\n'
                f'Regulation: {subject_context.get("regulation", "N/A")}\n'
                f'Subject: {subject_context.get("subject", "N/A")}\n'
            )

        combined_context = ''

        if rag_context:
            combined_context += (
                'UPLOADED PDF MATERIAL CONTEXT:\n'
                + rag_context
                + '\n\n'
            )

        if web_context:
            combined_context += (
                'WEB SEARCH STUDY MATERIAL CONTEXT:\n'
                + web_context
                + '\n\n'
            )

        if not combined_context:
            combined_context = (
                'No specific study material context is available. '
                'Use general academic knowledge for this engineering subject.'
            )

        system_prompt = """
You are SmartNotes AI, a focused AI Doubt Assistant for B.Tech students.

Your job is to answer ONLY what the student asks.

IMPORTANT RESPONSE RULES:

1. Give a direct answer to the student's question first.
2. Do NOT generate a complete syllabus, revision guide, or question bank
   unless the student specifically asks for it.
3. Do NOT give information about all units unless requested.
4. Keep answers concise and easy to understand.
5. Use simple student-friendly English.
6. Use headings and bullet points when they improve clarity.
7. For definition questions:
   - Give the definition.
   - Give a simple explanation.
   - Give one example if useful.
8. For comparison questions:
   - Use a table.
9. For programming questions:
   - Give the correct C code.
   - Explain the code briefly.
   - Show sample output when useful.
10. For "2 marks" questions:
    - Give a short exam-ready answer.
11. For "5 marks" questions:
    - Give a structured answer with definition, explanation,
      important points, and example/code if required.
12. For "10 marks" questions:
    - Give a detailed but focused answer with headings,
      explanation, code/diagram/steps when appropriate.
13. If the student asks "what is X?", answer only about X.
14. If the student asks "explain X", explain only X.
15. If the student asks for important questions, then provide
    important questions.
16. If the student asks for unit-wise notes, then provide
    unit-wise notes.
17. Do not assume the student wants information they did not request.
18. Do not repeat the student's question unnecessarily.
19. Do not add unrelated topics.
20. If regulation and subject are provided, use them as context,
    but do not invent regulation-specific syllabus details.

The student's exact question is the highest priority.

Answer in a clear, exam-oriented format.
"""

        user_prompt = f"""
{subject_info}

{combined_context}

STUDENT'S EXACT QUESTION:
{question}

Answer ONLY the student's exact question.

Do not provide a complete unit-wise guide unless the student
explicitly asks for one.

Keep the answer clear, focused, and exam-oriented.

If the question asks for a definition:
Definition:
Simple Explanation:
Example:

If the question asks for a comparison:
Use a comparison table.

If the question asks for a program:
Provide:
1. Logic
2. C Program
3. Explanation
4. Sample Output

If the question asks for a 2-mark answer:
Keep it short.

If the question asks for a 5-mark answer:
Give a moderately detailed structured answer.

If the question asks for a 10-mark answer:
Give a detailed structured answer.

Do not add unrelated topics.
"""

        try:
            answer = self._generate(
                system_prompt,
                user_prompt
            )

            if not answer:
                answer = (
                    'I could not generate an answer. '
                    'Please try again.'
                )

            sources = []

            for result in rag_results:
                meta = result.get('metadata', {})

                sources.append({
                    'title': meta.get('title', 'Unknown'),
                    'page': meta.get('page', 'N/A'),
                })

            return {
                'answer': answer,
                'sources': sources,
            }

        except Exception as e:
            return {
                'answer': (
                    f'AI service encountered an error: {str(e)}'
                ),
                'sources': [],
            }

    def generate_questions(
        self,
        subject_name,
        regulation=None,
        unit=None,
        web_context=None,
        db_session=None
    ):
        """Generate important exam questions."""

        if not self.enabled:
            return {
                'questions': [],
                'error': (
                    'AI features are disabled. '
                    'Configure GEMINI_API_KEY.'
                ),
            }

        if not self._get_client():
            return {
                'questions': [],
                'error': 'AI service unavailable.',
            }

        context = web_context or ''
        unit_text = f' - {unit}' if unit else ''
        reg_text = regulation or 'N/A'

        prompt = f"""
Generate important exam preparation questions for the
engineering subject.

Subject: {subject_name}
Regulation: {reg_text}{unit_text}

Study Material Context:
{context if context else 'No specific materials found.'}

Generate:

1. 3 two-mark questions
2. 3 five-mark questions
3. 2 ten-mark questions
4. Important topics for the exam
5. 5 additional short exam-oriented questions

Make the questions suitable for B.Tech / Engineering students.

Format the response clearly with headings and numbered lists.
"""

        try:
            system_prompt = (
                'You are an AI exam preparation assistant '
                'for B.Tech engineering students. '
                'Generate useful, clear and exam-oriented questions.'
            )

            questions = self._generate(
                system_prompt,
                prompt
            )

            return {
                'questions': questions or 'No questions generated.',
                'error': None,
            }

        except Exception as e:
            return {
                'questions': [],
                'error': str(e),
            }


ai_service = AIService()