from sqlalchemy import func, case, text
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime, timedelta
import pandas as pd
from .visualization import SocialMediaVisualizer

class EngagementAnalyzer:
    def __init__(self, session: Session):
        self.session = session
    
    def get_post_engagement(self, days: int = 30) -> List[Dict[str, Any]]:
        """Calculate engagement metrics for posts within a time period"""
        query = text("""
            WITH post_stats AS (
                SELECT 
                    p.post_id,
                    p.user_id AS author_id,
                    u.username AS author_name,
                    p.post_text,
                    p.post_time,
                    COUNT(DISTINCT l.user_id) AS like_count,
                    COUNT(DISTINCT c.comment_id) AS comment_count,
                    COUNT(DISTINCT f.follower_id) AS follower_count
                FROM posts p
                LEFT JOIN likes l ON p.post_id = l.post_id
                LEFT JOIN comments c ON p.post_id = c.post_id
                JOIN users u ON p.user_id = u.user_id
                LEFT JOIN follows f ON p.user_id = f.followee_id
                WHERE p.post_time >= :start_date
                GROUP BY p.post_id, p.user_id, u.username, p.post_text, p.post_time
            )
            SELECT 
                post_id,
                author_id,
                author_name,
                post_text,
                post_time,
                like_count,
                comment_count,
                follower_count,
                ROUND((like_count + comment_count) * 100.0 / NULLIF(follower_count, 0), 2) AS engagement_rate,
                RANK() OVER (ORDER BY (like_count + comment_count) DESC) AS engagement_rank
            FROM post_stats
            ORDER BY engagement_rate DESC
        """)
        
        start_date = datetime.utcnow() - timedelta(days=days)
        result = self.session.execute(
            query, 
            {'start_date': start_date}
        ).fetchall()
        
        return [dict(row) for row in result]
    
    def get_user_engagement_summary(self) -> pd.DataFrame:
        """Generate engagement summary per user"""
        query = text("""
            SELECT 
                u.user_id,
                u.username,
                COUNT(DISTINCT p.post_id) AS post_count,
                COUNT(DISTINCT l.like_id) AS likes_received,
                COUNT(DISTINCT c.comment_id) AS comments_received,
                COUNT(DISTINCT f.follower_id) AS follower_count,
                COUNT(DISTINCT fl.followee_id) AS following_count,
                ROUND(COUNT(DISTINCT l.like_id) * 100.0 / 
                    NULLIF(COUNT(DISTINCT f.follower_id), 0), 2) AS avg_like_rate,
                ROUND(COUNT(DISTINCT c.comment_id) * 100.0 / 
                    NULLIF(COUNT(DISTINCT f.follower_id), 0), 2) AS avg_comment_rate
            FROM users u
            LEFT JOIN posts p ON u.user_id = p.user_id
            LEFT JOIN likes l ON p.post_id = l.post_id
            LEFT JOIN comments c ON p.post_id = c.post_id
            LEFT JOIN follows f ON u.user_id = f.followee_id
            LEFT JOIN follows fl ON u.user_id = fl.follower_id
            GROUP BY u.user_id, u.username
            ORDER BY likes_received DESC
        """)
        
        result = self.session.execute(query).fetchall()
        return pd.DataFrame([dict(row) for row in result])
    
    def analyze_and_visualize_engagement(self, days: int = 30) -> None:
        """Run analysis and create visualizations for engagement"""
        # Get data
        engagement_data = self.get_post_engagement(days)
        user_engagement = self.get_user_engagement_summary()
        
        # Convert to DataFrames
        engagement_df = pd.DataFrame(engagement_data)
        user_engagement_df = user_engagement.copy()
        
        # Visualizations
        print("\nEngagement Trends Over Time:")
        self.visualizer.plot_engagement_trends(
            engagement_df, 
            engine='plotly'
        )
        
        print("\nUser Engagement Matrix:")
        self.visualizer.plot_user_engagement_matrix(
            user_engagement_df,
            engine='plotly'
        )
        
        # Additional metrics
        print("\nTop 5 Posts by Engagement Rate:")
        print(engagement_df.nlargest(5, 'engagement_rate')[
            ['post_id', 'author_name', 'engagement_rate']
        ].to_string(index=False))
        
        print("\nBottom 5 Posts by Engagement Rate:")
        print(engagement_df.nsmallest(5, 'engagement_rate')[
            ['post_id', 'author_name', 'engagement_rate']
        ].to_string(index=False))