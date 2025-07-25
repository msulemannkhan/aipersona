#!/usr/bin/env python3
"""
Script to fix counselor permission issues.

This script:
1. Finds users with counselor role but no counselor record
2. Creates counselor records for them
3. Ensures proper organization assignment
"""

import asyncio
import uuid
from datetime import datetime
from sqlmodel import Session, select
from app.core.db import engine
from app.models import User, Counselor, Organization


def fix_counselor_permissions():
    """Fix counselor permission issues."""
    print("🔧 Fixing counselor permission issues...")
    
    with Session(engine) as session:
        # Check users with counselor role
        counselor_users = session.exec(select(User).where(User.role == 'counselor')).all()
        print(f"📊 Found {len(counselor_users)} users with counselor role")
        
        if not counselor_users:
            print("✅ No users with counselor role found")
            return
        
        # Check actual counselor records
        counselors = session.exec(select(Counselor)).all()
        existing_counselor_user_ids = {str(c.user_id) for c in counselors}
        
        print(f"📊 Found {len(counselors)} existing counselor records")
        
        # Get default organization (create if needed)
        default_org = session.exec(select(Organization)).first()
        if not default_org:
            print("🏢 Creating default organization...")
            default_org = Organization(
                name="Default Organization",
                description="Default organization for counselors",
                is_active=True
            )
            session.add(default_org)
            session.commit()
            session.refresh(default_org)
        
        # Create missing counselor records
        created_count = 0
        for user in counselor_users:
            if str(user.id) not in existing_counselor_user_ids:
                print(f"👩‍⚕️ Creating counselor record for {user.full_name} ({user.email})")
                
                # Update user organization if not set
                if not user.organization_id:
                    user.organization_id = default_org.id
                    session.add(user)
                
                # Create counselor record
                counselor = Counselor(
                    user_id=user.id,
                    organization_id=user.organization_id or default_org.id,
                    specializations="general counseling, crisis intervention",
                    license_number=f"AUTO-{str(uuid.uuid4())[:8].upper()}",
                    license_type="Licensed Professional Counselor",
                    is_available=True,
                    max_concurrent_cases=10
                )
                session.add(counselor)
                created_count += 1
        
        if created_count > 0:
            session.commit()
            print(f"✅ Created {created_count} counselor records")
        else:
            print("✅ All counselor users already have counselor records")
        
        # Verify the fix
        print("\n🔍 Verification:")
        counselor_users_after = session.exec(select(User).where(User.role == 'counselor')).all()
        counselors_after = session.exec(select(Counselor)).all()
        
        print(f"📊 Users with counselor role: {len(counselor_users_after)}")
        print(f"📊 Counselor records: {len(counselors_after)}")
        
        # Check for any remaining mismatches
        mismatches = []
        for user in counselor_users_after:
            counselor_record = session.exec(select(Counselor).where(Counselor.user_id == user.id)).first()
            if not counselor_record:
                mismatches.append(user)
        
        if mismatches:
            print(f"❌ Still have {len(mismatches)} mismatches:")
            for user in mismatches:
                print(f"  - {user.full_name} ({user.email})")
        else:
            print("✅ All counselor users now have proper counselor records")


if __name__ == "__main__":
    fix_counselor_permissions() 