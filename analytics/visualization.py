import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import Optional

class SocialMediaVisualizer:
    def __init__(self, dark_mode: bool = False):
        self.dark_mode = dark_mode
        self._set_style()
    
    def _set_style(self):
        """Set consistent style for all visualizations"""
        if self.dark_mode:
            plt.style.use('dark_background')
            self.bg_color = '#1a1a1a'
            self.text_color = '#ffffff'
            self.plotly_template = 'plotly_dark'
        else:
            plt.style.use('seaborn')
            self.bg_color = '#ffffff'
            self.text_color = '#000000'
            self.plotly_template = 'plotly_white'
    
    def plot_engagement_trends(
        self, 
        df: pd.DataFrame,
        time_col: str = 'post_time',
        engagement_col: str = 'engagement_rate',
        fig_size: tuple = (12, 6),
        engine: str = 'matplotlib'
    ) -> None:
        """Plot engagement trends over time"""
        if engine == 'matplotlib':
            plt.figure(figsize=fig_size)
            df.set_index(time_col)[engagement_col].plot(
                kind='line',
                title='Engagement Rate Over Time',
                xlabel='Date',
                ylabel='Engagement Rate (%)',
                grid=True
            )
            plt.tight_layout()
            plt.show()
            
        elif engine == 'plotly':
            fig = px.line(
                df,
                x=time_col,
                y=engagement_col,
                title='Engagement Rate Over Time',
                labels={
                    time_col: 'Date',
                    engagement_col: 'Engagement Rate (%)'
                },
                template=self.plotly_template
            )
            fig.update_layout(
                hovermode='x unified',
                xaxis_title='Date',
                yaxis_title='Engagement Rate (%)'
            )
            fig.show()
    
    def plot_user_engagement_matrix(
        self,
        user_df: pd.DataFrame,
        x_col: str = 'avg_like_rate',
        y_col: str = 'avg_comment_rate',
        size_col: str = 'follower_count',
        engine: str = 'plotly'
    ) -> None:
        """Create bubble chart of user engagement metrics"""
        if engine == 'matplotlib':
            plt.figure(figsize=(10, 8))
            plt.scatter(
                user_df[x_col],
                user_df[y_col],
                s=user_df[size_col]/10,
                alpha=0.6,
                c=user_df['post_count'],
                cmap='viridis'
            )
            plt.colorbar(label='Post Count')
            plt.xlabel(x_col.replace('_', ' ').title())
            plt.ylabel(y_col.replace('_', ' ').title())
            plt.title('User Engagement Matrix')
            
            # Annotate top users
            for _, row in user_df.nlargest(5, size_col).iterrows():
                plt.annotate(
                    row['username'],
                    (row[x_col], row[y_col]),
                    textcoords="offset points",
                    xytext=(0,10),
                    ha='center'
                )
            
            plt.grid(True)
            plt.tight_layout()
            plt.show()
            
        elif engine == 'plotly':
            fig = px.scatter(
                user_df,
                x=x_col,
                y=y_col,
                size=size_col,
                color='post_count',
                hover_name='username',
                title='User Engagement Matrix',
                labels={
                    x_col: x_col.replace('_', ' ').title(),
                    y_col: y_col.replace('_', ' ').title(),
                    size_col: size_col.replace('_', ' ').title(),
                    'post_count': 'Post Count'
                },
                template=self.plotly_template
            )
            fig.update_layout(
                xaxis_title=x_col.replace('_', ' ').title(),
                yaxis_title=y_col.replace('_', ' ').title()
            )
            fig.show()
    
    def plot_thread_depth_distribution(
        self,
        thread_df: pd.DataFrame,
        engine: str = 'plotly'
    ) -> None:
        """Visualize distribution of comment thread depths"""
        if engine == 'matplotlib':
            plt.figure(figsize=(10, 6))
            thread_df['max_thread_depth'].value_counts().sort_index().plot(
                kind='bar',
                color='skyblue',
                edgecolor='black'
            )
            plt.title('Distribution of Comment Thread Depths')
            plt.xlabel('Thread Depth')
            plt.ylabel('Number of Threads')
            plt.xticks(rotation=0)
            plt.grid(axis='y')
            plt.tight_layout()
            plt.show()
            
        elif engine == 'plotly':
            depth_counts = thread_df['max_thread_depth'].value_counts().sort_index()
            fig = px.bar(
                depth_counts,
                x=depth_counts.index,
                y=depth_counts.values,
                title='Distribution of Comment Thread Depths',
                labels={
                    'x': 'Thread Depth',
                    'y': 'Number of Threads'
                },
                template=self.plotly_template
            )
            fig.update_layout(
                xaxis_title='Thread Depth',
                yaxis_title='Number of Threads',
                showlegend=False
            )
            fig.show()
    
    def plot_follower_network(
        self,
        network_data: pd.DataFrame,
        engine: str = 'plotly'
    ) -> None:
        """Visualize follower network relationships"""
        if engine == 'matplotlib':
            # Basic network visualization (matplotlib is limited for networks)
            plt.figure(figsize=(10, 8))
            
            # Create position map for nodes
            unique_users = pd.concat([
                network_data['follower_username'],
                network_data['followee_username']
            ]).unique()
            
            pos = {user: (i, i) for i, user in enumerate(unique_users)}
            
            # Draw edges
            for _, row in network_data.iterrows():
                x = [pos[row['follower_username']][0], pos[row['followee_username']][0]]
                y = [pos[row['follower_username']][1], pos[row['followee_username']][1]]
                plt.plot(x, y, 'k-', alpha=0.3)
            
            # Draw nodes
            for user, (x, y) in pos.items():
                plt.plot(x, y, 'o', markersize=15, alpha=0.6)
                plt.text(x, y, user, ha='center', va='center')
            
            plt.title('Follower Network')
            plt.axis('off')
            plt.tight_layout()
            plt.show()
            
        elif engine == 'plotly':
            # Create nodes list
            nodes = list(set(network_data['follower_username']).union(
                set(network_data['followee_username'])
            ))
            
            # Create edges
            edges = []
            for _, row in network_data.iterrows():
                edges.append((
                    nodes.index(row['follower_username']),
                    nodes.index(row['followee_username'])
                ))
            
            # Create network graph
            fig = go.Figure()
            
            # Add edges
            for edge in edges:
                fig.add_trace(go.Scatter(
                    x=[None],
                    y=[None],
                    mode='lines',
                    line=dict(width=0.5, color='#888'),
                    hoverinfo='none',
                    showlegend=False
                ))
            
            # Add nodes
            fig.add_trace(go.Scatter(
                x=[],  # Will be set in layout
                y=[],  # Will be set in layout
                mode='markers+text',
                text=nodes,
                marker=dict(
                    size=20,
                    color='LightSkyBlue',
                    line=dict(width=1, color='DarkSlateGrey')
                ),
                hoverinfo='text',
                showlegend=False
            ))
            
            # Create network layout
            fig.update_layout(
                title='Follower Network',
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20, l=5, r=5, t=40),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                template=self.plotly_template
            )
            
            # Create force-directed layout
            fig.update_layout(
                updatemenus=[dict(
                    type="buttons",
                    buttons=[dict(
                        label="Animate",
                        method="animate",
                        args=[None]
                    )]
                )]
            )
            
            fig.show()
    def plot_activity_timeline(
        self,
        timeline_df: pd.DataFrame,
        title: str = "Post Activity Timeline",
        engine: str = 'plotly'
    ) -> None:
        """Visualize the timeline of activity for a post"""
        if engine == 'matplotlib':
            plt.figure(figsize=(12, 6))
            
            # Plot comments
            comments = timeline_df[timeline_df['activity_type'] == 'comment']
            plt.scatter(
                comments['timestamp'],
                [1] * len(comments),
                c='blue',
                label='Comments',
                alpha=0.7
            )
            
            # Plot likes
            likes = timeline_df[timeline_df['activity_type'] == 'like'].drop_duplicates('timestamp')
            plt.scatter(
                likes['timestamp'],
                [0.5] * len(likes),
                c='green',
                s=likes['like_count'] * 10,
                label='Likes',
                alpha=0.5
            )
            
            plt.title(title)
            plt.xlabel('Time')
            plt.yticks([0.5, 1], ['Likes', 'Comments'])
            plt.legend()
            plt.grid(True, axis='x')
            plt.tight_layout()
            plt.show()
            
        elif engine == 'plotly':
            fig = go.Figure()
            
            # Add comments
            comments = timeline_df[timeline_df['activity_type'] == 'comment']
            fig.add_trace(go.Scatter(
                x=comments['timestamp'],
                y=['Comment'] * len(comments),
                mode='markers',
                name='Comments',
                marker=dict(
                    color='blue',
                    size=8,
                    opacity=0.7
                ),
                text=comments['username'] + ': ' + comments['content'].str.slice(0, 50),
                hoverinfo='text'
            ))
            
            # Add likes
            likes = timeline_df[timeline_df['activity_type'] == 'like'].drop_duplicates('timestamp')
            fig.add_trace(go.Scatter(
                x=likes['timestamp'],
                y=['Like'] * len(likes),
                mode='markers',
                name='Likes',
                marker=dict(
                    color='green',
                    size=likes['like_count'] * 5,
                    opacity=0.5
                ),
                text=likes['username'] + ' liked this post',
                hoverinfo='text'
            ))
            
            fig.update_layout(
                title=title,
                xaxis_title='Time',
                yaxis_title='Activity Type',
                hovermode='closest',
                template=self.plotly_template
            )
            fig.show()

    def plot_controversial_posts(
        self,
        controversial_df: pd.DataFrame,
        engine: str = 'plotly'
    ) -> None:
        """Visualize controversial posts metrics"""
        if engine == 'matplotlib':
            fig, ax = plt.subplots(figsize=(12, 6))
            
            controversial_df.set_index('post_id')[
                ['total_comments', 'unique_commenters', 'controversy_score']
            ].plot(kind='bar', ax=ax, alpha=0.7)
            
            plt.title('Controversial Posts Metrics')
            plt.xlabel('Post ID')
            plt.ylabel('Count/Score')
            plt.xticks(rotation=45)
            plt.grid(True, axis='y')
            plt.tight_layout()
            plt.show()
            
        elif engine == 'plotly':
            fig = px.bar(
                controversial_df,
                x='post_id',
                y=['total_comments', 'unique_commenters', 'controversy_score'],
                title='Controversial Posts Metrics',
                labels={
                    'post_id': 'Post ID',
                    'value': 'Count/Score',
                    'variable': 'Metric'
                },
                barmode='group',
                template=self.plotly_template
            )
            
            fig.update_layout(
                xaxis_title='Post ID',
                yaxis_title='Count/Score',
                legend_title='Metric',
                hovermode='x unified'
            )
            fig.show()    