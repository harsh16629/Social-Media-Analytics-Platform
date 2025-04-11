from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import text
from .models import Base
from config import config
import logging

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

def setup_database():
    try:
        engine = create_engine(config.DATABASE_URI)
        
        # Create tables
        Base.metadata.create_all(engine)
        
        # Add indexes
        with engine.connect() as conn:
            index_queries = [
                "CREATE INDEX IF NOT EXISTS idx_posts_user ON posts(user_id)",
                "CREATE INDEX IF NOT EXISTS idx_comments_post ON comments(post_id)",
                "CREATE INDEX IF NOT EXISTS idx_comments_parent ON comments(parent_comment_id)",
                "CREATE INDEX IF NOT EXISTS idx_likes_post ON likes(post_id)",
                "CREATE INDEX IF NOT EXISTS idx_likes_comment ON likes(comment_id)",
                "CREATE INDEX IF NOT EXISTS idx_likes_user ON likes(user_id)",
                "CREATE INDEX IF NOT EXISTS idx_follows_follower ON follows(follower_id)",
                "CREATE INDEX IF NOT EXISTS idx_follows_followee ON follows(followee_id)"
            ]
            
            for query in index_queries:
                conn.execute(text(query))
            
            conn.commit()
        
        print("Database setup completed successfully")
        return engine
        
    except SQLAlchemyError as e:
        print(f"Error setting up database: {e}")
        raise