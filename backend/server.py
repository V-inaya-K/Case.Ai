# from fastapi import FastAPI, APIRouter, UploadFile, File, HTTPException, Form
# from fastapi.responses import JSONResponse
# from dotenv import load_dotenv
# from starlette.middleware.cors import CORSMiddleware
# from motor.motor_asyncio import AsyncIOMotorClient
# import os
# import logging
# from pathlib import Path
# from pydantic import BaseModel, Field
# from typing import List, Optional
# import uuid
# from datetime import datetime, timezone
# import PyPDF2
# import io
# import asyncio
# from emergentintegrations.llm.chat import LlmChat, UserMessage

# ROOT_DIR = Path(__file__).parent
# load_dotenv(ROOT_DIR / '.env')

# # MongoDB connection
# mongo_url = os.environ['MONGO_URL']
# client = AsyncIOMotorClient(mongo_url)
# db = client[os.environ['DB_NAME']]

# # Create the main app without a prefix
# app = FastAPI()

# # Create a router with the /api prefix
# api_router = APIRouter(prefix="/api")

# # Models
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

# # Initialize LLM Chat
# def get_llm_chat(session_id: str):
#     api_key = os.environ.get('EMERGENT_LLM_KEY')
#     return LlmChat(
#         api_key=api_key,
#         session_id=session_id,
#         system_message="You are a legal assistant specialized in analyzing legal documents. Provide clear, accurate, and helpful responses about legal content."
#     ).with_model("gemini", "gemini-2.0-flash")

# def extract_text_from_pdf(file_content: bytes) -> str:
#     try:
#         pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
#         text = ""
#         for page in pdf_reader.pages:
#             text += page.extract_text() + "\n"
#         return text.strip()
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=f"Error extracting text from PDF: {str(e)}")

# async def generate_summary(content: str, language: str = "english") -> str:
#     try:
#         chat = get_llm_chat(f"summary_{uuid.uuid4()}")
        
#         language_prompts = {
#             "english": "Summarize this legal document in clear, professional English. Focus on key legal points, obligations, rights, and important clauses:",
#             "hindi": "इस कानूनी दस्तावेज़ का सारांश स्पष्ट और व्यावसायिक हिंदी में प्रस्तुत करें। मुख्य कानूनी बिंदुओं, दायित्वों, अधिकारों और महत्वपूर्ण खंडों पर ध्यान दें:",
#             "punjabi": "ਇਸ ਕਾਨੂੰਨੀ ਦਸਤਾਵੇਜ਼ ਦਾ ਸਾਰ ਸਪਸ਼ਟ ਅਤੇ ਪੇਸ਼ੇਵਰ ਪੰਜਾਬੀ ਵਿੱਚ ਪੇਸ਼ ਕਰੋ। ਮੁੱਖ ਕਾਨੂੰਨੀ ਨੁਕਤਿਆਂ, ਜ਼ਿੰਮੇਵਾਰੀਆਂ, ਅਧਿਕਾਰਾਂ ਅਤੇ ਮਹੱਤਵਪੂਰਨ ਧਾਰਾਵਾਂ 'ਤੇ ਧਿਆਨ ਦਿਓ:"
#         }
        
#         prompt = language_prompts.get(language, language_prompts["english"])
#         message = UserMessage(text=f"{prompt}\n\n{content}")
        
#         response = await chat.send_message(message)
#         return response
#     except Exception as e:
#         return f"Error generating summary: {str(e)}"

# async def get_answer(document_content: str, question: str, language: str = "english") -> str:
#     try:
#         chat = get_llm_chat(f"qa_{uuid.uuid4()}")
        
#         language_prompts = {
#             "english": f"Based on the following legal document, please answer this question in English: {question}\n\nDocument Content:\n{document_content}",
#             "hindi": f"निम्नलिखित कानूनी दस्तावेज़ के आधार पर, कृपया इस प्रश्न का उत्तर हिंदी में दें: {question}\n\nदस्तावेज़ की सामग्री:\n{document_content}",
#             "punjabi": f"ਹੇਠ ਲਿਖੇ ਕਾਨੂੰਨੀ ਦਸਤਾਵੇਜ਼ ਦੇ ਆਧਾਰ 'ਤੇ, ਕਿਰਪਾ ਕਰਕੇ ਇਸ ਸਵਾਲ ਦਾ ਜਵਾਬ ਪੰਜਾਬੀ ਵਿੱਚ ਦਿਓ: {question}\n\nਦਸਤਾਵੇਜ਼ ਦੀ ਸਮੱਗਰੀ:\n{document_content}"
#         }
        
#         prompt = language_prompts.get(language, language_prompts["english"])
#         message = UserMessage(text=prompt)
        
#         response = await chat.send_message(message)
#         return response
#     except Exception as e:
#         return f"Error getting answer: {str(e)}"

# # API Routes
# @api_router.post("/users", response_model=User)
# async def create_user(user_data: UserCreate):
#     user_dict = user_data.dict()
#     user_obj = User(**user_dict)
    
#     # Check if user already exists
#     existing_user = await db.users.find_one({"email": user_obj.email})
#     if existing_user:
#         return User(**existing_user)
    
#     await db.users.insert_one(user_obj.dict())
#     return user_obj

# @api_router.get("/users/{email}", response_model=User)
# async def get_user(email: str):
#     user = await db.users.find_one({"email": email})
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
#     return User(**user)

# @api_router.post("/upload")
# async def upload_document(
#     file: UploadFile = File(...),
#     user_id: str = Form(...)
# ):
#     try:
#         # Get user and check upload limits
#         user = await db.users.find_one({"id": user_id})
#         if not user:
#             raise HTTPException(status_code=404, detail="User not found")
        
#         user_obj = User(**user)
        
#         # Check if user has exceeded free uploads
#         if user_obj.uploads_used >= 2:
#             return JSONResponse(
#                 status_code=402,
#                 content={"detail": "Free uploads exceeded. ₹50 payment required for additional uploads."}
#             )
        
#         # Read file content
#         content = await file.read()
        
#         # Extract text based on file type
#         if file.filename.lower().endswith('.pdf'):
#             text_content = extract_text_from_pdf(content)
#             file_type = "pdf"
#         else:
#             raise HTTPException(status_code=400, detail="Only PDF files are supported currently")
        
#         if not text_content.strip():
#             raise HTTPException(status_code=400, detail="No text could be extracted from the document")
        
#         # Generate summaries in all languages
#         print("Generating English summary...")
#         summary_en = await generate_summary(text_content, "english")
        
#         print("Generating Hindi summary...")
#         summary_hi = await generate_summary(text_content, "hindi")
        
#         print("Generating Punjabi summary...")
#         summary_pa = await generate_summary(text_content, "punjabi")
        
#         # Create document
#         document = Document(
#             user_id=user_id,
#             filename=file.filename,
#             content=text_content,
#             summary=summary_en,
#             summary_hindi=summary_hi,
#             summary_punjabi=summary_pa,
#             file_type=file_type
#         )
        
#         # Save document
#         await db.documents.insert_one(document.dict())
        
#         # Update user upload count
#         await db.users.update_one(
#             {"id": user_id},
#             {"$inc": {"uploads_used": 1}}
#         )
        
#         return {
#             "document_id": document.id,
#             "message": "Document uploaded and summarized successfully",
#             "summary": {
#                 "english": summary_en,
#                 "hindi": summary_hi,
#                 "punjabi": summary_pa
#             },
#             "uploads_remaining": 2 - (user_obj.uploads_used + 1)
#         }
        
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @api_router.get("/documents/{user_id}", response_model=List[Document])
# async def get_user_documents(user_id: str):
#     documents = await db.documents.find({"user_id": user_id}).to_list(length=None)
#     return [Document(**doc) for doc in documents]

# @api_router.get("/documents/detail/{document_id}", response_model=Document)
# async def get_document(document_id: str):
#     document = await db.documents.find_one({"id": document_id})
#     if not document:
#         raise HTTPException(status_code=404, detail="Document not found")
#     return Document(**document)

# @api_router.post("/chat", response_model=ChatMessage)
# async def ask_question(chat_request: ChatRequest):
#     try:
#         # Get document
#         document = await db.documents.find_one({"id": chat_request.document_id})
#         if not document:
#             raise HTTPException(status_code=404, detail="Document not found")
        
#         # Get answer
#         answer = await get_answer(
#             document["content"],
#             chat_request.question,
#             chat_request.language
#         )
        
#         # Save chat message
#         chat_message = ChatMessage(
#             document_id=chat_request.document_id,
#             user_id=chat_request.user_id,
#             question=chat_request.question,
#             answer=answer,
#             language=chat_request.language
#         )
        
#         await db.chat_messages.insert_one(chat_message.dict())
        
#         return chat_message
        
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @api_router.get("/chat/{document_id}/{user_id}", response_model=List[ChatMessage])
# async def get_chat_history(document_id: str, user_id: str):
#     messages = await db.chat_messages.find({
#         "document_id": document_id,
#         "user_id": user_id
#     }).sort("timestamp", 1).to_list(length=None)
    
#     return [ChatMessage(**msg) for msg in messages]

# # Include the router in the main app
# app.include_router(api_router)

# app.add_middleware(
#     CORSMiddleware,
#     allow_credentials=True,
#     allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Configure logging
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
# )
# logger = logging.getLogger(__name__)

# @app.on_event("shutdown")
# async def shutdown_db_client():
#     client.close()

# --------------------

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

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / ".env")

# MongoDB setup
mongo_url = os.environ.get("MONGO_URL")
db_name = os.environ.get("DB_NAME")
client = AsyncIOMotorClient(mongo_url)
db = client[db_name]

# Google Gen AI setup
genai.api_key = os.environ.get("GOOGLE_GENAI_KEY")

# FastAPI setup
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

# ---------------- Helper functions ----------------
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

async def generate_summary(content: str, language: str = "english") -> str:
    prompts = {
        "english": "Summarize this legal document in clear, professional English.",
        "hindi": "इस कानूनी दस्तावेज़ का सारांश स्पष्ट और व्यावसायिक हिंदी में प्रस्तुत करें।",
        "punjabi": "ਇਸ ਕਾਨੂੰਨੀ ਦਸਤਾਵੇਜ਼ ਦਾ ਸਾਰ ਸਪਸ਼ਟ ਅਤੇ ਪੇਸ਼ੇਵਰ ਪੰਜਾਬੀ ਵਿੱਚ ਪੇਸ਼ ਕਰੋ।"
    }
    prompt = prompts.get(language, prompts["english"]) + "\n\n" + content
    try:
        response = genai.generate_text(model="gemini-2.5-flash", prompt=prompt)
        return response.text
    except Exception as e:
        return f"Error generating summary: {str(e)}"

async def get_answer(document_content: str, question: str, language: str = "english") -> str:
    prompts = {
        "english": f"Based on the following legal document, answer this question in English: {question}\n\n{document_content}",
        "hindi": f"निम्नलिखित कानूनी दस्तावेज़ के आधार पर इस प्रश्न का उत्तर हिंदी में दें: {question}\n\n{document_content}",
        "punjabi": f"ਹੇਠ ਲਿਖੇ ਕਾਨੂੰਨੀ ਦਸਤਾਵੇਜ਼ ਦੇ ਆਧਾਰ 'ਤੇ ਇਸ ਸਵਾਲ ਦਾ ਜਵਾਬ ਪੰਜਾਬੀ ਵਿੱਚ ਦਿਓ: {question}\n\n{document_content}"
    }
    prompt = prompts.get(language, prompts["english"])
    try:
        response = genai.generate_text(model="gemini-2.5-flash", prompt=prompt)
        return response.text
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
async def upload_document(file: UploadFile = File(...), user_id: str = Form(...)):
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

    summary_en = await generate_summary(text_content, "english")
    summary_hi = await generate_summary(text_content, "hindi")
    summary_pa = await generate_summary(text_content, "punjabi")

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
    answer = await get_answer(document["content"], chat_request.question, chat_request.language)
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

# ---------------- Final setup ----------------
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
