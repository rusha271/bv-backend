#!/usr/bin/env python3
"""
Test script to verify all imports work correctly
"""

def test_imports():
    """Test all critical imports"""
    try:
        print("Testing imports...")
        
        # Test core security imports
        from app.core.security import rate_limit_dependency, security_validation_dependency
        print("✅ Security imports successful")
        
        # Test API imports
        from app.api.contact import router as contact_router
        print("✅ Contact router import successful")
        
        from app.api.analytics import router as analytics_router
        print("✅ Analytics router import successful")
        
        from app.api.blog import router as blog_router
        print("✅ Blog router import successful")
        
        from app.api.auth import router as auth_router
        print("✅ Auth router import successful")
        
        from app.api.users import router as users_router
        print("✅ Users router import successful")
        
        from app.api.vastu import router as vastu_router
        print("✅ Vastu router import successful")
        
        # Test main app
        from app.main import app
        print("✅ Main app import successful")
        
        print("\n🎉 All imports successful! Server should start without errors.")
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

if __name__ == "__main__":
    test_imports()
