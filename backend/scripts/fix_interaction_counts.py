#!/usr/bin/env python3
"""
Script to fix interaction counts for AI souls.
Interaction count should represent conversation pairs (user message + AI response), not individual messages.
"""

import sys
import os
from pathlib import Path

# Add the parent directory to the Python path so we can import from app
sys.path.append(str(Path(__file__).parent.parent))

from sqlmodel import Session, select, func
from app.core.db import engine
from app.models import AISoulEntity, ChatMessage, TrainingMessage


def fix_interaction_counts():
    """
    Recalculate interaction counts for all AI souls based on actual conversation pairs.
    1 interaction = 1 user message + 1 AI response (for both chat and training)
    """
    
    with Session(engine) as session:
        # Get all AI souls
        ai_souls = session.exec(select(AISoulEntity)).all()
        
        print(f"Found {len(ai_souls)} AI souls to update...")
        
        for ai_soul in ai_souls:
            print(f"\nProcessing AI Soul: {ai_soul.name} (ID: {ai_soul.id})")
            
            # Count chat message pairs
            # Count user messages in chat (each user message typically gets an AI response)
            chat_user_messages = session.exec(
                select(func.count(ChatMessage.id)).where(
                    ChatMessage.ai_soul_id == ai_soul.id,
                    ChatMessage.is_from_user == True
                )
            ).one()
            
            # Count training message pairs
            # Count trainer messages (each trainer message typically gets an AI response)
            training_user_messages = session.exec(
                select(func.count(TrainingMessage.id)).where(
                    TrainingMessage.ai_soul_id == ai_soul.id,
                    TrainingMessage.is_from_trainer == True
                )
            ).one()
            
            # Calculate total interactions (conversation pairs)
            total_interactions = chat_user_messages + training_user_messages
            
            print(f"  - Chat user messages: {chat_user_messages}")
            print(f"  - Training user messages: {training_user_messages}")
            print(f"  - Total interactions: {total_interactions}")
            print(f"  - Current interaction_count: {ai_soul.interaction_count}")
            
            # Update the interaction count
            ai_soul.interaction_count = total_interactions
            session.add(ai_soul)
            
            print(f"  - Updated interaction_count to: {total_interactions}")
        
        # Commit all changes
        session.commit()
        print(f"\n✅ Successfully updated interaction counts for {len(ai_souls)} AI souls!")


def verify_counts():
    """
    Verify the updated counts by showing a summary.
    """
    
    with Session(engine) as session:
        # Get summary statistics
        total_ai_souls = session.exec(select(func.count(AISoulEntity.id))).one()
        total_chat_messages = session.exec(select(func.count(ChatMessage.id))).one()
        total_training_messages = session.exec(select(func.count(TrainingMessage.id))).one()
        total_interactions = session.exec(select(func.sum(AISoulEntity.interaction_count))).one() or 0
        
        print("\n" + "="*50)
        print("VERIFICATION SUMMARY")
        print("="*50)
        print(f"Total AI Souls: {total_ai_souls}")
        print(f"Total Chat Messages: {total_chat_messages}")
        print(f"Total Training Messages: {total_training_messages}")
        print(f"Total Interactions (sum of all AI souls): {total_interactions}")
        print(f"Expected Interactions (rough estimate): ~{(total_chat_messages + total_training_messages) // 2}")
        
        # Show individual AI soul counts
        ai_souls = session.exec(select(AISoulEntity)).all()
        print(f"\nIndividual AI Soul Interaction Counts:")
        for ai_soul in ai_souls:
            print(f"  - {ai_soul.name}: {ai_soul.interaction_count} interactions")


if __name__ == "__main__":
    print("🔧 Fixing AI Soul interaction counts...")
    print("This script will recalculate interaction counts based on conversation pairs.")
    print("1 interaction = 1 user message + 1 AI response\n")
    
    try:
        fix_interaction_counts()
        verify_counts()
        
        print("\n🎉 Interaction count fix completed successfully!")
        print("The interaction counts now properly represent conversation pairs.")
        
    except Exception as e:
        print(f"\n❌ Error fixing interaction counts: {e}")
        sys.exit(1) 