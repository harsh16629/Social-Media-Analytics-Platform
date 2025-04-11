from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import pandas as pd
from datetime import datetime
from .visualization import SocialMediaVisualizer

class ContentAnalyzer:
    def __init__(self, session: Session):
        self.session = session
        self.visualizer = SocialMediaVisualizer(dark_mode=True)
    
    def analyze_thread_depth(self, min_depth: int = 2) -> List[Dict[str, Any]]:
        """
        Analyze comment thread depths and identify posts with deep conversations
        Args:
            min_depth: Minimum thread depth to consider (default: 2)
        Returns:
            List of dictionaries containing thread depth analysis
        """
        query = text("""
            WITH RECURSIVE comment_threads AS (
                -- Base case: top-level comments
                SELECT 
                    comment_id,
                    post_id,
                    user_id,
                    parent_comment_id,
                    comment_text,
                    1 AS depth
                FROM comments
                WHERE parent_comment_id IS NULL
                
                UNION ALL
                
                -- Recursive case: replies
                SELECT 
                    c.comment_id,
                    c.post_id,
                    c.user_id,
                    c.parent_comment_id,
                    c.comment_text,
                    ct.depth + 1 AS depth
                FROM comments c
                JOIN comment_threads ct ON c.parent_comment_id = ct.comment_id
            )
            SELECT 
                p.post_id,
                SUBSTRING(p.post_text, 1, 50) AS post_preview,
                COUNT(DISTINCT ct.comment_id) AS total_comments,
                MAX(ct.depth) AS max_thread_depth,
                ROUND(AVG(ct.depth), 2) AS avg_thread_depth,
                COUNT(DISTINCT ct.user_id) AS unique_participants,
                GROUP_CONCAT(DISTINCT u.username ORDER BY u.username SEPARATOR ', ') AS participants
            FROM posts p
            JOIN comment_threads ct ON p.post_id = ct.post_id
            JOIN users u ON ct.user_id = u.user_id
            GROUP BY p.post_id, p.post_text
            HAVING MAX(ct.depth) >= :min_depth
            ORDER BY max_thread_depth DESC, total_comments DESC
        """)
        
        result = self.session.execute(query, {'min_depth': min_depth}).fetchall()
        return [dict(row) for row in result]
    
    def get_post_activity_timeline(self, post_id: int) -> pd.DataFrame:
        """
        Get the timeline of activity for a specific post
        Args:
            post_id: ID of the post to analyze
        Returns:
            DataFrame with timeline of comments and likes
        """
        query = text("""
            SELECT 
                'comment' AS activity_type,
                c.comment_time AS timestamp,
                u.username,
                c.comment_text AS content,
                NULL AS like_count
            FROM comments c
            JOIN users u ON c.user_id = u.user_id
            WHERE c.post_id = :post_id
            
            UNION ALL
            
            SELECT 
                'like' AS activity_type,
                l.like_time AS timestamp,
                u.username,
                NULL AS content,
                COUNT(*) OVER (PARTITION BY DATE(l.like_time)) AS like_count
            FROM likes l
            JOIN users u ON l.user_id = u.user_id
            WHERE l.post_id = :post_id
            ORDER BY timestamp
        """)
        
        result = self.session.execute(query, {'post_id': post_id}).fetchall()
        return pd.DataFrame([dict(row) for row in result])
    
    def identify_controversial_posts(self, min_comments: int = 10, min_stddev: float = 2.0) -> List[Dict[str, Any]]:
        """
        Identify posts with controversial discussions based on comment patterns
        Args:
            min_comments: Minimum number of comments to consider
            min_stddev: Minimum standard deviation of reply depths
        Returns:
            List of controversial posts with metrics
        """
        query = text("""
            WITH comment_stats AS (
                SELECT 
                    post_id,
                    COUNT(*) AS total_comments,
                    AVG(LENGTH(comment_text)) AS avg_comment_length,
                    STDDEV(LENGTH(comment_text)) AS stddev_comment_length,
                    COUNT(DISTINCT user_id) AS unique_commenters
                FROM comments
                GROUP BY post_id
                HAVING COUNT(*) >= :min_comments
            ),
            reply_depth AS (
                SELECT 
                    c1.post_id,
                    COUNT(c2.comment_id) AS reply_count,
                    AVG(LENGTH(c2.comment_text)) AS avg_reply_length
                FROM comments c1
                JOIN comments c2 ON c1.comment_id = c2.parent_comment_id
                GROUP BY c1.post_id
            )
            SELECT 
                p.post_id,
                p.post_text,
                p.post_time,
                u.username AS author,
                cs.total_comments,
                cs.unique_commenters,
                cs.avg_comment_length,
                cs.stddev_comment_length,
                COALESCE(rd.reply_count, 0) AS reply_count,
                COALESCE(rd.avg_reply_length, 0) AS avg_reply_length,
                (cs.stddev_comment_length * cs.total_comments) AS controversy_score
            FROM posts p
            JOIN comment_stats cs ON p.post_id = cs.post_id
            LEFT JOIN reply_depth rd ON p.post_id = rd.post_id
            JOIN users u ON p.user_id = u.user_id
            WHERE cs.stddev_comment_length >= :min_stddev
            ORDER BY controversy_score DESC
        """)
        
        result = self.session.execute(
            query, 
            {'min_comments': min_comments, 'min_stddev': min_stddev}
        ).fetchall()
        return [dict(row) for row in result]
    
    def analyze_and_visualize_content(self, min_depth: int = 2) -> None:
        """Run complete content analysis and create visualizations"""
        # Get data
        thread_data = self.analyze_thread_depth(min_depth)
        controversial_posts = self.identify_controversial_posts()
        
        # Convert to DataFrames
        thread_df = pd.DataFrame(thread_data)
        controversial_df = pd.DataFrame(controversial_posts)
        
        # Visualizations
        print("\n=== Thread Depth Analysis ===")
        self.visualizer.plot_thread_depth_distribution(
            thread_df,
            engine='plotly'
        )
        
        if not controversial_df.empty:
            print("\n=== Controversial Posts ===")
            self.visualizer.plot_controversial_posts(
                controversial_df,
                engine='plotly'
            )
        
        # Metrics
        print("\nPosts with Deepest Threads:")
        print(thread_df.nlargest(5, 'max_thread_depth')[
            ['post_id', 'post_preview', 'max_thread_depth', 'unique_participants']
        ].to_string(index=False))
        
        if not controversial_df.empty:
            print("\nMost Controversial Posts:")
            print(controversial_df.nlargest(3, 'controversy_score')[
                ['post_id', 'author', 'controversy_score', 'total_comments']
            ].to_string(index=False))
        
        avg_thread_depth = thread_df['avg_thread_depth'].mean()
        print(f"\nAverage Thread Depth: {avg_thread_depth:.1f}")
        
        if not thread_df.empty:
            # Analyze a sample post's activity timeline
            sample_post = thread_df.iloc[0]['post_id']
            timeline = self.get_post_activity_timeline(sample_post)
            
            print(f"\nActivity Timeline for Post {sample_post}:")
            self.visualizer.plot_activity_timeline(
                timeline,
                title=f"Activity Timeline for Post {sample_post}",
                engine='plotly'
            )

    def get_top_contributors(self, days: int = 30, limit: int = 5) -> pd.DataFrame:
        """
        Identify the most active contributors in the network
        Args:
            days: Lookback period in days
            limit: Number of top contributors to return
        Returns:
            DataFrame with top contributors and their activity metrics
        """
        query = text("""
            WITH user_activity AS (
                SELECT 
                    u.user_id,
                    u.username,
                    COUNT(DISTINCT p.post_id) AS post_count,
                    COUNT(DISTINCT c.comment_id) AS comment_count,
                    COUNT(DISTINCT l.like_id) AS like_count,
                    COUNT(DISTINCT CASE WHEN f.follow_time >= NOW() - INTERVAL ':days DAYS' THEN f.followee_id END) AS new_following,
                    COUNT(DISTINCT CASE WHEN f2.follow_time >= NOW() - INTERVAL ':days DAYS' THEN f2.follower_id END) AS new_followers
                FROM users u
                LEFT JOIN posts p ON u.user_id = p.user_id AND p.post_time >= NOW() - INTERVAL ':days DAYS'
                LEFT JOIN comments c ON u.user_id = c.user_id AND c.comment_time >= NOW() - INTERVAL ':days DAYS'
                LEFT JOIN likes l ON u.user_id = l.user_id AND l.like_time >= NOW() - INTERVAL ':days DAYS'
                LEFT JOIN follows f ON u.user_id = f.follower_id AND f.follow_time >= NOW() - INTERVAL ':days DAYS'
                LEFT JOIN follows f2 ON u.user_id = f2.followee_id AND f2.follow_time >= NOW() - INTERVAL ':days DAYS'
                GROUP BY u.user_id, u.username
            )
            SELECT 
                user_id,
                username,
                post_count,
                comment_count,
                like_count,
                new_following,
                new_followers,
                (post_count * 3 + comment_count * 2 + like_count * 1 + new_followers * 5) AS activity_score
            FROM user_activity
            ORDER BY activity_score DESC
            LIMIT :limit
        """)
        
        result = self.session.execute(
            query, 
            {'days': days, 'limit': limit}
        ).fetchall()
        return pd.DataFrame([dict(row) for row in result])