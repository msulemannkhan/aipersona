#!/usr/bin/env python3
"""
Script to create comprehensive test data for the system.

This script:
1. Creates test users with proper roles
2. Creates test AI souls
3. Creates test pending responses for counselor dashboard
4. Creates test chat messages and risk assessments
"""

import uuid
import json
from datetime import datetime, timedelta
from sqlmodel import Session, select
from app.core.db import engine
from app.core.security import get_password_hash
from app.models import (
    User, Counselor, Organization, AISoulEntity, 
    ChatMessage, PendingResponse, RiskAssessment
)


def create_comprehensive_test_data():
    """Create comprehensive test data for the system."""
    print("🚀 Creating comprehensive test data...")
    
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
            },
            {
                "email": "testuser@example.com",
                "password": "test123",
                "full_name": "Test User",
                "role": "user", 
                "is_superuser": False
            }
        ]
        
        created_users = {}
        
        for user_data in test_users:
            # Check if user already exists
            existing_user = session.exec(
                select(User).where(User.email == user_data["email"])
            ).first()
            
            if existing_user:
                created_users[user_data["role"]] = existing_user
                print(f"   ✅ User already exists: {user_data['email']}")
                continue
                
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
            print(f"   ✅ Created {user_data['role']}: {user_data['email']}")
        
        # Create counselor profile for counselor user
        counselor_user = created_users.get("counselor")
        if counselor_user:
            existing_counselor = session.exec(
                select(Counselor).where(Counselor.user_id == counselor_user.id)
            ).first()
            
            if not existing_counselor:
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
                session.refresh(counselor)
                print(f"   ✅ Created counselor profile for {counselor_user.email}")
            else:
                counselor = existing_counselor
                print(f"   ✅ Counselor profile already exists for {counselor_user.email}")
        
        # Create sample AI soul for trainer
        trainer_user = created_users.get("trainer")
        if trainer_user:
            existing_soul = session.exec(
                select(AISoulEntity).where(AISoulEntity.user_id == trainer_user.id)
            ).first()
            
            if not existing_soul:
                ai_soul = AISoulEntity(
                    name="Therapy Assistant",
                    description="A compassionate AI assistant for mental health support",
                    personality="Empathetic, professional, and supportive",
                    background="Trained in cognitive behavioral therapy techniques",
                    user_id=trainer_user.id
                )
                session.add(ai_soul)
                session.commit()
                session.refresh(ai_soul)
                print(f"   ✅ Created sample AI soul for {trainer_user.email}")
            else:
                ai_soul = existing_soul
                print(f"   ✅ AI soul already exists for {trainer_user.email}")
        
        # Create test chat messages and pending responses
        regular_user = created_users.get("user")
        if regular_user and counselor and ai_soul:
            print("   🔄 Creating test chat messages and pending responses...")
            
            # Create test chat messages
            test_messages = [
                {
                    "content": "I've been feeling really overwhelmed lately and having trouble sleeping.",
                    "risk_level": "medium",
                    "ai_response": "I understand you're feeling overwhelmed and having sleep difficulties. These feelings are valid and it's important that you reached out. Can you tell me more about what's been contributing to these feelings of being overwhelmed?"
                },
                {
                    "content": "I sometimes think about hurting myself when things get really bad.",
                    "risk_level": "high", 
                    "ai_response": "I'm very concerned about what you've shared. These thoughts about self-harm are serious, and I want you to know that you're not alone. There are people who want to help you through this difficult time."
                },
                {
                    "content": "I can't take this anymore. I have a plan and I'm going to end it all tonight.",
                    "risk_level": "critical",
                    "ai_response": "I'm extremely concerned about your safety right now. What you're feeling is temporary, but ending your life is permanent. Please reach out for immediate help - you deserve support and care."
                }
            ]
            
            for i, msg_data in enumerate(test_messages):
                # Create user chat message
                user_message = ChatMessage(
                    content=msg_data["content"],
                    user_id=regular_user.id,
                    ai_soul_id=ai_soul.id,
                    is_from_user=True,
                    timestamp=datetime.utcnow() - timedelta(hours=i+1)
                )
                session.add(user_message)
                session.commit()
                session.refresh(user_message)
                
                # Create risk assessment
                risk_categories = []
                if msg_data["risk_level"] == "medium":
                    risk_categories = ["mental_health_crisis", "sleep_disturbance"]
                elif msg_data["risk_level"] == "high":
                    risk_categories = ["self_harm", "mental_health_crisis"]
                elif msg_data["risk_level"] == "critical":
                    risk_categories = ["suicide", "self_harm", "mental_health_crisis"]
                
                risk_assessment = RiskAssessment(
                    chat_message_id=user_message.id,
                    user_id=regular_user.id,
                    ai_soul_id=ai_soul.id,
                    organization_id=default_org.id,
                    risk_level=msg_data["risk_level"],
                    risk_categories=json.dumps(risk_categories),
                    confidence_score=0.8 + (i * 0.1),
                    reasoning=f"Analysis indicates {msg_data['risk_level']} risk based on content and context",
                    requires_human_review=msg_data["risk_level"] in ["high", "critical"],
                    auto_response_blocked=msg_data["risk_level"] == "critical"
                )
                session.add(risk_assessment)
                session.commit()
                session.refresh(risk_assessment)
                
                # Create pending response if human review is required
                if risk_assessment.requires_human_review:
                    priority = "urgent" if msg_data["risk_level"] == "critical" else "high"
                    
                    pending_response = PendingResponse(
                        chat_message_id=str(user_message.id),
                        risk_assessment_id=str(risk_assessment.id),
                        user_id=regular_user.id,
                        ai_soul_id=ai_soul.id,
                        organization_id=default_org.id,
                        original_user_message=msg_data["content"],
                        ai_generated_response=msg_data["ai_response"],
                        priority=priority,
                        assigned_counselor_id=counselor.id,
                        response_time_limit=datetime.utcnow() + timedelta(hours=2),
                        status="pending"
                    )
                    session.add(pending_response)
                    session.commit()
                    
                    print(f"      ✅ Created {priority} priority pending response")
                else:
                    # Create AI response message for low/medium risk
                    ai_message = ChatMessage(
                        content=msg_data["ai_response"],
                        user_id=regular_user.id,
                        ai_soul_id=ai_soul.id,
                        is_from_user=False,
                        timestamp=datetime.utcnow() - timedelta(hours=i+1) + timedelta(minutes=5)
                    )
                    session.add(ai_message)
                    session.commit()
                    print(f"      ✅ Created AI response for {msg_data['risk_level']} risk message")
        
        print("✅ Comprehensive test data created successfully!")
        print("\n📋 Summary:")
        print("-" * 50)
        print("Users created:")
        print("  - admin@example.com (password: admin123) - Admin")
        print("  - counselor@example.com (password: counselor123) - Counselor") 
        print("  - trainer@example.com (password: trainer123) - Trainer")
        print("  - user@example.com (password: user123) - User")
        print("  - testuser@example.com (password: test123) - User")
        print("\nTest data:")
        print("  - 1 AI Soul (Therapy Assistant)")
        print("  - 3 Chat messages with different risk levels")
        print("  - 2 Pending responses for counselor review")
        print("  - Risk assessments for all messages")
        print("-" * 50)


if __name__ == "__main__":
    create_comprehensive_test_data() 