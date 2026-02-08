#!/usr/bin/env python3
"""
Initialize database and create test users
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from app.database import SessionLocal, engine, Base
from app.models.user import User
from app.core.security import hash_password

# Create all tables
print("Creating database tables...")
Base.metadata.create_all(bind=engine)
print("Database tables created!")

# Create session
db = SessionLocal()

# Check if users exist
existing_users = db.query(User).all()
print(f"\nExisting users: {len(existing_users)}")

if len(existing_users) == 0:
    print("\nCreating test users...")
    test_users = [
        {"username": "user1", "password": "pass123", "role": "USER"},
        {"username": "qa_user", "password": "pass123", "role": "QA"},
        {"username": "admin", "password": "pass123", "role": "ADMIN"},
    ]
    
    for user_data in test_users:
        user = User(
            username=user_data["username"],
            password_hash=hash_password(user_data["password"]),
            role=user_data["role"]
        )
        db.add(user)
        print(f"  Created: {user_data['username']} ({user_data['role']})")
    
    db.commit()
    print("\nTest users created successfully!")
else:
    print("\nUsers already exist:")
    for user in existing_users:
        print(f"  - {user.username} ({user.role})")

db.close()
print("\nDatabase initialization complete!")
