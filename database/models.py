from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean, 
    ForeignKey, CheckConstraint, UniqueConstraint
)
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    user_id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False, unique=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True)
    join_date = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    posts = relationship("Post", back_populates="user")
    comments = relationship("Comment", back_populates="user")
    likes = relationship("Like", back_populates="user")
    followers = relationship(
        "User",
        secondary="follows",
        primaryjoin="User.user_id==Follow.followee_id",
        secondaryjoin="User.user_id==Follow.follower_id",
        backref="following"
    )

class Post(Base):
    __tablename__ = 'posts'
    
    post_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    post_text = Column(Text)
    media_url = Column(String(255))
    post_time = Column(DateTime, default=datetime.utcnow)
    is_public = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post")
    likes = relationship("Like", back_populates="post")

class Comment(Base):
    __tablename__ = 'comments'
    
    comment_id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey('posts.post_id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    parent_comment_id = Column(Integer, ForeignKey('comments.comment_id'))
    comment_text = Column(Text, nullable=False)
    comment_time = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="comments")
    post = relationship("Post", back_populates="comments")
    parent = relationship(
        "Comment", 
        remote_side=[comment_id],
        backref=backref('replies'),
        uselist=False
    )

class Like(Base):
    __tablename__ = 'likes'
    
    like_id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey('posts.post_id'))
    comment_id = Column(Integer, ForeignKey('comments.comment_id'))
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    like_time = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="likes")
    post = relationship("Post", back_populates="likes")
    comment = relationship("Comment")
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            '(post_id IS NOT NULL AND comment_id IS NULL) OR '
            '(post_id IS NULL AND comment_id IS NOT NULL)',
            name='chk_like_target'
        ),
        UniqueConstraint('user_id', 'post_id', 'comment_id', name='unq_like')
    )

class Follow(Base):
    __tablename__ = 'follows'
    
    follower_id = Column(
        Integer, 
        ForeignKey('users.user_id'), 
        primary_key=True
    )
    followee_id = Column(
        Integer, 
        ForeignKey('users.user_id'), 
        primary_key=True
    )
    follow_time = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        CheckConstraint('follower_id != followee_id', name='chk_no_self_follow'),
    )