#!/usr/bin/env python3
"""
Security Test Script for BV Backend API
Tests for missing authentication, authorization, and input validation
"""

import requests
import json
import time
from typing import Dict, Any, List

class SecurityTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.results = []
    
    def test_endpoint(self, method: str, endpoint: str, data: Dict = None, 
                     headers: Dict = None, expected_status: int = None,
                     test_name: str = "") -> Dict[str, Any]:
        """Test an endpoint and return results"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url, headers=headers)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data, headers=headers)
            elif method.upper() == "PUT":
                response = self.session.put(url, json=data, headers=headers)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, headers=headers)
            
            result = {
                "test_name": test_name,
                "method": method,
                "endpoint": endpoint,
                "status_code": response.status_code,
                "success": response.status_code < 400,
                "response_size": len(response.content),
                "has_data": len(response.content) > 0,
                "vulnerable": response.status_code == 200 and len(response.content) > 0
            }
            
            if expected_status and response.status_code != expected_status:
                result["warning"] = f"Expected {expected_status}, got {response.status_code}"
            
            return result
            
        except Exception as e:
            return {
                "test_name": test_name,
                "method": method,
                "endpoint": endpoint,
                "error": str(e),
                "success": False,
                "vulnerable": False
            }
    
    def run_security_tests(self):
        """Run comprehensive security tests"""
        print("🔍 Running Security Tests for BV Backend API")
        print("=" * 60)
        
        # Test 1: Unprotected endpoints that should require authentication
        unprotected_endpoints = [
            ("GET", "/api/contact/consultation/simple"),
            ("GET", "/api/analytics/video-view"),
            ("GET", "/api/analytics/video-view/flush-cache"),
            ("GET", "/api/vastu/categories"),
            ("GET", "/api/vastu/planetary-data"),
            ("GET", "/api/vastu/remedies"),
            ("GET", "/api/vastu/zodiac-data"),
            ("GET", "/api/vastu/chakra-points"),
            ("GET", "/api/blog/books"),
            ("GET", "/api/blog/videos"),
        ]
        
        print("\n🚨 Testing Unprotected Endpoints:")
        for method, endpoint in unprotected_endpoints:
            result = self.test_endpoint(method, endpoint, test_name=f"Unprotected {endpoint}")
            self.results.append(result)
            status = "✅ PROTECTED" if result.get("status_code") in [401, 403] else "❌ VULNERABLE"
            print(f"  {status} {method} {endpoint} - Status: {result.get('status_code')}")
        
        # Test 2: POST endpoints with malicious data
        print("\n🔍 Testing Input Validation:")
        malicious_payloads = [
            {
                "name": "<script>alert('xss')</script>",
                "email": "invalid-email",
                "message": "A" * 2000,  # Very long message
                "phone": "'; DROP TABLE users; --"
            },
            {
                "name": "",
                "email": "",
                "message": ""
            },
            {
                "name": "Test User",
                "email": "test@example.com",
                "message": "Normal message"
            }
        ]
        
        for i, payload in enumerate(malicious_payloads):
            result = self.test_endpoint(
                "POST", 
                "/api/contact/consultation/simple", 
                data=payload,
                test_name=f"Malicious Payload {i+1}"
            )
            self.results.append(result)
            status = "✅ VALIDATED" if result.get("status_code") in [400, 422] else "❌ VULNERABLE"
            print(f"  {status} Malicious Payload {i+1} - Status: {result.get('status_code')}")
        
        # Test 3: Admin-only endpoints without authentication
        print("\n🔐 Testing Admin Endpoints:")
        admin_endpoints = [
            ("POST", "/api/blog/books"),
            ("POST", "/api/blog/videos"),
            ("GET", "/api/admin/chakra-points"),
            ("GET", "/api/admin/floorplan-analyses"),
        ]
        
        for method, endpoint in admin_endpoints:
            result = self.test_endpoint(method, endpoint, test_name=f"Admin {endpoint}")
            self.results.append(result)
            status = "✅ PROTECTED" if result.get("status_code") in [401, 403] else "❌ VULNERABLE"
            print(f"  {status} {method} {endpoint} - Status: {result.get('status_code')}")
        
        # Test 4: Rate limiting
        print("\n⏱️ Testing Rate Limiting:")
        for i in range(15):  # Try to exceed rate limit
            result = self.test_endpoint(
                "GET", 
                "/api/vastu/chakra-points", 
                test_name=f"Rate Limit Test {i+1}"
            )
            if i == 14:  # Only show the last result
                status = "✅ RATE LIMITED" if result.get("status_code") == 429 else "❌ NO RATE LIMIT"
                print(f"  {status} Request {i+1} - Status: {result.get('status_code')}")
            time.sleep(0.1)  # Small delay between requests
        
        # Test 5: File upload security
        print("\n📁 Testing File Upload Security:")
        # This would require actual file upload testing
        print("  ⚠️  File upload testing requires manual verification")
        
        return self.results
    
    def generate_report(self):
        """Generate security test report"""
        print("\n" + "=" * 60)
        print("📊 SECURITY TEST REPORT")
        print("=" * 60)
        
        total_tests = len(self.results)
        vulnerable_tests = [r for r in self.results if r.get("vulnerable")]
        protected_tests = [r for r in self.results if not r.get("vulnerable")]
        
        print(f"Total Tests: {total_tests}")
        print(f"Vulnerable: {len(vulnerable_tests)}")
        print(f"Protected: {len(protected_tests)}")
        print(f"Security Score: {len(protected_tests)/total_tests*100:.1f}%")
        
        if vulnerable_tests:
            print("\n🚨 VULNERABILITIES FOUND:")
            for test in vulnerable_tests:
                print(f"  - {test['test_name']}: {test['method']} {test['endpoint']}")
        
        print("\n✅ RECOMMENDATIONS:")
        print("  1. Add authentication to all sensitive endpoints")
        print("  2. Implement proper input validation and sanitization")
        print("  3. Add rate limiting to prevent abuse")
        print("  4. Use proper authorization checks for admin endpoints")
        print("  5. Implement file upload validation and restrictions")

def main():
    """Main function to run security tests"""
    tester = SecurityTester()
    results = tester.run_security_tests()
    tester.generate_report()

if __name__ == "__main__":
    main()
