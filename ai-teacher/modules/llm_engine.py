"""
llm_engine.py
--------------
The "brain" of the AI Teacher. Wraps Groq's free-tier LLM API and implements
the Understand -> Plan -> Explain -> Question -> Evaluate -> Adapt loop
required by the assessment.

If no GROQ_API_KEY is set, the app still runs end-to-end using a rule-based
offline fallback (LOCAL_MODE) so the prototype is never "broken" during a
demo - it just teaches less richly without a key.

IMPORTANT for debugging "AI doesn't work": call get_status() - it tells you
exactly whether a real key was found, which model is configured, and (after
the first request) the last real error the Groq API returned. Do not guess;
check this.
"""

import os
import json
import re
import time
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
# openai/gpt-oss-120b is Groq's current production general-purpose model.
# Override via GROQ_MODEL in .env if Groq's lineup changes again later.
GROQ_MODEL = os.getenv("GROQ_MODEL", "").strip() or "openai/gpt-oss-120b"

_client = None
_init_error = None
if GROQ_API_KEY:
    try:
        from groq import Groq
        _client = Groq(api_key=GROQ_API_KEY)
    except Exception as e:
        _client = None
        _init_error = str(e)

LOCAL_MODE = _client is None

# The single source of truth for "is the AI actually working right now".
# Updated on every real call so the frontend/status endpoint can show the
# TRUE state instead of just "a key exists".
_last_error = _init_error
_last_success_ts = None


def get_status():
    """Used by /api/status so the UI can show a real, honest banner instead
    of silently teaching from the offline template."""
    return {
        "local_mode": LOCAL_MODE,
        "has_key": bool(GROQ_API_KEY),
        "model": GROQ_MODEL,
        "last_error": _last_error,
        "ever_succeeded": _last_success_ts is not None,
    }


def _chat(messages, temperature=0.4, json_mode=False):
    """Low-level call to Groq. Raises if LOCAL_MODE - callers should check first."""
    global _last_error, _last_success_ts
    kwargs = dict(model=GROQ_MODEL, messages=messages, temperature=temperature)
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}
    try:
        resp = _client.chat.completions.create(**kwargs)
        _last_success_ts = time.time()
        _last_error = None
        return resp.choices[0].message.content
    except Exception as e:
        # Surface the REAL error (model name typo, invalid key, rate limit,
        # etc.) instead of swallowing it - this is what you should read if
        # "AI doesn't work" even though a key is set.
        _last_error = f"{type(e).__name__}: {e}"
        raise


def _extract_json(raw: str):
    """Best-effort JSON extraction in case the model wraps JSON in prose/fences."""
    raw = raw.strip()
    raw = re.sub(r"^```(json)?", "", raw).strip()
    raw = re.sub(r"```$", "", raw).strip()
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if match:
        raw = match.group(0)
    return json.loads(raw)


def _chat_json_with_retry(system, user, temperature=0.5):
    """Calls the model expecting JSON; if parsing fails, asks once more with
    a stricter instruction before giving up."""
    raw = _chat(
        [{"role": "system", "content": system}, {"role": "user", "content": user}],
        temperature=temperature,
        json_mode=True,
    )
    try:
        return _extract_json(raw)
    except Exception:
        pass

    # Retry once - some models occasionally add stray prose even in JSON mode.
    retry_user = user + "\n\nSTRICT: reply with ONLY the JSON object. No prose, no markdown fences."
    raw2 = _chat(
        [{"role": "system", "content": system}, {"role": "user", "content": retry_user}],
        temperature=0.1,
        json_mode=True,
    )
    return _extract_json(raw2)


def num_questions_for(minutes: int, level: str) -> int:
    """How many final-assessment questions a session should have. Scales with
    time available and depth expected at the learner's level - never a fixed
    3-4 regardless of session length."""
    minutes = max(1, int(minutes or 20))
    base = round(minutes / 4)
    level_bonus = {"beginner": 0, "intermediate": 2, "advanced": 4}.get((level or "").lower(), 0)
    return max(4, min(15, base + level_bonus))


# ---------------------------------------------------------------------------
# 1. LESSON PLANNING  (Understand -> Plan)
# ---------------------------------------------------------------------------
def generate_lesson_plan(topic, level, minutes, language, style, context_chunks):
    context_text = "\n---\n".join(c["text"] for c in context_chunks) if context_chunks else ""
    n_questions = num_questions_for(minutes, level)

    if LOCAL_MODE:
        return _fallback_lesson_plan(topic, level, minutes, language, n_questions), "fallback"

    system = (
        "You are an expert human-like AI teacher. You design short, structured, "
        "personalized lessons the way a great real teacher plans a class: "
        "understand the learner, break the topic into a logical sequence of "
        "segments, decide where to insert questions, and pick suitable examples "
        "and visual types for each segment. You never behave like a plain Q&A "
        "chatbot - you actively teach."
    )

    grounding = (
        f"Ground your lesson in the following material extracted from the "
        f"student's uploaded document. Prefer facts and examples from this "
        f"material; do not invent facts that contradict it:\n{context_text}\n"
        if context_text else
        "No material was uploaded - teach the topic from general knowledge, "
        "clearly structured for the learner's level."
    )

    n_segments = max(3, min(8, round(int(minutes or 20) / 4)))

    user = f"""
Design a lesson with these parameters:
- Topic: {topic}
- Learner level: {level}
- Available time: {minutes} minutes
- Teaching language: {language}
- Preferred style: {style}

{grounding}

Return STRICT JSON with this exact shape:
{{
  "title": "string",
  "learning_objectives": ["string", ...],
  "segments": [
    {{
      "heading": "string",
      "explanation": "spoken-style explanation text, 3-6 sentences, in {language}",
      "example": "a concrete example or analogy",
      "visual_type": "one of: equation | graph | diagram | timeline | code | image | none",
      "visual_hint": "short description of what the visual should show",
      "checkpoint_question": "a question to ask the student after this segment, or null if none",
      "question_type": "one of: mcq | short_answer | conceptual | none"
    }}
  ],
  "final_assessment": {{
    "questions": [
      {{"question": "string", "type": "mcq|short_answer", "options": ["..."] or null, "correct_answer": "string"}}
    ]
  }}
}}
Create exactly {n_segments} segments (roughly 1 segment per 3-5 minutes of the {minutes}-minute session).
Create exactly {n_questions} final_assessment questions - this must genuinely evaluate understanding
of every learning objective and segment, not just the first one. Mix mcq and short_answer types.
Respond with JSON only, no extra commentary.
"""
    try:
        data = _chat_json_with_retry(system, user, temperature=0.5)
        # Defensive: if the model ignored the count instructions, pad/trim so
        # the UI's "N questions" promise is always kept.
        data = _normalize_plan_question_count(data, n_questions, topic)
        return data, "groq"
    except Exception:
        return _fallback_lesson_plan(topic, level, minutes, language, n_questions), "fallback"


def _normalize_plan_question_count(data, n_questions, topic):
    qs = (data.get("final_assessment") or {}).get("questions") or []
    if len(qs) < n_questions:
        objectives = data.get("learning_objectives") or [topic]
        i = 0
        while len(qs) < n_questions:
            obj = objectives[i % len(objectives)]
            qs.append({
                "question": f"In your own words, explain: {obj}",
                "type": "short_answer",
                "options": None,
                "correct_answer": obj,
            })
            i += 1
    elif len(qs) > n_questions:
        qs = qs[:n_questions]
    data.setdefault("final_assessment", {})["questions"] = qs
    return data


def _fallback_lesson_plan(topic, level, minutes, language, n_questions):
    """Rule-based lesson so the app still works with zero API keys. Clearly
    marked as 'fallback' by the caller - never presented as if it were a
    real AI-generated lesson."""
    n_segments = max(3, min(6, round(int(minutes or 20) / 5)))
    stage_names = [
        "What is {t}?", "How {t} works", "A worked example",
        "Common mistakes with {t}", "Where {t} is used", "Recap",
    ]
    segments = []
    for i in range(n_segments):
        heading = stage_names[i % len(stage_names)].format(t=topic)
        is_recap = heading == "Recap"
        segments.append({
            "heading": heading,
            "explanation": (
                f"Let's continue with {topic}. At a {level} level, we build this "
                f"idea from a few simple pieces, step by step, in {language}."
                if not is_recap else f"Let's recap what we covered about {topic}."
            ),
            "example": f"A concrete example related to {topic}." if not is_recap else "Quick summary of key points.",
            "visual_type": "diagram" if not is_recap else "none",
            "visual_hint": f"A simple labeled diagram for {topic}" if not is_recap else "",
            "checkpoint_question": None if is_recap else f"In your own words, what is the key idea in '{heading}'?",
            "question_type": "none" if is_recap else "short_answer",
        })

    questions = []
    for i in range(n_questions):
        questions.append({
            "question": f"Question {i+1} on {topic}: explain one important idea from this lesson.",
            "type": "short_answer",
            "options": None,
            "correct_answer": f"Any answer showing understanding of {topic}.",
        })

    return {
        "title": f"Introduction to {topic}",
        "learning_objectives": [
            f"Understand the core idea behind {topic}",
            f"See a real example of {topic} in action",
            f"Be able to answer questions about {topic}",
        ],
        "segments": segments,
        "final_assessment": {"questions": questions},
    }


# ---------------------------------------------------------------------------
# 2. ANSWER EVALUATION + MISCONCEPTION DETECTION  (Evaluate -> Adapt)
# ---------------------------------------------------------------------------
def evaluate_answer(question, student_answer, expected_context, language):
    if LOCAL_MODE:
        correct = bool(student_answer) and len(student_answer.strip()) > 3
        return {
            "is_correct": correct,
            "misconception": None if correct else "Answer seems incomplete or unclear.",
            "feedback": (
                "Good attempt! Let's move on." if correct else
                "That's not quite right - let's go over this concept again with a "
                "different example."
            ),
            "re_explanation": None if correct else (
                f"Here is the idea again, explained differently: {expected_context}"
            ),
            "difficulty_adjustment": "same" if correct else "easier",
        }, "fallback"

    system = (
        "You are an experienced, kind teacher evaluating a student's answer. "
        "You do not just mark right/wrong - you diagnose the specific "
        "misconception behind a wrong answer, the way a real teacher would, "
        "and prepare a fresh explanation using a different angle or analogy."
    )
    user = f"""
Question asked: {question}
Student's answer: {student_answer}
Relevant lesson context: {expected_context}
Respond in {language} where natural for explanations.

Return STRICT JSON:
{{
  "is_correct": true/false,
  "misconception": "string describing the specific misunderstanding, or null if correct",
  "feedback": "short, encouraging, constructive feedback sentence",
  "re_explanation": "a fresh explanation using a different analogy, or null if correct",
  "difficulty_adjustment": "one of: easier | same | harder"
}}
JSON only.
"""
    try:
        data = _chat_json_with_retry(system, user, temperature=0.3)
        return data, "groq"
    except Exception:
        return {
            "is_correct": False,
            "misconception": "Could not confidently evaluate - treating as needing review.",
            "feedback": "Let's review this concept once more.",
            "re_explanation": expected_context,
            "difficulty_adjustment": "same",
        }, "fallback"


# ---------------------------------------------------------------------------
# 3. FOLLOW-UP QUESTIONS (context-aware chat during the lesson)
# ---------------------------------------------------------------------------
def answer_followup(question, lesson_context, language):
    if LOCAL_MODE:
        return (
            f"(Offline mode - no GROQ_API_KEY loaded) Based on the lesson so far: "
            f"{lesson_context[:400]} ... Add a real GROQ_API_KEY in .env and restart "
            f"the server for a fully generated answer."
        ), "fallback"
    system = (
        "You are the same AI teacher continuing the lesson. Answer the "
        "student's follow-up question while staying consistent with the "
        "lesson taught so far. Keep it concise and encouraging."
    )
    user = f"Lesson so far:\n{lesson_context}\n\nStudent's follow-up question: {question}\nAnswer in {language}."
    try:
        return _chat(
            [{"role": "system", "content": system}, {"role": "user", "content": user}],
            temperature=0.5,
        ), "groq"
    except Exception as e:
        return f"(AI request failed: {e}) Please try again in a moment.", "error"


# ---------------------------------------------------------------------------
# 4. FINAL REPORT
# ---------------------------------------------------------------------------
def generate_report(topic, results):
    """results: list of {question, is_correct, misconception}"""
    total = len(results) or 1
    correct = sum(1 for r in results if r["is_correct"])
    score_pct = round((correct / total) * 100)

    weak = [r["misconception"] for r in results if not r["is_correct"] and r.get("misconception")]
    strong_topics = [r["question"] for r in results if r["is_correct"]]

    return {
        "topic": topic,
        "score_percent": score_pct,
        "correct": correct,
        "total": total,
        "strong_areas": strong_topics[:5],
        "weak_areas": weak[:5] if weak else ["None - great job!"],
        "recommendation": (
            f"Revise: {weak[0]}" if weak else
            f"You're ready to move to the next topic after {topic}."
        ),
        # Raw per-question correctness sequence - used to draw a REAL chart
        # in the report dashboard (not fabricated data).
        "history": [{"correct": bool(r["is_correct"])} for r in results],
    }
