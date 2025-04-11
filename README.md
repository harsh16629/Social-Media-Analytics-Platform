# Social Media Analytics Platform

A comprehensive SQL and Python-based analytics platform for social media data, featuring advanced engagement metrics, network analysis, and content performance tracking with interactive visualizations.

# Features
- Engagement Analytics: Track post performance, user engagement rates, and content trends
- Network Analysis: Identify ghost followers, analyze follower networks, and recommend connections
- Content Insights: Measure comment thread depth, detect controversial posts, and analyze activity patterns
- Interactive Visualizations: Beautiful Plotly and Matplotlib charts for data exploration
- Database Backend: SQLAlchemy ORM with optimized PostgreSQL schema

# Technology Stack
- Backend: Python 3.8+
- Database: PostgreSQL (with SQLAlchemy ORM)
- Visualization: Plotly, Matplotlib
- Data Processing: Pandas, NumPy
- Environment Management: Python-dotenv

# Installation
1. Clone the repository:

```bash
git clone https://github.com/yourusername/social-media-analytics.git
cd social-media-analytics
```

2. Set up a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Configure your database:

- Create a .env file based on .env.example
- Update with your PostgreSQL credentials

5. Initialize the database:

```bash
python -m scripts.populate_db
```

# Project Structure

```bash
social-media-analytics/
├── database/               # Database models and setup
│   ├── __init__.py
│   ├── models.py           # SQLAlchemy ORM models
│   ├── queries.py          # Raw SQL queries
│   └── setup_db.py         # Database initialization
│
├── analytics/              # Analysis modules
│   ├── __init__.py
│   ├── content.py          # Content performance analysis
│   ├── engagement.py       # Engagement metrics
│   ├── network.py          # Follower network analysis
│   └── visualization.py    # Visualization components
│
├── scripts/                # Utility scripts
│   ├── populate_db.py      # Sample data generation
│   └── demo_queries.py     # Demonstration of features
│
├── config.py               # Application configuration
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

# Usage
Run the demo script to see all analytics features with sample data:

```bash
python scripts/demo_queries.py
```

This will generate:

- Engagement metrics and visualizations
- Network analysis and follower graphs
- Content performance reports
- Interactive visualizations in your browser

# Custom Implementation
Import the analytics modules into your own application:

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from analytics.engagement import EngagementAnalyzer

# Initialize database connection
engine = create_engine("your_database_uri")
Session = sessionmaker(bind=engine)
session = Session()

# Analyze engagement
analyzer = EngagementAnalyzer(session)
engagement_data = analyzer.get_post_engagement(days=30)

# Generate visualizations
analyzer.analyze_and_visualize_engagement()
```
# Sample Visualizations
- Engagement Trends
- Network Graph
- Thread Analysis

# Contributing
Contributions are welcome! Please follow these steps:

Fork the repository
- Create your feature branch (git checkout -b feature/your-feature)
- Commit your changes (git commit -am 'Add some feature')
- Push to the branch (git push origin feature/your-feature)
- Open a Pull Request

# License
This project is licensed under the [MIT License](LICENSE).