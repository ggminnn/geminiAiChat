import sys

if sys.stdout is not None and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr is not None and hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

import asyncio
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from pydantic import BaseModel
from google import genai
from google.genai import types
import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session
import models
from database import engine, get_db, SessionLocal

load_dotenv()


models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    
class ChatRequest(BaseModel):
    message: str


@app.post("/chat/stream")
async def chat_stream(request: ChatRequest, db: Session = Depends(get_db)):
    # 유저 메시지 DB 저장
    db.add(models.ChatMessage(role="user", content=request.message))
    db.commit()

    # 최근 10개 메시지 불러오기 (방금 저장한 것 포함)
    history_rows = (
        db.query(models.ChatMessage)
        .order_by(models.ChatMessage.id.desc())
        .limit(10)
        .all()
    )
    history_rows.reverse()

    # 전체 대화를 Gemini contents 형식으로 구성
    contents = [
        types.Content(
            role="user" if msg.role == "user" else "model",
            parts=[types.Part(text=msg.content)],
        )
        for msg in history_rows
    ]

    async def event_generator():
        full_response = ""
        loop = asyncio.get_event_loop()
        chunk_queue: asyncio.Queue = asyncio.Queue()

        def run_sync_stream():
            try:
                for chunk in client.models.generate_content_stream(
                    model="models/gemini-2.5-flash",
                    contents=contents,
                ):
                    text = getattr(chunk, "text", None)
                    if text:
                        loop.call_soon_threadsafe(chunk_queue.put_nowait, text)
            except Exception as e:
                loop.call_soon_threadsafe(chunk_queue.put_nowait, f"[ERROR] {e}")
            finally:
                loop.call_soon_threadsafe(chunk_queue.put_nowait, None)

        loop.run_in_executor(None, run_sync_stream)

        while True:
            text = await chunk_queue.get()
            if text is None:
                break
            full_response += text
            yield f"data: {text}\n\n"

        # AI 응답 DB 저장
        save_db = SessionLocal()
        try:
            save_db.add(models.ChatMessage(role="assistant", content=full_response))
            save_db.commit()
        finally:
            save_db.close()

        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
