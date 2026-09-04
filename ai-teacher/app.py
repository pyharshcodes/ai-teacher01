"""
AI Teacher - Flask backend
===========================
Implements the full Understand -> Plan -> Explain -> Question -> Evaluate ->
Adapt -> Continue loop from the assessment brief, end to end:

  0. /api/status           - is the real AI engine actually working right now?
  1. /api/upload            - process uploaded learning material (RAG indexing)
  2. /api/create_lesson     - generate a personalized, structured lesson plan
  3. /api/segment_media     - render narration audio + a talking-avatar video
                              for one lesson segment
  4. /api/checkpoint        - evaluate a student's answer mid-lesson, detect
                              misconceptions, and adapt
  5. /api/followup          - answer a free-form follow-up question in context
  6. /api/final_quiz        - fetch the end-of-lesson assessment
  7. /api/submit_quiz       - grade the assessment and generate a learning report

Run:  python app.py   (see README.md for full setup)
"""

import os
import uuid
import traceback
from flask import Flask, request, jsonify, render_template, session, url_for
from dotenv import load_dotenv

from modules import document_processor, rag_engine, llm_engine, tts_engine
from modules import video_generator, quiz_engine

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-change-me")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
AUDIO_DIR = os.path.join(BASE_DIR, "static", "generated", "audio")
VIDEO_DIR = os.path.join(BASE_DIR, "static", "generated", "video")
for d in (UPLOAD_DIR, AUDIO_DIR, VIDEO_DIR):
    os.makedirs(d, exist_ok=True)

ALLOWED_EXT = {".pdf", ".docx", ".pptx", ".txt", ".md"}

# In-memory lesson state per session (fine for a hackathon demo; swap for a
# real DB / Redis for production use).
LESSONS = {}


def get_session_id():
    if "session_id" not in session:
        session["session_id"] = uuid.uuid4().hex
    return session["session_id"]


def error_response(e, code=500):
    app.logger.error(traceback.format_exc())
    return jsonify({"ok": False, "error": str(e)}), code


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    get_session_id()
    return render_template("index.html", local_mode=llm_engine.LOCAL_MODE)


# ---------------------------------------------------------------------------
# 0. Honest AI status - so "AI doesn't work" is never a silent mystery
# ---------------------------------------------------------------------------
@app.route("/api/status", methods=["GET"])
def status():
    return jsonify({"ok": True, **llm_engine.get_status()})


# ---------------------------------------------------------------------------
# 1. Upload + RAG indexing
# ---------------------------------------------------------------------------
@app.route("/api/upload", methods=["POST"])
def upload():
    try:
        sid = get_session_id()
        if "file" not in request.files:
            return jsonify({"ok": False, "error": "No file provided"}), 400

        file = request.files["file"]
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in ALLOWED_EXT:
            return jsonify({"ok": False, "error": f"Unsupported file type {ext}"}), 400

        save_path = os.path.join(UPLOAD_DIR, f"{sid}_{uuid.uuid4().hex}{ext}")
        file.save(save_path)

        text = document_processor.extract_text(save_path)
        if not text.strip():
            return jsonify({
                "ok": False,
                "error": "No readable text was found in this file (it may be a scanned/image-only document).",
            }), 400

        chunks = document_processor.chunk_text(text)

        store = rag_engine.get_or_create_store(sid)
        store.index(chunks)

        return jsonify({
            "ok": True,
            "filename": file.filename,
            "characters_extracted": len(text),
            "chunks_indexed": len(chunks),
        })
    except Exception as e:
        return error_response(e)


# ---------------------------------------------------------------------------
# 2. Lesson planning
# ---------------------------------------------------------------------------
@app.route("/api/create_lesson", methods=["POST"])
def create_lesson():
    try:
        sid = get_session_id()
        data = request.get_json(force=True)

        topic = (data.get("topic") or "").strip()
        level = data.get("level", "beginner")
        minutes = int(data.get("minutes", 20))
        language = data.get("language", "English")
        style = data.get("style", "simple with examples")

        if not topic:
            return jsonify({"ok": False, "error": "Please provide a topic (or upload material and name its main topic)."}), 400

        store = rag_engine.get_or_create_store(sid)
        context_chunks = store.retrieve(topic, top_k=4) if store.has_material() else []

        plan, engine = llm_engine.generate_lesson_plan(topic, level, minutes, language, style, context_chunks)

        LESSONS[sid] = {
            "topic": topic,
            "language": language,
            "level": level,
            "plan": plan,
            "results": [],
            "taught_so_far": [],
        }

        return jsonify({
            "ok": True,
            "plan": plan,
            "engine": engine,              # "groq" (real AI) or "fallback" (offline template)
            "local_mode": llm_engine.LOCAL_MODE,
        })
    except Exception as e:
        return error_response(e)


# ---------------------------------------------------------------------------
# 3. Segment media (audio + avatar video)
# ---------------------------------------------------------------------------
@app.route("/api/segment_media", methods=["POST"])
def segment_media():
    try:
        sid = get_session_id()
        data = request.get_json(force=True)
        idx = int(data.get("segment_index", 0))

        lesson = LESSONS.get(sid)
        if not lesson:
            return jsonify({"ok": False, "error": "No active lesson. Create a lesson first."}), 400

        segments = lesson["plan"].get("segments", [])
        if idx < 0 or idx >= len(segments):
            return jsonify({"ok": False, "error": "Invalid segment index"}), 400

        seg = segments[idx]
        narration = f"{seg.get('heading', '')}. {seg.get('explanation', '')} For example, {seg.get('example', '')}"

        # Audio and video are generated as two independent steps. If video
        # rendering fails (e.g. ffmpeg not available in this environment),
        # the student still gets narrated audio + captions instead of a
        # completely dead segment - a real, labelled degradation, not a fake
        # success.
        audio_url = None
        video_url = None
        media_warning = None

        try:
            audio_path = tts_engine.synthesize(narration, lesson["language"], AUDIO_DIR)
            audio_url = url_for("static", filename=f"generated/audio/{os.path.basename(audio_path)}")
            duration = video_generator.get_audio_duration(audio_path)
            captions = video_generator.build_caption_segments(narration, duration)
        except Exception as e:
            app.logger.error("Audio generation failed: %s", traceback.format_exc())
            return jsonify({
                "ok": False,
                "error": f"Could not generate narration audio: {e}. Check your internet connection (gTTS needs one) or set ELEVENLABS_API_KEY.",
            }), 502

        try:
            video_path = video_generator.render_lesson_video(
                audio_path, captions, seg.get("heading", ""), seg.get("visual_hint", ""), VIDEO_DIR
            )
            video_url = url_for("static", filename=f"generated/video/{os.path.basename(video_path)}")
        except Exception as e:
            app.logger.error("Video generation failed: %s", traceback.format_exc())
            media_warning = f"Video could not be rendered ({e}); playing audio only."

        lesson["taught_so_far"].append(f"{seg.get('heading')}: {seg.get('explanation')}")

        return jsonify({
            "ok": True,
            "video_url": video_url,
            "audio_url": audio_url,
            "captions": captions,
            "media_warning": media_warning,
            "heading": seg.get("heading"),
            "explanation": seg.get("explanation"),
            "example": seg.get("example"),
            "visual_type": seg.get("visual_type"),
            "visual_hint": seg.get("visual_hint"),
            "checkpoint_question": seg.get("checkpoint_question"),
            "question_type": seg.get("question_type"),
            "segment_number": idx + 1,
            "total_segments": len(segments),
            "is_last_segment": idx == len(segments) - 1,
        })
    except Exception as e:
        return error_response(e)


# ---------------------------------------------------------------------------
# 4. Checkpoint answer evaluation (misconception detection + adaptation)
# ---------------------------------------------------------------------------
@app.route("/api/checkpoint", methods=["POST"])
def checkpoint():
    try:
        sid = get_session_id()
        data = request.get_json(force=True)
        idx = int(data.get("segment_index", 0))
        student_answer = data.get("answer", "")

        lesson = LESSONS.get(sid)
        if not lesson:
            return jsonify({"ok": False, "error": "No active lesson."}), 400

        segments = lesson["plan"].get("segments", [])
        seg = segments[idx] if 0 <= idx < len(segments) else {}
        question = seg.get("checkpoint_question") or ""
        context = seg.get("explanation", "")

        result, engine = llm_engine.evaluate_answer(question, student_answer, context, lesson["language"])
        lesson["results"].append({
            "question": question,
            "is_correct": bool(result.get("is_correct")),
            "misconception": result.get("misconception"),
        })

        return jsonify({"ok": True, "engine": engine, **result})
    except Exception as e:
        return error_response(e)


# ---------------------------------------------------------------------------
# 5. Follow-up Q&A during the lesson
# ---------------------------------------------------------------------------
@app.route("/api/followup", methods=["POST"])
def followup():
    try:
        sid = get_session_id()
        data = request.get_json(force=True)
        question = (data.get("question") or "").strip()

        lesson = LESSONS.get(sid)
        if not lesson:
            return jsonify({"ok": False, "error": "No active lesson."}), 400
        if not question:
            return jsonify({"ok": False, "error": "Empty question."}), 400

        context = "\n".join(lesson["taught_so_far"])
        answer, engine = llm_engine.answer_followup(question, context, lesson["language"])
        return jsonify({"ok": True, "answer": answer, "engine": engine})
    except Exception as e:
        return error_response(e)


# ---------------------------------------------------------------------------
# 6 & 7. Final assessment + report
# ---------------------------------------------------------------------------
@app.route("/api/final_quiz", methods=["GET"])
def final_quiz():
    try:
        sid = get_session_id()
        lesson = LESSONS.get(sid)
        if not lesson:
            return jsonify({"ok": False, "error": "No active lesson."}), 400
        questions = lesson["plan"].get("final_assessment", {}).get("questions", [])
        return jsonify({"ok": True, "questions": questions})
    except Exception as e:
        return error_response(e)


@app.route("/api/submit_quiz", methods=["POST"])
def submit_quiz():
    try:
        sid = get_session_id()
        data = request.get_json(force=True)
        answers = data.get("answers", [])

        lesson = LESSONS.get(sid)
        if not lesson:
            return jsonify({"ok": False, "error": "No active lesson."}), 400

        results = list(lesson["results"])  # include checkpoint results too
        for a in answers:
            q = a.get("question", "")
            qtype = a.get("type", "short_answer")
            student = a.get("student_answer", "")
            correct_answer = a.get("correct_answer", "")

            if qtype == "mcq":
                is_correct = quiz_engine.grade_mcq({"correct_answer": correct_answer}, student)
                misconception = None if is_correct else f"Selected option differs from expected: {correct_answer}"
            else:
                eval_result, _engine = llm_engine.evaluate_answer(q, student, correct_answer, lesson["language"])
                is_correct = bool(eval_result.get("is_correct"))
                misconception = eval_result.get("misconception")

            results.append({"question": q, "is_correct": is_correct, "misconception": misconception})

        report = llm_engine.generate_report(lesson["topic"], results)
        return jsonify({"ok": True, "report": report})
    except Exception as e:
        return error_response(e)


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "true").lower() != "false"
    print("=" * 60)
    status = llm_engine.get_status()
    if status["local_mode"]:
        print("⚠  AI ENGINE: OFFLINE (no working GROQ_API_KEY found).")
        print("   Lessons will use the basic rule-based template, not real AI.")
        print("   Fix: put GROQ_API_KEY=<your key> in a .env file next to")
        print("   app.py, then restart this server.")
    else:
        print(f"✅ AI ENGINE: configured with model '{status['model']}'.")
        print("   (Errors on individual requests, if any, will be logged below")
        print("   and also visible at GET /api/status.)")
    print("=" * 60)
    app.run(host="0.0.0.0", port=port, debug=debug)
