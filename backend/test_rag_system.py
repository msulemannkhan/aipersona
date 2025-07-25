#!/usr/bin/env python3
"""
Comprehensive RAG System Test Script

This script tests all the enhanced RAG features:
1. Data isolation between AI souls
2. Enhanced chunking with maximum context
3. Vectorization and semantic search
4. Chat history integration
5. Context window management
6. RAG best practices implementation
"""

import asyncio
import json
import os
import sys
import uuid
from datetime import datetime
from typing import Any, Dict, List

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.core.config import settings
from app.core.db import engine
from app.models import AISoulEntity, TrainingDocument, TrainingMessage, User
from app.services.ai_soul_service import AISoulService
from app.services.training_service import TrainingService
from sqlmodel import Session, select


class RAGSystemTester:
    """Comprehensive RAG system tester"""
    
    def __init__(self):
        self.session = Session(engine)
        self.ai_soul_service = AISoulService()
        self.training_service = TrainingService(self.session)
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
        
    async def setup_test_data(self):
        """Set up test data for RAG testing"""
        print("\n🔧 Setting up test data...")
        
        try:
            # Create or get test user
            test_user = self.session.query(User).filter(User.email == "test@example.com").first()
            if not test_user:
                test_user = User(
                    id=uuid.uuid4(),
                    email="test@example.com",
                    hashed_password="test_password",
                    full_name="Test User",
                    is_active=True
                )
                self.session.add(test_user)
                self.session.commit()
            self.test_user_id = str(test_user.id)
            
            # Create two test AI souls for isolation testing
            ai_soul_1 = AISoulEntity(
                id=uuid.uuid4(),
                name="Test Soul 1",
                description="First test AI soul for isolation testing",
                persona_type="assistant",
                specializations="testing, isolation",
                base_prompt="You are a helpful test assistant.",
                user_id=test_user.id
            )
            
            ai_soul_2 = AISoulEntity(
                id=uuid.uuid4(),
                name="Test Soul 2", 
                description="Second test AI soul for isolation testing",
                persona_type="assistant",
                specializations="testing, isolation",
                base_prompt="You are another helpful test assistant.",
                user_id=test_user.id
            )
            
            self.session.add(ai_soul_1)
            self.session.add(ai_soul_2)
            self.session.commit()
            
            self.ai_soul_1_id = str(ai_soul_1.id)
            self.ai_soul_2_id = str(ai_soul_2.id)
            
            self.log_test("setup_test_data", True, "Created test user and 2 AI souls")
            
        except Exception as e:
            self.log_test("setup_test_data", False, f"Error: {str(e)}")
            raise
            
    async def test_training_message_creation(self):
        """Test training message creation with embeddings"""
        print("\n📝 Testing training message creation...")
        
        try:
            # Add training message to AI Soul 1
            training_msg = await self.training_service.send_training_message(
                user_id=self.test_user_id,
                ai_soul_id=self.ai_soul_1_id,
                content="My name is John Smith and I am a software engineer specializing in Python and AI.",
                is_from_trainer=True
            )
            
            # Verify message was created with embedding
            if training_msg and training_msg.embedding:
                embedding_data = json.loads(training_msg.embedding)
                if len(embedding_data) > 0:
                    self.log_test("training_message_creation", True, 
                                f"Created training message with {len(embedding_data)}-dimensional embedding")
                else:
                    self.log_test("training_message_creation", False, "Embedding is empty")
            else:
                self.log_test("training_message_creation", False, "No embedding generated")
                
        except Exception as e:
            self.log_test("training_message_creation", False, f"Error: {str(e)}")
            
    async def test_data_isolation(self):
        """Test that AI souls can only access their own training data"""
        print("\n🔒 Testing data isolation...")
        
        try:
            # Add training data to AI Soul 1
            await self.training_service.send_training_message(
                user_id=self.test_user_id,
                ai_soul_id=self.ai_soul_1_id,
                content="Soul 1 specific data: I prefer morning meetings and coffee.",
                is_from_trainer=True
            )
            
            # Add different training data to AI Soul 2
            await self.training_service.send_training_message(
                user_id=self.test_user_id,
                ai_soul_id=self.ai_soul_2_id,
                content="Soul 2 specific data: I prefer evening meetings and tea.",
                is_from_trainer=True
            )
            
            # Test that Soul 1 only gets its own data
            soul_1_data = await self.training_service.get_training_data(
                ai_soul_id=self.ai_soul_1_id,
                user_id=self.test_user_id,
                query="meeting preferences",
                limit=10
            )
            
            # Test that Soul 2 only gets its own data
            soul_2_data = await self.training_service.get_training_data(
                ai_soul_id=self.ai_soul_2_id,
                user_id=self.test_user_id,
                query="meeting preferences",
                limit=10
            )
            
            # Verify isolation
            soul_1_has_coffee = any("coffee" in item.get("content", "") for item in soul_1_data)
            soul_1_has_tea = any("tea" in item.get("content", "") for item in soul_1_data)
            soul_2_has_coffee = any("coffee" in item.get("content", "") for item in soul_2_data)
            soul_2_has_tea = any("tea" in item.get("content", "") for item in soul_2_data)
            
            if soul_1_has_coffee and not soul_1_has_tea and soul_2_has_tea and not soul_2_has_coffee:
                self.log_test("data_isolation", True, 
                            "AI souls only access their own training data")
            else:
                self.log_test("data_isolation", False, 
                            f"Data leakage detected: Soul1(coffee:{soul_1_has_coffee}, tea:{soul_1_has_tea}), Soul2(coffee:{soul_2_has_coffee}, tea:{soul_2_has_tea})")
                
        except Exception as e:
            self.log_test("data_isolation", False, f"Error: {str(e)}")
            
    async def test_semantic_search(self):
        """Test semantic search functionality"""
        print("\n🔍 Testing semantic search...")
        
        try:
            # Add diverse training content
            training_contents = [
                "I am a Python developer with 5 years of experience",
                "My favorite programming language is Python",
                "I work on machine learning projects using TensorFlow",
                "I enjoy hiking and outdoor activities on weekends",
                "My preferred IDE is Visual Studio Code"
            ]
            
            for content in training_contents:
                await self.training_service.send_training_message(
                    user_id=self.test_user_id,
                    ai_soul_id=self.ai_soul_1_id,
                    content=content,
                    is_from_trainer=True
                )
            
            # Test semantic search with different queries
            test_queries = [
                ("programming experience", "Python developer"),
                ("coding preferences", "programming language"),
                ("machine learning", "TensorFlow"),
                ("leisure activities", "hiking"),
                ("development tools", "Visual Studio Code")
            ]
            
            successful_searches = 0
            for query, expected_keyword in test_queries:
                results = await self.training_service.get_training_data(
                    ai_soul_id=self.ai_soul_1_id,
                    user_id=self.test_user_id,
                    query=query,
                    limit=3
                )
                
                # Check if relevant content was found
                relevant_found = any(
                    expected_keyword.lower() in item.get("content", "").lower()
                    for item in results
                )
                
                if relevant_found:
                    successful_searches += 1
                    
            success_rate = successful_searches / len(test_queries)
            if success_rate >= 0.8:  # 80% success rate
                self.log_test("semantic_search", True, 
                            f"Semantic search working: {successful_searches}/{len(test_queries)} queries successful")
            else:
                self.log_test("semantic_search", False, 
                            f"Poor semantic search performance: {successful_searches}/{len(test_queries)} queries successful")
                
        except Exception as e:
            self.log_test("semantic_search", False, f"Error: {str(e)}")
            
    async def test_context_window_management(self):
        """Test context window management"""
        print("\n📏 Testing context window management...")
        
        try:
            # Create a very long system prompt and messages to test context management
            long_content = "This is a very long training message. " * 100  # ~700 words
            
            # Add multiple long messages
            for i in range(5):
                await self.training_service.send_training_message(
                    user_id=self.test_user_id,
                    ai_soul_id=self.ai_soul_1_id,
                    content=f"Message {i+1}: {long_content}",
                    is_from_trainer=True
                )
            
            # Test context window management by generating a response
            try:
                response = await self.ai_soul_service.generate_ai_response(
                    session=self.session,
                    user_id=self.test_user_id,
                    ai_soul_id=self.ai_soul_1_id,
                    user_message="What can you tell me about the training messages?"
                )
                
                if response and len(response) > 0:
                    self.log_test("context_window_management", True, 
                                "Context window managed successfully, response generated")
                else:
                    self.log_test("context_window_management", False, 
                                "No response generated")
                    
            except Exception as e:
                if "token" in str(e).lower() or "context" in str(e).lower():
                    self.log_test("context_window_management", False, 
                                f"Context window overflow: {str(e)}")
                else:
                    self.log_test("context_window_management", False, 
                                f"Unexpected error: {str(e)}")
                    
        except Exception as e:
            self.log_test("context_window_management", False, f"Error: {str(e)}")
            
    async def test_chunking_strategy(self):
        """Test enhanced chunking strategy"""
        print("\n✂️ Testing chunking strategy...")
        
        try:
            # Create a test document with our test content
            test_document_path = "/tmp/test_rag_document.txt"
            with open(test_document_path, 'w') as f:
                with open("test_documents/ai_soul_knowledge_base.txt", 'r') as source:
                    f.write(source.read())
            
            # Test chunking
            chunks = self.training_service._extract_text_chunks(test_document_path)
            
            if len(chunks) > 0:
                # Analyze chunk sizes
                chunk_sizes = [len(chunk[0].split()) for chunk in chunks]
                avg_chunk_size = sum(chunk_sizes) / len(chunk_sizes)
                max_chunk_size = max(chunk_sizes)
                
                # Check if chunks are reasonably sized (target: ~1000 words)
                if 800 <= avg_chunk_size <= 1200 and max_chunk_size <= 1500:
                    self.log_test("chunking_strategy", True, 
                                f"Optimal chunking: {len(chunks)} chunks, avg size {avg_chunk_size:.0f} words")
                else:
                    self.log_test("chunking_strategy", False, 
                                f"Suboptimal chunking: avg size {avg_chunk_size:.0f} words, max {max_chunk_size}")
            else:
                self.log_test("chunking_strategy", False, "No chunks generated")
                
            # Cleanup
            os.remove(test_document_path)
            
        except Exception as e:
            self.log_test("chunking_strategy", False, f"Error: {str(e)}")
            
    async def test_rag_best_practices(self):
        """Test RAG best practices implementation"""
        print("\n🏆 Testing RAG best practices...")
        
        try:
            # Add training data with specific information
            await self.training_service.send_training_message(
                user_id=self.test_user_id,
                ai_soul_id=self.ai_soul_1_id,
                content="My name is Alice Johnson and I am a data scientist working on NLP projects.",
                is_from_trainer=True
            )
            
            # Test if the AI can use training data in responses
            response = await self.ai_soul_service.generate_ai_response(
                session=self.session,
                user_id=self.test_user_id,
                ai_soul_id=self.ai_soul_1_id,
                user_message="What is my name?"
            )
            
            # Check if response uses training data
            if response and "alice" in response.lower():
                self.log_test("rag_best_practices", True, 
                            "AI successfully uses training data in responses")
            else:
                self.log_test("rag_best_practices", False, 
                            f"AI not using training data effectively. Response: {response}")
                
        except Exception as e:
            self.log_test("rag_best_practices", False, f"Error: {str(e)}")
            
    async def cleanup_test_data(self):
        """Clean up test data"""
        print("\n🧹 Cleaning up test data...")
        
        try:
            # Delete test data
            self.session.query(TrainingMessage).filter(
                TrainingMessage.user_id == uuid.UUID(self.test_user_id)
            ).delete()
            
            self.session.query(AISoulEntity).filter(
                AISoulEntity.user_id == uuid.UUID(self.test_user_id)
            ).delete()
            
            self.session.query(User).filter(
                User.id == uuid.UUID(self.test_user_id)
            ).delete()
            
            self.session.commit()
            self.log_test("cleanup_test_data", True, "Test data cleaned up")
            
        except Exception as e:
            self.log_test("cleanup_test_data", False, f"Error: {str(e)}")
        finally:
            self.session.close()
            
    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "="*60)
        print("🧪 RAG SYSTEM TEST SUMMARY")
        print("="*60)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        print("\nDetailed Results:")
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}: {result['details']}")
            
        print("\n" + "="*60)
        
        if passed == total:
            print("🎉 ALL TESTS PASSED! RAG system is working correctly.")
        else:
            print("⚠️  Some tests failed. Please review the results above.")
            
    async def run_all_tests(self):
        """Run all RAG system tests"""
        print("🚀 Starting comprehensive RAG system tests...")
        
        try:
            await self.setup_test_data()
            await self.test_training_message_creation()
            await self.test_data_isolation()
            await self.test_semantic_search()
            await self.test_context_window_management()
            await self.test_chunking_strategy()
            await self.test_rag_best_practices()
            
        except Exception as e:
            print(f"❌ Critical error during testing: {str(e)}")
            
        finally:
            await self.cleanup_test_data()
            self.print_test_summary()


async def main():
    """Main test runner"""
    tester = RAGSystemTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main()) 