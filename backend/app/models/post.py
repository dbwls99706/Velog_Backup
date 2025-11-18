from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class PostCache(Base):
    """Velog 포스트 캐시 - 변경 감지를 위해 저장"""
    __tablename__ = "posts_cache"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Velog Post Info
    slug = Column(String, index=True, nullable=False)  # URL slug
    title = Column(String, nullable=False)
    content_hash = Column(String, nullable=False)  # MD5 hash for change detection
    thumbnail = Column(String, nullable=True)
    tags = Column(Text, nullable=True)  # JSON array as string
    is_private = Column(Boolean, default=False)

    # Metadata
    published_at = Column(DateTime(timezone=True), nullable=True)
    last_backed_up = Column(DateTime(timezone=True), nullable=True)
    last_modified = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="posts")

    def __repr__(self):
        return f"<PostCache {self.slug}>"
