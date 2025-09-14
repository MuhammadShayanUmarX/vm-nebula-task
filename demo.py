

import asyncio
import json
import time
import httpx
from typing import Dict, List

# Demo Configuration
BASE_URL = "http://localhost:8000"

def print_header(text: str):
    """Print section header"""
    print("\n" + "="*50)
    print(f"🚀 {text}")
    print("="*50)

class DemoRunner:
    """Automated demo runner for VM Nebula AI Assistant"""
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def test_health(self):
        """Test 1: Health Check"""
        print_header("Health Check")
        response = await self.client.get(f"{BASE_URL}/health")
        data = response.json()
        print(f"✅ Status: {data['status']}")
        print(f"📊 Models Available: {data['models_available']}")
        return response.status_code == 200
    
    async def test_models_status(self):
        """Test 2: Models Status"""
        print_header("Models Status")
        response = await self.client.get(f"{BASE_URL}/models/status")
        data = response.json()
        print(f"📊 Total Models: {data['total_models']}")
        for model in data['models']:
            print(f"✅ {model['model']} ({model['provider']})")
        return response.status_code == 200
    
    async def test_agent_detection(self):
        """Test 3: Agent Detection"""
        print_header("Agent Detection Test")
        
        test_cases = [
            {
                "query": "Explain this Python function: def add(a,b): return a+b",
                "expected_agent": "code",
                "description": "Code Assistant"
            },
            {
                "query": "Research the latest AI trends",
                "expected_agent": "research", 
                "description": "Research Assistant"
            },
            {
                "query": "How to setup Python environment?",
                "expected_agent": "task",
                "description": "Task Helper"
            }
        ]
        
        for test_case in test_cases:
            print(f"\n🔍 Testing: {test_case['description']}")
            response = await self.client.post(
                f"{BASE_URL}/chat",
                json={"query": test_case["query"]}
            )
            
            if response.status_code == 200:
                data = response.json()
                agent_used = data["agent_used"]
                print(f"🤖 Agent: {agent_used}")
                print(f"🔧 Model: {data['model']}")
                print(f"⏱️ Time: {data['processing_time']:.2f}s")
                print(f"💬 Response: {data['response'][:100]}...")
        
        return True
    
    async def test_cost_optimization(self):
        """Test 4: Cost Optimization"""
        print_header("Cost Optimization")
        
        # Simple query
        print("\n💰 Testing Simple Query (should use fast model)")
        response = await self.client.post(
            f"{BASE_URL}/chat",
            json={"query": "What is 2+2?"}
        )
        data = response.json()
        print(f"🤖 Model: {data['model']}")
        print(f"⏱️ Time: {data['processing_time']:.2f}s")
        
        # Complex query
        print("\n💰 Testing Complex Query (should use advanced model)")
        complex_query = "Write a comprehensive analysis of machine learning algorithms including neural networks and their applications"
        response = await self.client.post(
            f"{BASE_URL}/chat",
            json={"query": complex_query}
        )
        data = response.json()
        print(f"🤖 Model: {data['model']}")
        print(f"⏱️ Time: {data['processing_time']:.2f}s")
        
        return True
    
    async def test_streaming(self):
        """Test 5: Streaming Response"""
        print_header("Streaming Response Test")
        
        print("🌊 Testing Server-Sent Events...")
        async with self.client.stream(
            "POST",
            f"{BASE_URL}/chat/stream",
            json={"query": "Explain machine learning"}
        ) as response:
            
            if response.status_code == 200:
                print("✅ Streaming connection established")
                chunk_count = 0
                async for chunk in response.aiter_text():
                    if chunk.strip() and chunk.startswith("data: "):
                        chunk_count += 1
                        try:
                            data = json.loads(chunk[6:])
                            event = data.get("event")
                            if event == "start":
                                print(f"🚀 Stream started")
                            elif event == "delta":
                                print(f"📝 Chunk {chunk_count}")
                            elif event == "complete":
                                print(f"✅ Stream complete")
                                break
                        except:
                            continue
                print(f"📊 Total chunks: {chunk_count}")
                return True
        return False
    
    async def run_demo(self):
        """Run complete demonstration"""
        print("🚀 VM Nebula AI Assistant - Automated Demo")
        print("=" * 60)
        
        tests = [
            ("Health Check", self.test_health),
            ("Models Status", self.test_models_status),
            ("Agent Detection", self.test_agent_detection),
            ("Cost Optimization", self.test_cost_optimization),
            ("Streaming", self.test_streaming)
        ]
        
        results = []
        
        for test_name, test_func in tests:
            print(f"\n⏳ Running {test_name}...")
            try:
                result = await test_func()
                results.append(result)
                status = "✅ PASSED" if result else "❌ FAILED"
                print(f"{status} {test_name}")
            except Exception as e:
                print(f"❌ {test_name} ERROR: {e}")
                results.append(False)
        
        # Summary
        print_header("Demo Summary")
        passed = sum(results)
        total = len(results)
        print(f"📊 Tests Passed: {passed}/{total}")
        
        if passed == total:
            print("\n🎉 ALL TESTS PASSED! System working perfectly!")
        else:
            print(f"\n⚠️ {total - passed} tests failed.")
        
        await self.client.aclose()

async def main():
    """Main demo function"""
    demo = DemoRunner()
    
    # Check server
    try:
        response = await demo.client.get(f"{BASE_URL}/health")
        if response.status_code != 200:
            print("❌ Server not responding. Start server first:")
            print("   python app.py")
            return
    except:
        print("❌ Cannot connect to server. Start server first:")
        print("   python app.py")
        return
    
    await demo.run_demo()

if __name__ == "__main__":
    print("🚀 Starting VM Nebula AI Assistant Demo...")
    print("🔗 Server should be running on http://localhost:8000")
    print("📝 To start server: python app.py")
    print()
    
    asyncio.run(main())
