from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class PostCache(Base):
    """Velog 포스트 백업 저장소 - 서버에 직접 저장"""
    __tablename__ = "post_cache"
    __table_args__ = (
        UniqueConstraint('user_id', 'slug', name='uq_post_cache_user_slug'),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Velog Post Info
    slug = Column(String, index=True, nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=True)  # 마크다운 전체 내용 저장
    content_hash = Column(String, nullable=False)  # MD5 hash for change detection
    thumbnail = Column(String, nullable=True)
    tags = Column(Text, nullable=True)  # JSON string

    # Metadata
    velog_published_at = Column(DateTime(timezone=True), nullable=True)
    last_backed_up = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="posts")

    def __repr__(self):
        return f"<PostCache {self.slug}>"
