from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from database import Base

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    role = Column(String(20))          # 'user' 또는 'assistant'
    content = Column(Text)             # 채팅 내용 (Text)
    created_at = Column(DateTime, default=datetime.utcnow) # 저장된 시간