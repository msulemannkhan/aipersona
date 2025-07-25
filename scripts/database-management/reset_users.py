#!/usr/bin/env python3
"""
Script to reset all users and start fresh.

This script:
1. Deletes all users and related data
2. Creates new test users with proper roles
3. Sets up proper relationships and permissions
"""

import uuid
from sqlmodel import Session, select, delete
from app.core.db import engine
from app.core.security import get_password_hash
from app.models import (
    User, Counselor, Organization, AISoulEntity, 
    ChatMessage, PendingResponse, CounselorAction,
    RiskAssessment, TrainingDocument, TrainingMessage
)


def delete_all_users():
    """Delete all users and related data."""
    print("🗑️ Deleting all users and related data...")
    
    with Session(engine) as session:
        # Delete in proper order to avoid foreign key constraints
        
        # Delete chat messages
        session.exec(delete(ChatMessage))
        print("   ✅ Deleted chat messages")
        
        # Delete training messages
        session.exec(delete(TrainingMessage))
        print("   ✅ Deleted training messages")
        
        # Delete training documents
        session.exec(delete(TrainingDocument))
        print("   ✅ Deleted training documents")
        
        # Delete counselor actions
        session.exec(delete(CounselorAction))
        print("   ✅ Deleted counselor actions")
        
        # Delete pending responses
        session.exec(delete(PendingResponse))
        print("   ✅ Deleted pending responses")
        
        # Delete risk assessments
        session.exec(delete(RiskAssessment))
        print("   ✅ Deleted risk assessments")
        
        # Delete AI souls
        session.exec(delete(AISoulEntity))
        print("   ✅ Deleted AI souls")
        
        # Delete counselors
        session.exec(delete(Counselor))
        print("   ✅ Deleted counselors")
        
        # Delete users
        session.exec(delete(User))
        print("   ✅ Deleted users")
        
        session.commit()
        print("✅ All users and related data deleted successfully")


def create_test_users():
    """Create new test users with proper roles."""
    print("👥 Creating new test users...")
    
    with Session(engine) as session:
        # Get or create default organization
        default_org = session.exec(select(Organization)).first()
        if not default_org:
            print("🏢 Creating default organization...")
            default_org = Organization(
                name="Test Organization",
                description="Default organization for testing",
                is_active=True
            )
            session.add(default_org)
            session.commit()
            session.refresh(default_org)
        
        # Create test users
        test_users = [
            {
                "email": "admin@example.com",
                "password": "admin123",
                "full_name": "System Administrator",
                "role": "admin",
                "is_superuser": True
            },
            {
                "email": "counselor@example.com", 
                "password": "counselor123",
                "full_name": "Dr. Sarah Wilson",
                "role": "counselor",
                "is_superuser": False
            },
            {
                "email": "trainer@example.com",
                "password": "trainer123", 
                "full_name": "AI Trainer Smith",
                "role": "trainer",
                "is_superuser": False
            },
            {
                "email": "user@example.com",
                "password": "user123",
                "full_name": "John Doe",
                "role": "user", 
                "is_superuser": False
            }
        ]
        
        created_users = {}
        
        for user_data in test_users:
            user = User(
                email=user_data["email"],
                full_name=user_data["full_name"],
                hashed_password=get_password_hash(user_data["password"]),
                role=user_data["role"],
                is_superuser=user_data["is_superuser"],
                is_active=True,
                organization_id=default_org.id
            )
            session.add(user)
            session.commit()
            session.refresh(user)
            
            created_users[user_data["role"]] = user
            print(f"   ✅ Created {user_data['role']}: {user_data['email']} (password: {user_data['password']})")
        
        # Create counselor profile for counselor user
        if "counselor" in created_users:
            counselor_user = created_users["counselor"]
            counselor = Counselor(
                user_id=counselor_user.id,
                organization_id=default_org.id,
                specializations="general counseling, crisis intervention, trauma therapy",
                license_number="LCSW-12345",
                license_type="Licensed Clinical Social Worker",
                is_available=True,
                max_concurrent_cases=15
            )
            session.add(counselor)
            session.commit()
            print(f"   ✅ Created counselor profile for {counselor_user.email}")
        
        # Create sample AI soul for trainer
        if "trainer" in created_users:
            trainer_user = created_users["trainer"]
            ai_soul = AISoulEntity(
                name="Therapy Assistant",
                description="A compassionate AI assistant for mental health support",
                personality="Empathetic, professional, and supportive",
                background="Trained in cognitive behavioral therapy techniques",
                user_id=trainer_user.id
            )
            session.add(ai_soul)
            session.commit()
            print(f"   ✅ Created sample AI soul for {trainer_user.email}")
        
        print("✅ All test users created successfully")
        return created_users


def reset_database():
    """Reset the entire user database."""
    print("🔄 Resetting user database...")
    delete_all_users()
    users = create_test_users()
    
    print("\n📋 Summary of created users:")
    print("-" * 50)
    print("Email: admin@example.com | Password: admin123 | Role: Admin")
    print("Email: counselor@example.com | Password: counselor123 | Role: Counselor") 
    print("Email: trainer@example.com | Password: trainer123 | Role: Trainer")
    print("Email: user@example.com | Password: user123 | Role: User")
    print("-" * 50)
    print("✅ Database reset complete!")
    
    return users


if __name__ == "__main__":
    reset_database() 