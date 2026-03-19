from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, DateTime, ForeignKey, func
from sqlalchemy.orm import mapped_column, Mapped
from database.Base import Base


class ChunkRecord(Base):
    __tablename__ = "chunks"
    chunk_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    file_hash: Mapped[str] = mapped_column(String, ForeignKey("files.file_hash", ondelete="CASCADE"), nullable=False)
    node_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    node_title: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    node_path: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    node_summary: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    page_index: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    text: Mapped[str] = mapped_column(String, nullable=False)
    embedding: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
