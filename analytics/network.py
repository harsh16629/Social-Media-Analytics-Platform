from typing import List, Dict, Any
import pandas as pd
from sqlalchemy import text
from .visualization import SocialMediaVisualizer

class NetworkAnalyzer:
    def __init__(self, session):
        self.session = session
        self.visualizer = SocialMediaVisualizer(dark_mode=True)
    
    def get_follower_network(self) -> pd.DataFrame:
        """Get complete follower network relationships"""
        query = text("""
            SELECT 
                u1.username AS follower_username,
                u2.username AS followee_username,
                f.follow_time
            FROM follows f
            JOIN users u1 ON f.follower_id = u1.user_id
            JOIN users u2 ON f.followee_id = u2.user_id
        """)
        result = self.session.execute(query).fetchall()
        return pd.DataFrame([dict(row) for row in result])
    
    def analyze_and_visualize_network(self) -> None:
        """Run analysis and create visualizations for network"""
        # Get data
        ghost_followers = self.identify_ghost_followers()
        network_data = self.get_follower_network()
        
        # Visualizations
        print("\nFollower Network Visualization:")
        self.visualizer.plot_follower_network(
            network_data,
            engine='plotly'
        )
        
        # Metrics
        print("\nGhost Followers (Never Interacted):")
        print(ghost_followers[['username', 'following_count']].to_string(index=False))
        
        # Calculate network density
        num_users = network_data[['follower_username', 'followee_username']].stack().nunique()
        num_edges = len(network_data)
        max_possible_edges = num_users * (num_users - 1)
        density = num_edges / max_possible_edges
        
        print(f"\nNetwork Density: {density:.2%}")
        print(f"Total Users: {num_users}")
        print(f"Total Connections: {num_edges}")