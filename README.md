# 😎Case.ai

 1. Case.AI is a smart AI-driven assistant that makes legal document management easy.
 2. It automatically extracts and summarizes important details from long PDFs in simple, professional language.
 3. Case.ai has support for multiple languages—English, Hindi, and Punjabi—making it easy to understand by various users.
 4. Users can query their documents with questions and get accurate, context-sensitive responses.
 5. Case.AI saves time and minimizes manual effort, enabling legal professionals to make quicker, better-informed decisions.

## ✨Demo Images

## 🧲Tech Stack

 - Python+FastAPI – Backend framework for API routing, authentication, and file uploading (PDFs/audio). Also manages dividing transcripts into chunks for LLM processing.
 - Node.js – Can be leveraged for speech-to-text / transcription pipelines (e.g., Whisper.js, Deepgram SDK, or AssemblyAI clients). This is only needed if you’re actually handling audio/video transcription outside Python.
 - React(with CRACO) – Frontend library to manage user interaction, prompt chaining, document Q&A, and rendering LLM outputs dynamically.
 - Tailwind CSS+Radix UI – UI layer for fast, responsive, and accessible frontend design. (Not an LLM — but it makes your app look polished).
 - MongoDB(via Motor) – Database to store user accounts, uploaded documents, summaries, chat history, etc.
 - Google Generative AI(Gemini API) – Core AI engine used for generating summaries, Q&A, and multi-language responses.

## 🌀Workflow
 1. User selects a PDF/DOCX file.
 2. React frontend sends document to FastAPI backend.
 3. FastAPI extracts and sanitizes text.
 4. Backend breaks down text into smaller pieces.
 5. Google Generative AI processes each piece.
 6. Backend aggregates results into a final summary.
 7. MongoDB saves file, text, and outputs.
 8. Frontend shows summary, hashtags, and results.
 9. User can query document for follow-up questions.

## 🌊Run on your System

 **Step1:** git clone https://github.com/V-inaya-K/Case.Ai.git<br />
 **Step2:** Open two seprate terminals<br />
 **Step3:** Create .env files with your Api keys in project root.<br />
 **Step4:** MongoDb and Google GenAI API in frontend/.env<br />
 **Step5:** React API in backend/.env<br />
 **Step6:** COMMANDS: cd frontend => npm install => npm start<br />
 **Step7:** COMMANDS: cd backend => pip install -r requirements.txt => python -m uvicorn server:app --reload
 
## 🚀Future Ambitions
