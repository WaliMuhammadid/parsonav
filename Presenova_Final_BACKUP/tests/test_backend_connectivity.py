"""
Test Backend and Frontend Connectivity
Verifies that backend APIs are working and frontend can connect

AUDIT-02: All requests now include explicit timeouts to prevent indefinite hangs.
AUDIT-10: Removed dead test_compare_documents() - /api/compare-documents is deprecated and removed from backend.
"""

import sys

# Force stdout/stderr to use UTF-8 encoding to prevent UnicodeEncodeError on Windows
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
if hasattr(sys.stderr, 'reconfigure'):
    try:
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

import requests
import json

BASE_URL = "http://localhost:5000"
# Default timeouts (seconds): connect + read
_TIMEOUT_SHORT = 5.0
_TIMEOUT_MEDIUM = 15.0
_TIMEOUT_LONG = 30.0


def test_health_check():
    """Test health check endpoint"""
    print("=" * 60)
    print("1️⃣  Testing Health Check Endpoint")
    print("=" * 60)
    try:
        response = requests.get(f"{BASE_URL}/", timeout=_TIMEOUT_SHORT)
        if response.status_code == 200:
            print(f"✅ Status Code: {response.status_code}")
            print(f"✅ Response: {response.json()}")
            print("✅ PASS: Backend is running and responding\n")
            return True
        else:
            print(f"❌ Status Code: {response.status_code}")
            print(f"❌ FAIL: Unexpected status code\n")
            return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print(f"❌ FAIL: Could not connect to backend\n")
        return False


def test_analyze_document():
    """Test document analysis endpoint"""
    print("=" * 60)
    print("2️⃣  Testing Document Analysis Endpoint")
    print("=" * 60)
    try:
        # Create a test file
        test_content = b"This is a test document for analysis."
        files = {'file': ('test.txt', test_content)}

        response = requests.post(
            f"{BASE_URL}/api/analyze-document",
            files=files,
            timeout=_TIMEOUT_LONG,
        )
        if response.status_code == 200:
            print(f"✅ Status Code: {response.status_code}")
            result = response.json()
            print(f"✅ Response Keys: {list(result.keys())}")
            print(f"✅ Overall Score: {result.get('overall_score', 'N/A')}")
            print("✅ PASS: Document analysis endpoint working\n")
            return True
        else:
            print(f"❌ Status Code: {response.status_code}")
            print(f"❌ Response: {response.text}")
            print(f"❌ FAIL: Document analysis failed\n")
            return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print(f"❌ FAIL: Could not test document analysis\n")
        return False


def test_analyze_speech():
    """Test speech analysis endpoint"""
    print("=" * 60)
    print("3️⃣  Testing Speech Analysis Endpoint")
    print("=" * 60)
    try:
        payload = {
            "text": "This is a test speech. Um, I like to, you know, basically explain this. Actually, this is working great.",
            "duration_seconds": 15
        }

        response = requests.post(
            f"{BASE_URL}/api/analyze-speech",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=_TIMEOUT_MEDIUM,
        )
        if response.status_code == 200:
            print(f"✅ Status Code: {response.status_code}")
            result = response.json()
            print(f"✅ Response Keys: {list(result.keys())}")
            print(f"✅ Word Count: {result.get('word_count', 'N/A')}")
            print(f"✅ Filler Words: {result.get('filler_words_count', 'N/A')}")
            print("✅ PASS: Speech analysis endpoint working\n")
            return True
        else:
            print(f"❌ Status Code: {response.status_code}")
            print(f"❌ Response: {response.text}")
            print(f"❌ FAIL: Speech analysis failed\n")
            return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print(f"❌ FAIL: Could not test speech analysis\n")
        return False


def test_practice_chat():
    """Test practice chat endpoint"""
    print("=" * 60)
    print("4️⃣  Testing Practice Chat Endpoint")
    print("=" * 60)
    try:
        payload = {
            "message": "How can I improve my presentation skills?",
            "history": [],
            "contextReport": {}
        }

        response = requests.post(
            f"{BASE_URL}/api/practice-chat",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=_TIMEOUT_MEDIUM,
        )
        if response.status_code == 200:
            print(f"✅ Status Code: {response.status_code}")
            result = response.json()
            print(f"✅ Response Keys: {list(result.keys())}")
            print(f"✅ AI Response: {result.get('ai_response', 'N/A')[:100]}...")
            print("✅ PASS: Practice chat endpoint working\n")
            return True
        else:
            print(f"❌ Status Code: {response.status_code}")
            print(f"❌ Response: {response.text}")
            print(f"❌ FAIL: Practice chat failed\n")
            return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print(f"❌ FAIL: Could not test practice chat\n")
        return False

# NOTE: test_compare_documents() removed (AUDIT-10).
# The /api/compare-documents endpoint has been deprecated and removed from the
# backend (phase_two.py) while the frontend comparison wizard was also removed.
# Keeping this test would produce a guaranteed 404 failure on every run.


def check_frontend_config():
    """Check frontend configuration"""
    print("=" * 60)
    print("5️⃣  Checking Frontend Configuration")
    print("=" * 60)
    try:
        with open("frontend/.env", "r") as f:
            content = f.read()
            print("✅ Frontend .env file found:")
            print(content)
            if "http://localhost:5000" in content:
                print("✅ PASS: Frontend correctly configured to connect to backend\n")
                return True
            else:
                print("❌ FAIL: Frontend API URL not configured correctly\n")
                return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print(f"❌ FAIL: Could not check frontend config\n")
        return False


def main():
    print("\n")
    print("█" * 60)
    print("  BACKEND & FRONTEND CONNECTIVITY TEST")
    print("█" * 60)
    print("\n")

    results = []
    results.append(("Health Check", test_health_check()))
    results.append(("Document Analysis", test_analyze_document()))
    results.append(("Speech Analysis", test_analyze_speech()))
    results.append(("Practice Chat", test_practice_chat()))
    results.append(("Frontend Config", check_frontend_config()))

    print("=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All connectivity tests passed! Backend and Frontend are properly connected!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the errors above.")

    print("\n")


try:
    import pytest

    @pytest.fixture
    def app():
        from main import create_app
        test_app = create_app()
        test_app.config['TESTING'] = True
        return test_app

    @pytest.fixture
    def client(app):
        return app.test_client()

    def test_flask_health_endpoint(client):
        res = client.get('/')
        assert res.status_code == 200
        data = res.get_json()
        assert data.get('status') == 'running'
except ImportError:
    pass


if __name__ == "__main__":
    main()
