# Pathshala AI — AI Teacher

> **An AI Teacher that teaches, asks, evaluates, adapts, and helps students learn — instead of simply answering questions.**

Pathshala AI is an AI-powered virtual teacher built for the **AI Innovation Hackathon 2026 – AI Teacher Challenge**.

It can take a topic directly from a student or learn from uploaded educational material such as PDF, DOCX, PPTX and TXT files. Based on the student's level, available time, language and preferred teaching style, it creates a structured lesson and delivers it through an AI teaching video with voice and an animated teacher.

The system then interacts with the student through checkpoint questions, evaluates their responses, identifies possible misconceptions, re-explains difficult concepts and provides a final assessment and learning report.

---

## 🚀 Try Pathshala AI

### Live Demo

**Live Application:** `PASTE_YOUR_DEPLOYED_LINK_HERE`

### Demo Video

**Demo Video:** `PASTE_YOUR_DEMO_VIDEO_LINK_HERE`

The demo shows the complete learning flow:

**Topic / Upload → Lesson Planning → AI Teaching Video → Student Interaction → Evaluation → Adaptation → Final Assessment → Learning Report**

---

# 1. Problem

Most digital learning platforms either provide pre-recorded lectures or chatbot-style question answering.

The problem is that these systems generally do not behave like an actual teacher.

A real teacher:

- Understands the learner's level
- Plans what should be taught
- Explains concepts progressively
- Uses examples
- Asks questions
- Checks understanding
- Identifies misconceptions
- Re-explains difficult concepts
- Adjusts the difficulty
- Gives feedback
- Suggests what to learn next

Pathshala AI is designed around this teaching process rather than treating education as simple question answering.

---

# 2. Our Solution

Pathshala AI follows a teacher-like learning loop:

```text
Understand
    ↓
Plan
    ↓
Explain
    ↓
Question
    ↓
Evaluate
    ↓
Adapt
    ↓
Continue
A student can either:

Enter a topic directly, or
Upload their own learning material.

The student can also specify:

Learning level
Available learning time
Preferred language
Teaching style

The AI then generates a structured lesson and teaches it segment by segment.

After selected segments, the student receives checkpoint questions. Their answers are evaluated and the teaching can adapt based on the result.

3. Key Features
📚 Learn From Uploaded Material

Pathshala AI supports:

PDF
DOCX
PPTX
TXT

The uploaded material is processed and converted into searchable text chunks.

Relevant content is retrieved when generating a lesson so that document-based teaching can remain grounded in the student's material.

🎯 Topic-Based Teaching

Students do not need to upload a document.

They can simply enter a topic such as:

Teach me Newton's Laws from the beginning.

The AI creates a structured lesson according to the selected learner level, time and teaching preferences.

🧠 Personalized Lesson Planning

The student can select:

Parameter	Example
Learning Level	Beginner / Intermediate / Advanced
Available Time	5 / 20 / 60 minutes
Language	English / Hindi / Hinglish / etc.
Teaching Style	Simple explanations with examples

These inputs are used when generating the lesson structure and explanations.

🎥 AI Teaching Video

Each lesson segment is converted into a teaching experience containing:

AI-generated explanation
Text-to-speech narration
Animated teacher/avatar
Captions
Topic heading
Example
Visual indication/suggestion

The current implementation uses a programmatically rendered animated teacher rather than a photorealistic avatar.

❓ Interactive Checkpoints

Pathshala AI does not continuously deliver a lecture.

Questions are inserted into the lesson so that the student can demonstrate their understanding.

Supported question styles include:

Multiple choice
Short answer
Conceptual questions

The student's response becomes part of the teaching process.

🔍 Misconception Detection

When a student gives an incorrect or incomplete response, the system does more than simply mark it wrong.

The AI evaluates the response and attempts to identify the underlying misconception.

For example:

Question
   ↓
Student Answer
   ↓
AI Evaluation
   ↓
Correct / Incorrect
   ↓
Possible Misconception
   ↓
Feedback
   ↓
Re-explanation
🔄 Adaptive Teaching

If the student struggles with a concept, the system can:

Identify the misunderstanding
Give constructive feedback
Provide a fresh explanation
Use another angle or analogy
Adjust the difficulty
Continue the lesson after the interaction

The evaluation system can return one of:

easier
same
harder

This creates the core adaptive teaching loop.

💬 Follow-up Questions

Students can ask questions while the lesson is in progress.

The system uses the lesson content already taught during the current session to answer follow-up questions while maintaining the context of the lesson.

📝 Final Assessment

After the lesson, Pathshala AI generates a final assessment based on the lesson objectives and covered concepts.

The assessment can contain:

MCQs
Short-answer questions

The student's responses are evaluated and combined with checkpoint performance.

📊 Learning Report

After assessment, the system generates a learning report containing:

Final score
Correct answers
Total questions
Strong areas
Weak areas
Misconceptions
Revision recommendation
Question-by-question performance history

Example:

Topic: Newton's Laws

Score: 80%

Strong Areas:
- First Law
- Inertia

Needs Improvement:
- Second Law
- Force calculations

Recommendation:
Revise the identified weak concept before moving
to the next topic.
4. How the System Works
Step 1 — Student Input

The student provides:

Topic
+
Level
+
Available Time
+
Language
+
Teaching Style

or uploads educational material.

Step 2 — Document Processing

For uploaded material:

PDF / DOCX / PPTX / TXT
          ↓
     Text Extraction
          ↓
       Chunking
          ↓
      RAG Index

The system extracts text from the uploaded file and divides it into chunks.

Step 3 — Knowledge Retrieval

The current implementation uses:

TF-IDF + Cosine Similarity

Relevant chunks are retrieved based on the requested topic.

Student Topic
     ↓
TF-IDF Query
     ↓
Similarity Search
     ↓
Top Relevant Chunks
     ↓
LLM Context

This provides knowledge grounding for document-based lessons.

Step 4 — Lesson Generation

The LLM receives:

Topic
Learner level
Available time
Language
Teaching style
Retrieved document context, when available

It generates a structured lesson containing:

Lesson Title
Learning Objectives
Lesson Segments
Explanations
Examples
Visual Suggestions
Checkpoint Questions
Final Assessment
Step 5 — Teaching Video Generation

For each lesson segment:

Lesson Explanation
       ↓
Text-to-Speech
       ↓
Audio
       ↓
Caption Timing
       ↓
Animated Teacher + Visual Layer
       ↓
Teaching Video

The generated video is presented to the student before the checkpoint interaction.

Step 6 — Student Evaluation

After a checkpoint question:

Student Answer
      ↓
AI Evaluation
      ↓
Correct?
   ↙       ↘
 Yes       No
  ↓         ↓
Continue   Diagnose
             ↓
        Re-explanation
             ↓
       Difficulty Update
             ↓
          Continue
Step 7 — Final Assessment

After completing the lesson:

Final Quiz
    ↓
Answer Evaluation
    ↓
Score Calculation
    ↓
Learning Report
5. System Architecture
                         ┌───────────────┐
                         │    STUDENT    │
                         └───────┬───────┘
                                 │
                   ┌─────────────┴─────────────┐
                   │                           │
                   ▼                           ▼
             Enter Topic                Upload Material
                                               │
                                               ▼
                                      ┌─────────────────┐
                                      │ Document Parser │
                                      └────────┬────────┘
                                               │
                                               ▼
                                      ┌─────────────────┐
                                      │ Text Chunking   │
                                      └────────┬────────┘
                                               │
                                               ▼
                                      ┌─────────────────┐
                                      │ TF-IDF RAG      │
                                      │ Retrieval       │
                                      └────────┬────────┘
                                               │
                   ┌───────────────────────────┘
                   │
                   ▼
          ┌────────────────────┐
          │   Groq LLM         │
          │ Lesson Planning    │
          │ Evaluation         │
          │ Adaptation         │
          └─────────┬──────────┘
                    │
                    ▼
          ┌────────────────────┐
          │ Structured Lesson  │
          │ Plan               │
          └─────────┬──────────┘
                    │
                    ▼
          ┌────────────────────┐
          │ Teaching Engine    │
          └─────────┬──────────┘
                    │
          ┌─────────┴─────────┐
          │                   │
          ▼                   ▼
     Text-to-Speech     Video Renderer
          │                   │
          └─────────┬─────────┘
                    ▼
             Teaching Video
                    │
                    ▼
           Checkpoint Question
                    │
                    ▼
             Student Answer
                    │
                    ▼
          ┌────────────────────┐
          │ AI Evaluation      │
          │ + Misconception    │
          │ Detection          │
          └─────────┬──────────┘
                    │
             ┌──────┴──────┐
             │             │
          Understood     Struggling
             │             │
             ▼             ▼
          Continue     Re-explain
                           │
                           ▼
                       Continue
                           │
                           ▼
                   Final Assessment
                           │
                           ▼
                    Learning Report
6. AI / ML Stack
Component	Technology
Backend	Flask
LLM	Groq API
Lesson Planning	LLM-based structured generation
Answer Evaluation	LLM-based evaluation
Misconception Detection	LLM-based evaluation
Knowledge Grounding	TF-IDF + Cosine Similarity
Document Processing	PyPDF2, python-docx, python-pptx
Text-to-Speech	gTTS
Optional Voice	ElevenLabs
Video Generation	MoviePy + Pillow
Frontend	HTML, CSS, JavaScript
ML Utilities	Scikit-learn
7. RAG Implementation

Pathshala AI currently uses a lightweight TF-IDF based retrieval approach.

Pipeline
Uploaded Document
       ↓
Text Extraction
       ↓
Text Chunking
       ↓
TF-IDF Vectorization
       ↓
Cosine Similarity
       ↓
Top Relevant Chunks
       ↓
LLM Lesson Generation

This approach keeps the prototype lightweight while providing actual retrieval-based grounding for uploaded material.

The retrieved context is passed to the lesson-generation model so that document-based lessons can use information from the student's material.

8. LLM / Prompt Architecture

The LLM is used for different stages of the teaching process.

Lesson Planning

The model receives:

Topic
Learner Level
Available Time
Teaching Language
Teaching Style
Retrieved Context

It returns a structured lesson plan containing segments, explanations, examples, visuals and questions.

Answer Evaluation

The model receives:

Question
Student Answer
Relevant Lesson Context
Teaching Language

It returns:

Correct / Incorrect
Misconception
Feedback
Re-explanation
Difficulty Adjustment
Follow-up Questions

The model receives:

Lesson Context
+
Student Follow-up Question

and generates a context-aware answer.

9. Personalization

Pathshala AI personalizes the lesson using four main inputs:

Learner Level
Beginner
Intermediate
Advanced
Available Time

The lesson structure changes according to the selected duration.

Short sessions focus on the most important concepts, while longer sessions can include more explanations, examples and assessment.

Language

The student can select the teaching language.

The current TTS layer includes mappings for:

English
Hindi
Hinglish
Tamil
Telugu
Marathi
Bengali
Gujarati
Kannada
Malayalam
Punjabi
Urdu
Spanish
French
Teaching Style

The student can specify the preferred teaching approach, such as simple explanations with examples.

10. Teaching Interaction

The application is designed around the following interaction:

Teacher Explains
       ↓
Teacher Asks
       ↓
Student Answers
       ↓
Teacher Evaluates
       ↓
Teacher Identifies Difficulty
       ↓
Teacher Re-explains if Required
       ↓
Teacher Continues

This is the main difference between Pathshala AI and a conventional educational chatbot.

11. Project Structure
ai-teacher/
│
├── app.py
├── requirements.txt
├── .env.example
├── .gitignore
│
├── modules/
│   ├── __init__.py
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
│   ├── js/
│   │   └── main.js
│   └── generated/
│       ├── audio/
│       └── video/
│
└── uploads/
12. API Flow

The Flask backend exposes the main application flow through API endpoints.

Endpoint	Purpose
/api/status	Check application/AI status
/api/upload	Upload and process learning material
/api/create_lesson	Generate personalized lesson
/api/segment_media	Generate lesson audio/video
/api/checkpoint	Evaluate checkpoint answer
/api/followup	Answer follow-up question
/api/final_quiz	Retrieve final assessment
/api/submit_quiz	Submit assessment and generate report
13. Installation
Requirements
Python 3.10+
Internet connection for gTTS
Groq API key for full AI-powered lesson generation
Clone the Repository
git clone https://github.com/pyharshcodes/ai-teacher01.git

Enter the project:

cd ai-teacher01/ai-teacher
Create Virtual Environment
Windows
python -m venv venv
venv\Scripts\activate
Linux / macOS
python -m venv venv
source venv/bin/activate
Install Dependencies
pip install -r requirements.txt
14. Environment Variables

Create a .env file in the ai-teacher directory.

GROQ_API_KEY=your_groq_api_key

Optional:

GROQ_MODEL=your_groq_model
ELEVENLABS_API_KEY=your_elevenlabs_api_key
FLASK_SECRET_KEY=your_secret_key

The .env.example file is included in the repository.

Do not commit your real API keys to GitHub.

15. Run the Application

Start the Flask server:

python app.py

Open:

http://localhost:5000
16. How to Use
Step 1

Enter a topic or upload learning material.

Step 2

Select:

Level
Available time
Language
Teaching style
Step 3

Start the lesson.

The AI generates a structured lesson plan.

Step 4

Watch the generated teaching segment.

The lesson contains voice narration, an animated teacher and captions.

Step 5

Answer the checkpoint question.

Step 6

The AI evaluates the response.

If required, it provides a different explanation and adjusts the difficulty.

Step 7

Continue through the remaining lesson segments.

Step 8

Complete the final assessment.

Step 9

View the learning report and recommended revision areas.

17. Deployment

Pathshala AI is implemented as a Flask web application and can be deployed on a Python-compatible hosting platform.

For deployment:

Upload/push the project repository.
Install dependencies from requirements.txt.
Configure environment variables.
Start the Flask application using the platform's Python web-service configuration.
Verify that generated media directories have write access.
Important

API keys should be configured as deployment environment variables rather than hard-coded into the source code.

18. Current Limitations

This is a hackathon prototype, so there are some known limitations.

RAG

The current retrieval system uses TF-IDF rather than neural embeddings.

Avatar

The current teacher is a programmatically animated avatar rather than a photorealistic AI-generated human.

Session Storage

Lesson state is currently maintained in memory for the running Flask process.

Text-to-Speech

The default gTTS implementation requires an internet connection.

Production Scale

The current architecture is optimized for a functional prototype and demonstration rather than large-scale multi-user deployment.

19. Future Improvements

The architecture can be extended with:

Semantic embedding-based RAG
Vector database
Persistent student profiles
Long-term learning history
Real-time conversational teaching
More advanced subject-specific visuals
Photorealistic AI teacher avatars
Personalized study plans
Revision mode
Exam preparation mode
Flashcard generation
Learning analytics
Persistent progress tracking
More advanced adaptive learning strategies
20. Why Pathshala AI?

A conventional chatbot:

Student → Question → Answer

Pathshala AI:

Student
   ↓
Understand
   ↓
Plan
   ↓
Explain
   ↓
Question
   ↓
Evaluate
   ↓
Detect Misconception
   ↓
Adapt
   ↓
Continue
   ↓
Assess
   ↓
Recommend

The focus is not simply generating educational content.

The focus is creating a teaching loop where student performance can influence what the AI teaches next.

21. Hackathon Requirements Coverage
Challenge Requirement	Pathshala AI
Uploaded learning material	✅
Topic-based teaching	✅
AI-generated lesson structure	✅
Personalized teaching	✅
Human-like teaching interaction	✅
Video-based teaching	✅
AI voice	✅
AI teacher/avatar	✅
Multilingual teaching	✅
Student questioning	✅
Student assessment	✅
Misconception detection	✅
Adaptive response	✅
Follow-up questions	✅
Learning report	✅
Working web application	✅
22. Technology Disclosure
Third-Party APIs / Services

Groq API

Used for:

Lesson planning
Student answer evaluation
Misconception detection
Adaptive feedback
Follow-up question answering

Google Text-to-Speech (gTTS)

Used for generating narrated lesson audio.

ElevenLabs

Supported as an optional text-to-speech provider.

Open-Source / Python Libraries
Flask
Scikit-learn
PyPDF2
python-docx
python-pptx
MoviePy
Pillow
NumPy
python-dotenv
gTTS
23. Repository

GitHub Repository:

https://github.com/pyharshcodes/ai-teacher01

24. Demo

Live Application:

https://ai-teacher-pathshala.onrender.com

Demo Video:

PASTE_YOUR_DEMO_VIDEO_LINK_HERE

25. CodeNova

Project: Pathshala AI — AI Teacher

Hackathon: AI Innovation Hackathon 2026
