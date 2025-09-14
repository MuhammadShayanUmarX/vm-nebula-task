#!/usr/bin/env python3
"""
Test script for streaming endpoint
"""

import requests
import json

def test_streaming_endpoint():
    """Test the streaming chat endpoint with correct JSON format"""
    
    # Correct JSON format
    payload = {
        "query": "Write a detailed explanation of machine learning."
    }
    
    print("Testing streaming endpoint...")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(
            "http://localhost:8000/chat/stream",
            json=payload,  # This automatically sets Content-Type: application/json
            headers={
                "Accept": "text/event-stream"
            },
            stream=True
        )
        
        if response.status_code == 200:
            print("✅ Success! Streaming response:")
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    print(decoded_line)
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Connection error: {e}")

def test_regular_chat():
    """Test the regular chat endpoint for comparison"""
    
    payload = {
        "query": "Write a detailed explanation of machine learning."
    }
    
    print("\nTesting regular chat endpoint...")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(
            "http://localhost:8000/chat",
            json=payload
        )
        
        if response.status_code == 200:
            print("✅ Success! Response:")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Connection error: {e}")

if __name__ == "__main__":
    print("=== API Testing Script ===")
    
    # Test both endpoints
    test_regular_chat()
    test_streaming_endpoint()
    
    print("\n=== cURL Examples ===")
    print("\n1. Regular Chat:")
    print('''curl -X POST "http://localhost:8000/chat" \\
     -H "Content-Type: application/json" \\
     -d '{"query": "Write a detailed explanation of machine learning."}'
''')
    
    print("2. Streaming Chat:")
    print('''curl -X POST "http://localhost:8000/chat/stream" \\
     -H "Content-Type: application/json" \\
     -H "Accept: text/event-stream" \\
     -d '{"query": "Write a detailed explanation of machine learning."}'
''')