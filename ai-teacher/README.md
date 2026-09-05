# 🎓 AI Teacher

**An AI-powered virtual teacher that transforms any topic or uploaded learning material into a personalized, spoken, avatar-led learning experience.**

AI Teacher doesn't just generate an explanation. It creates a complete learning loop — **teach → check understanding → detect misconceptions → re-teach → assess → report**.

Built for the **AI Innovation Hackathon 2026 — AI Teacher Challenge**.

---

## 🎯 Problem

Most AI learning tools behave like chatbots: they answer questions, generate explanations, or create quizzes when asked.

However, effective teaching requires more than providing information. A teacher needs to:

* Understand the learner's level and learning preferences
* Structure the topic into an understandable lesson
* Explain concepts clearly
* Check whether the learner actually understood
* Identify misconceptions
* Re-teach difficult concepts
* Evaluate learning progress

AI Teacher is designed to automate this complete teaching cycle.

---

## 💡 Our Solution

AI Teacher converts a **topic or uploaded learning material** into an interactive, personalized lesson.

The learner can provide a topic or upload **PDF, DOCX, PPTX, or TXT** material, then select their:

* Learning level
* Available time
* Preferred language
* Teaching style

The system generates a structured lesson and delivers it through **spoken, avatar-led video segments**.

After each segment, checkpoint questions test understanding. If the learner demonstrates a misconception, the system provides a targeted re-explanation before continuing.

At the end, the learner receives a final assessment and a learning report.

---

## 🚀 Key Features

### 📚 Document-Grounded Learning

Upload PDF, DOCX, PPTX, or TXT material and generate lessons grounded in the provided content.

### 🧠 Personalized Lesson Planning

Lessons are adapted according to the learner's level, available time, language, and preferred teaching style.

### 🎥 Avatar-Led Teaching

Concepts are delivered through spoken video lessons with an animated teaching avatar and captions.

### ❓ Checkpoint Questions

Short questions are presented throughout the lesson to continuously check understanding.

### 🔍 Misconception Detection

The system evaluates learner responses to identify where their understanding goes wrong.

### 🔄 Adaptive Re-Teaching

Instead of simply marking an answer wrong, AI Teacher generates a targeted explanation to address the learner's specific misconception.

### 📝 Final Assessment

A final quiz evaluates the learner's overall understanding after completing the lesson.

### 📊 Learning Report

The learner receives a summary of:

* Overall score
* Strong areas
* Weak areas
* Topics requiring revision
* Recommended next steps

### 💬 Follow-Up Questions

Learners can ask questions during the lesson instead of being restricted to a fixed learning path.

---

## ⭐ What Makes AI Teacher Different?

Traditional AI tutors often follow:

**Question → Answer**

AI Teacher follows a continuous teaching loop:

**Understand → Plan → Teach → Check → Evaluate → Adapt → Re-teach → Assess**

The key difference is that the system does not treat every learner the same way.

If a learner struggles with a concept, the lesson can **change its teaching approach based on the learner's response** rather than simply moving forward.

---

## 🧠 How It Works

```text
                 ┌─────────────────────┐
                 │   Topic / Document  │
                 └──────────┬──────────┘
                            ↓
                 ┌─────────────────────┐
                 │ Content Extraction  │
                 │      + RAG          │
                 └──────────┬──────────┘
                            ↓
                 ┌─────────────────────┐
                 │   Lesson Planner    │
                 │  (LLM + Learner     │
                 │     Profile)        │
                 └──────────┬──────────┘
                            ↓
                 ┌─────────────────────┐
                 │   AI Explanation   │
                 │  Voice + Avatar     │
                 └──────────┬──────────┘
                            ↓
                 ┌─────────────────────┐
                 │ Checkpoint Question │
                 └──────────┬──────────┘
                            ↓
                 ┌─────────────────────┐
                 │ Answer Evaluation   │
                 └──────────┬──────────┘
                            ↓
                    ┌───────┴───────┐
                    │               │
                 Understood      Misconception
                    │               │
                    ↓               ↓
                 Continue       Re-teach
                    │               │
                    └───────┬───────┘
                            ↓
                 ┌─────────────────────┐
                 │   Final Assessment  │
                 └──────────┬──────────┘
                            ↓
                 ┌─────────────────────┐
                 │   Learning Report   │
                 └─────────────────────┘
```

---

## 🏗️ System Architecture

```text
Frontend
   │
   ▼
Flask Backend / API
   │
   ├── Document Processor
   │       └── PDF / DOCX / PPTX / TXT
   │
   ├── RAG Engine
   │       └── TF-IDF Retrieval
   │
   ├── LLM Engine
   │       ├── Lesson Planning
   │       ├── Answer Evaluation
   │       ├── Misconception Detection
   │       └── Adaptive Re-teaching
   │
   ├── TTS Engine
   │       └── gTTS / ElevenLabs
   │
   ├── Video Generator
   │       └── Avatar + Voice + Captions
   │
   └── Quiz Engine
           └── Final Assessment
```

---

## 🛠️ Technology Stack

| Layer               | Technology                         |
| ------------------- | ---------------------------------- |
| Frontend            | HTML, CSS, JavaScript              |
| Backend             | Python, Flask                      |
| LLM                 | Groq                               |
| Retrieval           | TF-IDF                             |
| Document Processing | PDF / DOCX / PPTX / TXT processing |
| Text-to-Speech      | gTTS                               |
| Optional Voice      | ElevenLabs                         |
| Video Generation    | MoviePy + PIL                      |
| API Architecture    | REST APIs                          |

---

## 📁 Project Structure

```text
ai-teacher/
│
├── app.py
├── requirements.txt
├── .env.example
│
├── modules/
│   ├── document_processor.py
│   ├── rag_engine.py
│   ├── llm_engine.py
│   ├── tts_engine.py
│   ├── video_generator.py
│   └── quiz_engine.py
│
├── templates/
│   └── index.html
│
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js
│
├── uploads/
└── static/generated/
```

---




🔗 Project Links
🌐 Live Demo: https://ai-teacher-pathshala.onrender.com
💻 GitHub Repository: https://github.com/pyharshcodes/ai-teacher01/edit/main/ai-teacher
🎥 Demo Video: https://youtu.be/z5sn1_0l1pI?si=fSoH4O_5EXV6iruJ




---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd ai-teacher
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate it

**Windows:**

```bash
venv\Scripts\activate
```

**Linux / macOS:**

```bash
source venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure environment variables

Copy `.env.example` to `.env` and add your API keys.

```env
GROQ_API_KEY=your_key_here
ELEVENLABS_API_KEY=
```

### 6. Run the application

```bash
python app.py
```

Open:

```text
http://localhost:5000
```

---

## 🔐 API Configuration

**Groq** is required for the full AI-powered lesson generation, evaluation, misconception detection, and adaptive teaching pipeline.

**ElevenLabs** is optional and can be used for enhanced voice generation.

API keys should be stored in `.env` and **must not be committed to GitHub**.

---

## ⚠️ Current Limitations

* The default avatar is a programmatically animated illustration rather than a photorealistic AI avatar.
* The current RAG implementation uses TF-IDF retrieval rather than neural embeddings.
* Lesson state is currently maintained in memory and is intended for the prototype/demo environment.
* gTTS requires an internet connection during speech generation.

These limitations are primarily engineering trade-offs made to keep the prototype lightweight, accessible, and demonstrable.

---

## 🔮 Future Scope

### More Natural AI Avatars

Integration with advanced avatar-generation platforms for more realistic teaching videos.

### Semantic Retrieval

Replace TF-IDF with embedding-based retrieval and a vector database for stronger document understanding.

### Long-Term Learner Profiles

Store learning history and build persistent learner profiles to personalize future lessons.

### Multimodal Learning

Support diagrams, images, handwritten answers, and visual explanations.

### Voice-Based Interaction

Allow learners to communicate naturally with the AI teacher using speech.

### Learning Analytics

Track progress across multiple lessons and identify long-term learning patterns.

---

## 👥 Team

**Team:** *CodeNova*

**Hackathon:** AI Innovation Hackathon 2026

---

## 📄 License

This project is developed as a hackathon prototype.
