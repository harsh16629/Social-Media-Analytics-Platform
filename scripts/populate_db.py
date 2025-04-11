from sqlalchemy.orm import sessionmaker
from database.models import User, Post, Comment, Like, Follow
from database.setup_db import setup_database
from datetime import datetime, timedelta
import random

def populate_sample_data():
    engine = setup_database()
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Clear existing data
        session.query(Like).delete()
        session.query(Comment).delete()
        session.query(Post).delete()
        session.query(Follow).delete()
        session.query(User).delete()
        
        # Create users
        users = [
            User(username='alice_smith', full_name='Alice Smith', email='alice@example.com'),
            User(username='bob_jones', full_name='Bob Jones', email='bob@example.com'),
            User(username='charlie_brown', full_name='Charlie Brown', email='charlie@example.com'),
            User(username='diana_ross', full_name='Diana Ross', email='diana@example.com'),
            User(username='evan_garcia', full_name='Evan Garcia', email='evan@example.com')
        ]
        session.add_all(users)
        session.commit()
        
        # Create posts with varying dates
        posts = []
        for i, user in enumerate(users):
            for j in range(1, 4):  # 3 posts per user
                post_time = datetime.utcnow() - timedelta(days=random.randint(0, 30))
                posts.append(
                    Post(
                        user_id=user.user_id,
                        post_text=f"Sample post {j} from {user.username}",
                        post_time=post_time
                    )
                )
        session.add_all(posts)
        session.commit()
        
        # Create follows
        follows = [
            Follow(follower_id=users[1].user_id, followee_id=users[0].user_id),
            Follow(follower_id=users[2].user_id, followee_id=users[0].user_id),
            Follow(follower_id=users[3].user_id, followee_id=users[0].user_id),
            Follow(follower_id=users[4].user_id, followee_id=users[0].user_id),
            Follow(follower_id=users[0].user_id, followee_id=users[1].user_id),
            Follow(follower_id=users[2].user_id, followee_id=users[1].user_id),
            Follow(follower_id=users[0].user_id, followee_id=users[2].user_id),
            Follow(follower_id=users[1].user_id, followee_id=users[2].user_id),
            Follow(follower_id=users[3].user_id, followee_id=users[2].user_id),
            Follow(follower_id=users[0].user_id, followee_id=users[4].user_id)
        ]
        session.add_all(follows)
        session.commit()
        
        # Create comments with hierarchy
        comments = []
        for post in posts[:5]:  # Add comments to first 5 posts
            for i in range(3):  # 3 top-level comments per post
                comment = Comment(
                    post_id=post.post_id,
                    user_id=random.choice(users).user_id,
                    comment_text=f"Comment {i+1} on post {post.post_id}"
                )
                comments.append(comment)
                session.add(comment)
                session.flush()  # Get the comment_id
                
                # Add 1-2 replies to each comment
                for j in range(random.randint(1, 2)):
                    reply = Comment(
                        post_id=post.post_id,
                        user_id=random.choice(users).user_id,
                        parent_comment_id=comment.comment_id,
                        comment_text=f"Reply {j+1} to comment {comment.comment_id}"
                    )
                    comments.append(reply)
        session.add_all(comments)
        session.commit()
        
        # Create likes
        likes = []
        for post in posts:
            likers = random.sample(users, random.randint(1, len(users)))
            for user in likers:
                likes.append(
                    Like(
                        post_id=post.post_id,
                        user_id=user.user_id
                    )
                )
        session.add_all(likes)
        session.commit()
        
        print("Sample data populated successfully")
        
    except Exception as e:
        session.rollback()
        print(f"Error populating data: {e}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    populate_sample_data()