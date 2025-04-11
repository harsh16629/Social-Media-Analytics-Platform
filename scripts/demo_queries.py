from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.setup_db import setup_database
from analytics.engagement import EngagementAnalyzer
from analytics.network import NetworkAnalyzer
from analytics.content import ContentAnalyzer
import pandas as pd

def main():
    engine = setup_database()
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        print("=== Running Engagement Analysis ===")
        engagement_analyzer = EngagementAnalyzer(session)
        engagement_analyzer.analyze_and_visualize_engagement()
        
        print("\n=== Running Network Analysis ===")
        network_analyzer = NetworkAnalyzer(session)
        network_analyzer.analyze_and_visualize_network()
        
        print("\n=== Running Content Analysis ===")
        content_analyzer = ContentAnalyzer(session)
        content_analyzer.analyze_and_visualize_content()
        
    finally:
        session.close()

if __name__ == "__main__":
    main()