#!/usr/bin/env python3
"""
Document Upload Test Script

This script tests the document upload and processing functionality.
"""

import asyncio
import os
import sys
import uuid
from datetime import datetime

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.core.db import engine
from app.models import AISoulEntity, User
from app.services.training_service import TrainingService
from sqlmodel import Session


class MockUploadFile:
    """Mock UploadFile for testing"""
    
    def __init__(self, filename: str, content: bytes, content_type: str):
        self.filename = filename
        self.content = content
        self.content_type = content_type
        
    async def read(self):
        return self.content


async def test_document_upload():
    """Test document upload functionality"""
    print("🚀 Testing document upload functionality...")
    
    session = Session(engine)
    training_service = TrainingService(session)
    
    try:
        # Create or get test user
        test_user = session.query(User).filter(User.email == "test@example.com").first()
        if not test_user:
            test_user = User(
                id=uuid.uuid4(),
                email="test@example.com",
                hashed_password="test_password",
                full_name="Test User",
                is_active=True
            )
            session.add(test_user)
            session.commit()
        
        # Create test AI soul
        ai_soul = AISoulEntity(
            id=uuid.uuid4(),
            name="Test Soul",
            description="Test AI soul for document upload",
            persona_type="assistant",
            specializations="testing",
            base_prompt="You are a helpful test assistant.",
            user_id=test_user.id
        )
        session.add(ai_soul)
        session.commit()
        
        # Read our test document
        test_doc_path = "test_documents/ai_soul_knowledge_base.txt"
        if not os.path.exists(test_doc_path):
            print(f"❌ Test document not found: {test_doc_path}")
            return
            
        with open(test_doc_path, 'rb') as f:
            content = f.read()
            
        # Create mock upload file
        mock_file = MockUploadFile(
            filename="ai_soul_knowledge_base.txt",
            content=content,
            content_type="text/plain"
        )
        
        # Test document upload
        print("📤 Uploading test document...")
        training_doc = await training_service.upload_training_document(
            file=mock_file,
            user_id=str(test_user.id),
            ai_soul_id=str(ai_soul.id),
            description="Test knowledge base document"
        )
        
        if training_doc:
            print(f"✅ Document uploaded successfully: {training_doc.filename}")
            print(f"   File size: {training_doc.file_size} bytes")
            print(f"   Status: {training_doc.processing_status}")
            print(f"   Chunks: {training_doc.chunk_count}")
        else:
            print("❌ Document upload failed")
            
        # Test training data retrieval
        print("\n🔍 Testing training data retrieval...")
        training_data = await training_service.get_training_data(
            ai_soul_id=str(ai_soul.id),
            user_id=str(test_user.id),
            query="What is my name?",
            limit=5
        )
        
        if training_data:
            print(f"✅ Retrieved {len(training_data)} relevant training items")
            for i, item in enumerate(training_data[:3]):  # Show top 3
                print(f"   {i+1}. Similarity: {item.get('similarity', 0):.3f}")
                print(f"      Content: {item.get('content', '')[:100]}...")
        else:
            print("❌ No training data retrieved")
            
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Cleanup
        try:
            session.rollback()
            session.close()
            print("\n🧹 Test cleanup completed")
        except:
            pass


if __name__ == "__main__":
    asyncio.run(test_document_upload()) 