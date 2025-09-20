# from fastapi import FastAPI, APIRouter, UploadFile, File, Form, HTTPException
# from fastapi.responses import JSONResponse
# from starlette.middleware.cors import CORSMiddleware
# from pydantic import BaseModel, Field
# from typing import List
# from pathlib import Path
# from datetime import datetime, timezone
# import uuid
# import os
# import io
# import logging
# import PyPDF2
# from dotenv import load_dotenv
# from motor.motor_asyncio import AsyncIOMotorClient
# import google.generativeai as genai
# from contextlib import asynccontextmanager

# ROOT_DIR = Path(__file__).parent
# load_dotenv(ROOT_DIR / ".env")
# print("API key loaded?", os.getenv("GOOGLE_API_KEY") is not None)

# mongo_url = os.environ.get("MONGO_URL")
# db_name = os.environ.get("DB_NAME")
# client = AsyncIOMotorClient(mongo_url)
# db = client[db_name]

# genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     print("SERVER RUNNING SUCCESSFULLY 🚀")
#     try:
#         yield
#     finally:
#         client.close()

# app = FastAPI(lifespan=lifespan)
# api_router = APIRouter(prefix="/api")

# class User(BaseModel):
#     id: str = Field(default_factory=lambda: str(uuid.uuid4()))
#     email: str
#     uploads_used: int = 0
#     created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# class UserCreate(BaseModel):
#     email: str

# class Document(BaseModel):
#     id: str = Field(default_factory=lambda: str(uuid.uuid4()))
#     user_id: str
#     filename: str
#     content: str
#     summary: str = ""
#     summary_hindi: str = ""
#     summary_punjabi: str = ""
#     upload_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
#     file_type: str

# class ChatMessage(BaseModel):
#     id: str = Field(default_factory=lambda: str(uuid.uuid4()))
#     document_id: str
#     user_id: str
#     question: str
#     answer: str
#     language: str = "english"
#     timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# class ChatRequest(BaseModel):
#     document_id: str
#     user_id: str
#     question: str
#     language: str = "english"

# def extract_text_from_pdf(file_content: bytes) -> str:
#     try:
#         reader = PyPDF2.PdfReader(io.BytesIO(file_content))
#         text = ""
#         for page in reader.pages:
#             page_text = page.extract_text()
#             if page_text:
#                 text += page_text + "\n"
#         return text.strip()
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=f"Error extracting PDF: {str(e)}")

# # async def generate_summary(content: str, language: str = "english") -> str:
# #     prompts = {
# #         "english": "Summarize this legal document in clear, professional English.",
# #         "hindi": "इस कानूनी दस्तावेज़ का सारांश स्पष्ट और व्यावसायिक हिंदी में प्रस्तुत करें।",
# #         "punjabi": "ਇਸ ਕਾਨੂੰਨੀ ਦਸਤਾਵੇਜ਼ ਦਾ ਸਾਰ ਸਪਸ਼ਟ ਅਤੇ ਪੇਸ਼ੇਵਰ ਪੰਜਾਬੀ ਵਿੱਚ ਪੇਸ਼ ਕਰੋ।"
# #     }
# #     prompt = prompts.get(language, prompts["english"]) + "\n\n" + content
# #     try:
# #         model = genai.GenerativeModel("gemini-1.5-flash")
# #         response = model.generate_content(prompt)
# #         if hasattr(response, "text"):
# #             return response.text
# #         elif hasattr(response, "candidates"):
# #             return response.candidates[0].content.parts[0].text
# #         else:
# #             return "⚠️ No summary generated."
# #     except Exception as e:
# #         return f"Error generating summary: {str(e)}"

# MAX_CHARS = 4000  # max chars per chunk, adjust if needed

# def chunk_text(text: str, max_chars: int = MAX_CHARS):
#     """Split text into chunks of max_chars length."""
#     chunks = []
#     start = 0
#     while start < len(text):
#         chunks.append(text[start:start + max_chars])
#         start += max_chars
#     return chunks

# async def generate_summary(content: str, language: str = "english") -> str:
#     prompts = {
#         "english": "Summarize this legal document in clear, professional English.",
#         "hindi": "इस कानूनी दस्तावेज़ का सारांश स्पष्ट और व्यावसायिक हिंदी में प्रस्तुत करें।",
#         "punjabi": "ਇਸ ਕਾਨੂੰਨੀ ਦਸਤਾਵੇਜ਼ ਦਾ ਸਾਰ ਸਪਸ਼ਟ ਅਤੇ ਪੇਸ਼ੇਵਰ ਪੰਜਾਬੀ ਵਿੱਚ ਪੇਸ਼ ਕਰੋ।"
#     }

#     chunks = chunk_text(content)
#     summaries = []

#     for chunk in chunks:
#         prompt = prompts.get(language, prompts["english"]) + "\n\n" + chunk
#         try:
#             model = genai.GenerativeModel("gemini-1.5-flash")
#             response = model.generate_content(prompt)

#             # Extract text safely
#             if hasattr(response, "candidates") and response.candidates:
#                 candidate = response.candidates[0]
#                 if hasattr(candidate, "content"):
#                     if hasattr(candidate.content, "text"):
#                         summaries.append(candidate.content.text)
#                     elif hasattr(candidate.content, "parts") and candidate.content.parts:
#                         summaries.append(candidate.content.parts[0].text)
#                     else:
#                         summaries.append(str(candidate.content))
#                 else:
#                     summaries.append(str(candidate))
#             elif hasattr(response, "text"):
#                 summaries.append(response.text)
#             else:
#                 summaries.append(str(response))
#         except Exception as e:
#             summaries.append(f"Error: {str(e)}")

#     # Combine chunk summaries
#     final_summary = "\n".join(summaries)
#     return final_summary


# async def get_answer(document_content: str, question: str, language: str = "english") -> str:
#     prompts = {
#         "english": f"Based on the following legal document, answer this question in clear, professional English: {question}\n\n{document_content}",
#         "hindi": f"निम्नलिखित कानूनी दस्तावेज़ के आधार पर इस प्रश्न का उत्तर हिंदी में दें: {question}\n\n{document_content}",
#         "punjabi": f"ਹੇਠ ਲਿਖੇ ਕਾਨੂੰਨੀ ਦਸਤਾਵੇਜ਼ ਦੇ ਆਧਾਰ 'ਤੇ ਇਸ ਸਵਾਲ ਦਾ ਜਵਾਬ ਪੰਜਾਬੀ ਵਿੱਚ ਦਿਓ: {question}\n\n{document_content}"
#     }
#     prompt = prompts.get(language, prompts["english"])
#     try:
#         model = genai.GenerativeModel("gemini-1.5-flash")
#         response = model.generate_content(prompt)
#         if hasattr(response, "text"):
#             return response.text
#         elif hasattr(response, "candidates"):
#             return response.candidates[0].content.parts[0].text
#         else:
#             return "No answer generated."
#     except Exception as e:
#         return f"Error getting answer: {str(e)}"

# @api_router.post("/users", response_model=User)
# async def create_user(user_data: UserCreate):
#     existing = await db.users.find_one({"email": user_data.email})
#     if existing:
#         return User(**existing)
#     user_obj = User(email=user_data.email)
#     await db.users.insert_one(user_obj.dict())
#     return user_obj

# @api_router.get("/users/{email}", response_model=User)
# async def get_user(email: str):
#     user = await db.users.find_one({"email": email})
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
#     return User(**user)

# @api_router.post("/upload")
# async def upload_document(file: UploadFile = File(...), user_id: str = Form(...)):
#     user = await db.users.find_one({"id": user_id})
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
#     user_obj = User(**user)
#     if user_obj.uploads_used >= 2:
#         return JSONResponse(status_code=402, content={"detail": "Free uploads exceeded. ₹50 required."})

#     content = await file.read()
#     if not file.filename.lower().endswith(".pdf"):
#         raise HTTPException(status_code=400, detail="Only PDF files are supported")
#     text_content = extract_text_from_pdf(content)
#     if not text_content.strip():
#         raise HTTPException(status_code=400, detail="No text extracted")

#     summary_en = await generate_summary(text_content, "english")
#     summary_hi = await generate_summary(text_content, "hindi")
#     summary_pa = await generate_summary(text_content, "punjabi")

#     document = Document(
#         user_id=user_id,
#         filename=file.filename,
#         content=text_content,
#         summary=summary_en,
#         summary_hindi=summary_hi,
#         summary_punjabi=summary_pa,
#         file_type="pdf"
#     )
#     await db.documents.insert_one(document.dict())
#     await db.users.update_one({"id": user_id}, {"$inc": {"uploads_used": 1}})

#     return {
#         "document_id": document.id,
#         "message": "Document uploaded and summarized",
#         "summary": {"english": summary_en, "hindi": summary_hi, "punjabi": summary_pa},
#         "uploads_remaining": 2 - (user_obj.uploads_used + 1)
#     }

# @api_router.get("/documents/{user_id}", response_model=List[Document])
# async def get_user_documents(user_id: str):
#     docs = await db.documents.find({"user_id": user_id}).to_list(length=None)
#     return [Document(**doc) for doc in docs]

# @api_router.get("/documents/detail/{document_id}", response_model=Document)
# async def get_document(document_id: str):
#     doc = await db.documents.find_one({"id": document_id})
#     if not doc:
#         raise HTTPException(status_code=404, detail="Document not found")
#     return Document(**doc)

# @api_router.post("/chat", response_model=ChatMessage)
# async def ask_question(chat_request: ChatRequest):
#     document = await db.documents.find_one({"id": chat_request.document_id})
#     if not document:
#         raise HTTPException(status_code=404, detail="Document not found")
#     answer = await get_answer(document["content"], chat_request.question, chat_request.language)
#     chat_message = ChatMessage(
#         document_id=chat_request.document_id,
#         user_id=chat_request.user_id,
#         question=chat_request.question,
#         answer=answer,
#         language=chat_request.language
#     )
#     await db.chat_messages.insert_one(chat_message.dict())
#     return chat_message

# @api_router.get("/chat/{document_id}/{user_id}", response_model=List[ChatMessage])
# async def get_chat_history(document_id: str, user_id: str):
#     msgs = await db.chat_messages.find({"document_id": document_id, "user_id": user_id}).sort("timestamp", 1).to_list(length=None)
#     return [ChatMessage(**msg) for msg in msgs]

# # ---------------- Final setup Starts ----------------
# app.include_router(api_router)

# app.add_middleware(
#     CORSMiddleware,
#     allow_credentials=True,
#     allow_origins=os.environ.get("CORS_ORIGINS", "*").split(","),
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# logger = logging.getLogger(__name__)

# --------------

from fastapi import FastAPI, APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List
from pathlib import Path
from datetime import datetime, timezone
import uuid
import os
import io
import logging
import PyPDF2
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
import google.generativeai as genai
from contextlib import asynccontextmanager

# ---------------- Load environment ----------------
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / ".env")
print("API key loaded?", os.getenv("GOOGLE_API_KEY") is not None)

# ---------------- MongoDB setup ----------------
mongo_url = os.environ.get("MONGO_URL")
db_name = os.environ.get("DB_NAME")
client = AsyncIOMotorClient(mongo_url)
db = client[db_name]

# ---------------- Google Gen AI ----------------
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# ---------------- FastAPI setup ----------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("SERVER RUNNING SUCCESSFULLY 🚀")
    try:
        yield
    finally:
        client.close()

app = FastAPI(lifespan=lifespan)
api_router = APIRouter(prefix="/api")

# ---------------- Models ----------------
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    uploads_used: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserCreate(BaseModel):
    email: str

class Document(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    filename: str
    content: str
    summary: str = ""
    summary_hindi: str = ""
    summary_punjabi: str = ""
    upload_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    file_type: str

class ChatMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    document_id: str
    user_id: str
    question: str
    answer: str
    language: str = "english"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ChatRequest(BaseModel):
    document_id: str
    user_id: str
    question: str
    language: str = "english"
    tone: str = "professional"

# ---------------- Helpers ----------------
def extract_text_from_pdf(file_content: bytes) -> str:
    try:
        reader = PyPDF2.PdfReader(io.BytesIO(file_content))
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text.strip()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error extracting PDF: {str(e)}")

MAX_CHARS = 4000

def chunk_text(text: str, max_chars: int = MAX_CHARS):
    chunks = []
    start = 0
    while start < len(text):
        chunks.append(text[start:start + max_chars])
        start += max_chars
    return chunks

async def generate_summary(content: str, language: str = "english", tone: str = "professional") -> str:
    base_prompts = {
        "english": "Summarize this legal document in {style} English.",
        "hindi": "इस कानूनी दस्तावेज़ का सारांश {style} हिंदी में प्रस्तुत करें।",
        "punjabi": "ਇਸ ਕਾਨੂੰਨੀ ਦਸਤਾਵੇਜ਼ ਦਾ ਸਾਰ {style} ਪੰਜਾਬੀ ਵਿੱਚ ਪੇਸ਼ ਕਰੋ।"
    }
    tone_map = {
        "professional": "clear, professional",
        "friendly": "friendly and approachable",
        "casual": "casual and simple"
    }
    style = tone_map.get(tone, "clear, professional")
    prompt_template = base_prompts.get(language, base_prompts["english"])

    chunks = chunk_text(content)
    summaries = []

    for chunk in chunks:
        prompt = prompt_template.format(style=style) + "\n\n" + chunk
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)
            if hasattr(response, "candidates") and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, "content"):
                    if hasattr(candidate.content, "text"):
                        summaries.append(candidate.content.text)
                    elif hasattr(candidate.content, "parts") and candidate.content.parts:
                        summaries.append(candidate.content.parts[0].text)
                    else:
                        summaries.append(str(candidate.content))
                else:
                    summaries.append(str(candidate))
            elif hasattr(response, "text"):
                summaries.append(response.text)
            else:
                summaries.append(str(response))
        except Exception as e:
            summaries.append(f"Error: {str(e)}")

    return "\n".join(summaries)

async def get_answer(document_content: str, question: str, language: str = "english", tone: str = "professional") -> str:
    tone_map = {
        "professional": "clear, professional",
        "friendly": "friendly and approachable",
        "casual": "casual and simple"
    }
    style = tone_map.get(tone, "clear, professional")

    prompts = {
        "english": f"Based on the following legal document, answer this question in {style} English: {question}\n\n{document_content}",
        "hindi": f"निम्नलिखित कानूनी दस्तावेज़ के आधार पर इस प्रश्न का उत्तर {style} हिंदी में दें: {question}\n\n{document_content}",
        "punjabi": f"ਹੇਠ ਲਿਖੇ ਕਾਨੂੰਨੀ ਦਸਤਾਵੇਜ਼ ਦੇ ਆਧਾਰ 'ਤੇ ਇਸ ਸਵਾਲ ਦਾ ਜਵਾਬ {style} ਪੰਜਾਬੀ ਵਿੱਚ ਦਿਓ: {question}\n\n{document_content}"
    }

    prompt = prompts.get(language, prompts["english"])
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        if hasattr(response, "text"):
            return response.text
        elif hasattr(response, "candidates") and response.candidates:
            return response.candidates[0].content.parts[0].text
        else:
            return "No answer generated."
    except Exception as e:
        return f"Error getting answer: {str(e)}"

# ---------------- API Routes ----------------
@api_router.post("/users", response_model=User)
async def create_user(user_data: UserCreate):
    existing = await db.users.find_one({"email": user_data.email})
    if existing:
        return User(**existing)
    user_obj = User(email=user_data.email)
    await db.users.insert_one(user_obj.dict())
    return user_obj

@api_router.get("/users/{email}", response_model=User)
async def get_user(email: str):
    user = await db.users.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return User(**user)

@api_router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    user_id: str = Form(...),
    tone: str = Form("professional")
):
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user_obj = User(**user)
    if user_obj.uploads_used >= 2:
        return JSONResponse(status_code=402, content={"detail": "Free uploads exceeded. ₹50 required."})

    content = await file.read()
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    text_content = extract_text_from_pdf(content)
    if not text_content.strip():
        raise HTTPException(status_code=400, detail="No text extracted")

    summary_en = await generate_summary(text_content, "english", tone)
    summary_hi = await generate_summary(text_content, "hindi", tone)
    summary_pa = await generate_summary(text_content, "punjabi", tone)

    document = Document(
        user_id=user_id,
        filename=file.filename,
        content=text_content,
        summary=summary_en,
        summary_hindi=summary_hi,
        summary_punjabi=summary_pa,
        file_type="pdf"
    )
    await db.documents.insert_one(document.dict())
    await db.users.update_one({"id": user_id}, {"$inc": {"uploads_used": 1}})

    return {
        "document_id": document.id,
        "message": "Document uploaded and summarized",
        "summary": {"english": summary_en, "hindi": summary_hi, "punjabi": summary_pa},
        "uploads_remaining": 2 - (user_obj.uploads_used + 1)
    }

@api_router.get("/documents/{user_id}", response_model=List[Document])
async def get_user_documents(user_id: str):
    docs = await db.documents.find({"user_id": user_id}).to_list(length=None)
    return [Document(**doc) for doc in docs]

@api_router.get("/documents/detail/{document_id}", response_model=Document)
async def get_document(document_id: str):
    doc = await db.documents.find_one({"id": document_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return Document(**doc)

@api_router.post("/chat", response_model=ChatMessage)
async def ask_question(chat_request: ChatRequest):
    document = await db.documents.find_one({"id": chat_request.document_id})
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    answer = await get_answer(document["content"], chat_request.question, chat_request.language, chat_request.tone)
    chat_message = ChatMessage(
        document_id=chat_request.document_id,
        user_id=chat_request.user_id,
        question=chat_request.question,
        answer=answer,
        language=chat_request.language
    )
    await db.chat_messages.insert_one(chat_message.dict())
    return chat_message

@api_router.get("/chat/{document_id}/{user_id}", response_model=List[ChatMessage])
async def get_chat_history(document_id: str, user_id: str):
    msgs = await db.chat_messages.find({"document_id": document_id, "user_id": user_id}).sort("timestamp", 1).to_list(length=None)
    return [ChatMessage(**msg) for msg in msgs]

# ---------------- App setup ----------------
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get("CORS_ORIGINS", "*").split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
