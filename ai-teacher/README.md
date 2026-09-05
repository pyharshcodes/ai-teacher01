# Pathshala AI — AI Teacher

A human-like AI teacher that turns any topic or uploaded document (PDF, DOCX,
PPTX, TXT) into a personalized, spoken, avatar-led video lesson — with
checkpoint questions, misconception detection, adaptive re-teaching, a final
quiz, and a learning report.

Built for the **AI Innovation Hackathon 2026 — "AI Teacher" challenge**.

---

## 1. What's inside

```
ai-teacher/
├── app.py                     Flask backend / API routes
├── requirements.txt
├── .env.example                Copy to .env and paste your API keys
├── modules/
│   ├── document_processor.py   Extracts text from PDF/DOCX/PPTX/TXT
│   ├── rag_engine.py           TF-IDF based retrieval (knowledge grounding)
│   ├── llm_engine.py           Lesson planning, evaluation, adaptation (Groq)
│   ├── tts_engine.py           Text-to-speech (gTTS free / ElevenLabs optional)
│   ├── video_generator.py      Renders the talking-avatar teaching video
│   └── quiz_engine.py          MCQ grading helper
├── templates/index.html         Single-page frontend
├── static/css/style.css
├── static/js/main.js
├── uploads/                     Uploaded learning material (runtime)
└── static/generated/            Generated audio/video (runtime)
```

## 2. How it maps to the assessment's Understand → Plan → Explain →
Question → Evaluate → Adapt loop

| Step | Where it happens |
|---|---|
| Understand | `/api/upload` (RAG indexing) + the level/time/language/style form |
| Plan | `llm_engine.generate_lesson_plan()` → structured JSON lesson |
| Explain | `tts_engine` + `video_generator` render each segment as a video |
| Question | Each segment carries a `checkpoint_question` |
| Evaluate | `llm_engine.evaluate_answer()` detects the specific misconception |
| Adapt | A fresh re-explanation + difficulty adjustment is returned and shown |
| Continue | `/api/segment_media` advances through segments, then `/api/final_quiz` |


## 3. Setup

```bash
cd ai-teacher
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Open `.env` and paste your keys:

```
GROQ_API_KEY=your_key_here          # required for real lesson generation
ELEVENLABS_API_KEY=                 # optional, better voice
```

Get a **free** Groq key (no card needed) at https://console.groq.com — this
powers lesson planning, misconception detection, and adaptive teaching.

**No key? The app still runs.** Without `GROQ_API_KEY` it automatically
switches to `LOCAL_MODE`: a rule-based lesson planner and evaluator keep the
whole flow (upload → lesson → video → checkpoint → quiz → report) working
end-to-end, so a demo never breaks — it just teaches less richly.

## 4. Run

```bash
python app.py
```

Open **http://localhost:5000**

## 5. Using it

1. Type a topic (or upload a PDF/DOCX/PPTX and then type the chapter/topic
   you want taught — the app will ground the lesson in your material).
2. Choose your level, time available, language, and teaching style.
3. Click **Start the lesson** — the AI plans a multi-segment lesson and
   renders the first segment as a video with a talking avatar and captions.
4. Answer the checkpoint question after each segment — the AI detects
   misconceptions and re-explains before moving on.
5. Ask follow-up questions any time during the lesson.
6. After the last segment, take the final assessment.
7. Get a learning report: score, strong areas, weak areas, and what to
   revise next.

## 6. Swapping in premium APIs later

- **Better voice** — add `ELEVENLABS_API_KEY` in `.env`. `tts_engine.py`
  automatically prefers it over the free gTTS fallback.
- **Photorealistic avatar video** — add `HEYGEN_API_KEY` or `DID_API_KEY` in
  `.env`, then implement the stub functions `_render_with_heygen()` /
  `_render_with_did()` at the bottom of `modules/video_generator.py` and
  call one of them from `render_lesson_video()` instead of the local
  PIL/moviepy renderer. Nothing else in the app needs to change.
- **Semantic RAG** — `modules/rag_engine.py` currently uses TF-IDF for
  speed and zero-dependency-risk. Swap `TfidfVectorizer` for a
  `sentence-transformers` embedding model + a vector DB (e.g. ChromaDB) if
  you want semantic (not just keyword) retrieval.

## 7. Known limitations (be upfront about these in your documentation)

- The built-in avatar is a clean, programmatically-animated illustration
  (not a photorealistic video-generated face) — this keeps the whole
  pipeline free and dependency-light. Swap in HeyGen/D-ID for
  photorealism (see above).
- RAG uses TF-IDF keyword relevance rather than deep semantic embeddings.
- Lesson state is kept in-memory per Flask process — fine for a demo,
  swap for a database for multi-user production use.
- gTTS requires an internet connection at generation time (it calls
  Google's TTS endpoint); fully offline speech would need a local TTS
  model such as Coqui TTS.

## 8. Troubleshooting

- **`groq.NotFoundError: model_not_found` / "The model ... does not
  exist"** — Groq periodically retires older models. This project defaults
  to `openai/gpt-oss-120b`. If that ever gets deprecated too, check
  https://console.groq.com/docs/models for the current production model
  list and set `GROQ_MODEL=<new-model-id>` in your `.env` file, then
  restart `python app.py`.

- **`pip install` fails trying to build numpy/scipy from source (e.g. "NumPy
  requires GCC >= 8.4" on Windows)** — this happens when pip can't find a
  prebuilt wheel for your exact Python version and tries to compile from
  source. `requirements.txt` already uses minimum-version constraints
  (`numpy>=1.26`, not `numpy==1.26.4`) specifically to avoid this — make sure
  you're installing from the `requirements.txt` included in this zip. If it
  still happens, upgrade pip first (`python -m pip install --upgrade pip`)
  and try again; very new Python releases sometimes need a few weeks before
  every package has wheels published for them.

- **`moviepy`/ffmpeg errors on first run** — moviepy needs `ffmpeg`; the
  `imageio-ffmpeg` package (already in `requirements.txt`) auto-downloads a
  bundled ffmpeg binary the first time you render a video, so make sure you
  have an internet connection the first time you run a lesson.
- **gTTS "no internet" error** — gTTS calls Google's servers; check your
  connection, or add an `ELEVENLABS_API_KEY` instead.
- **Lesson feels generic** — add `GROQ_API_KEY`; local/offline mode uses a
  simple template so the demo never crashes without a key.
