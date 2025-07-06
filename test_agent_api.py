#!/usr/bin/env python3
"""
Test script for the LangChain Agent API
"""

import requests
import json
import time

class AgentAPITester:
    def __init__(self, base_url="http://localhost:1337", api_key="test-key"):
        self.base_url = base_url
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
    
    def test_get_tools(self):
        """Test getting available tools"""
        print("Testing GET /v1/agent/tools...")
        try:
            response = requests.get(f"{self.base_url}/v1/agent/tools", headers=self.headers)
            if response.status_code == 200:
                tools = response.json()
                print(f"✅ Success! Found {tools['total']} tools:")
                for tool in tools['tools']:
                    print(f"  - {tool['name']}: {tool['description']}")
                return True
            else:
                print(f"❌ Failed with status {response.status_code}: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def test_simple_agent(self):
        """Test simple agent execution"""
        print("\nTesting POST /v1/agent/run (simple)...")
        data = {
            "input": "What is 2 + 2?",
            "config": {
                "agent_type": "zero-shot-react-description",
                "tools": [],
                "verbose": False,
                "max_iterations": 3
            }
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/v1/agent/run",
                headers=self.headers,
                json=data
            )
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Success! Output: {result['output']}")
                print(f"   Execution time: {result.get('execution_time', 'N/A')}s")
                return True
            else:
                print(f"❌ Failed with status {response.status_code}: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def test_search_agent(self):
        """Test agent with search tool"""
        print("\nTesting POST /v1/agent/run (with search)...")
        data = {
            "input": "What is 2 + 2?",
            "config": {
                "agent_type": "zero-shot-react-description",
                "tools": ["duckduckgo_search"],
                "verbose": False,
                "max_iterations": 3,
                "model": "gpt-4o"
            }
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/v1/agent/run",
                headers=self.headers,
                json=data
            )
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Success! Output: {result['output'][:200]}...")
                print(f"   Execution time: {result.get('execution_time', 'N/A')}s")
                return True
            else:
                print(f"❌ Failed with status {response.status_code}: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def test_memory_operations(self):
        """Test memory operations"""
        print("\nTesting memory operations...")
        conversation_id = f"test_conv_{int(time.time())}"
        
        # Test adding to memory
        add_data = {
            "conversation_id": conversation_id,
            "action": "add",
            "input": "What is the capital of France?",
            "output": "The capital of France is Paris."
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/v1/agent/memory",
                headers=self.headers,
                json=add_data
            )
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Memory add: {result['message']}")
            else:
                print(f"❌ Memory add failed: {response.status_code}")
                return False
            
            # Test getting memory
            get_data = {
                "conversation_id": conversation_id,
                "action": "get"
            }
            
            response = requests.post(
                f"{self.base_url}/v1/agent/memory",
                headers=self.headers,
                json=get_data
            )
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Memory get: {result['message']}")
                if result.get('memory_content'):
                    print(f"   Memory content: {result['memory_content']}")
            else:
                print(f"❌ Memory get failed: {response.status_code}")
                return False
            
            # Test clearing memory
            clear_data = {
                "conversation_id": conversation_id,
                "action": "clear"
            }
            
            response = requests.post(
                f"{self.base_url}/v1/agent/memory",
                headers=self.headers,
                json=clear_data
            )
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Memory clear: {result['message']}")
                return True
            else:
                print(f"❌ Memory clear failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Memory operation error: {e}")
            return False
    
    def test_provider_specific_agent(self):
        """Test provider-specific agent"""
        print("\nTesting provider-specific agent...")
        data = {
            "input": "Hello, how are you?",
            "config": {
                "agent_type": "zero-shot-react-description",
                "tools": [],
                "verbose": False,
                "max_iterations": 3
            }
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/gemini/agent/run",
                headers=self.headers,
                json=data
            )
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Provider-specific agent success! Output: {result['output'][:100]}...")
                return True
            else:
                print(f"❌ Provider-specific agent failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Provider-specific agent error: {e}")
            return False
    
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting Agent API Tests...")
        print("=" * 50)
        
        tests = [
            ("Get Tools", self.test_get_tools),
            ("Simple Agent", self.test_simple_agent),
            ("Search Agent", self.test_search_agent),
            ("Memory Operations", self.test_memory_operations),
            ("Provider-Specific Agent", self.test_provider_specific_agent),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n🧪 Running test: {test_name}")
            if test_func():
                passed += 1
            else:
                print(f"❌ Test '{test_name}' failed!")
        
        print("\n" + "=" * 50)
        print(f"📊 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! Agent API is working correctly.")
        else:
            print("⚠️  Some tests failed. Check the output above for details.")
        
        return passed == total

def main():
    """Main function"""
    print("Agent API Test Suite")
    print("Make sure the g4f API server is running on http://localhost:1337")
    print("You can start it with: python main.py")
    print()
    
    # Check if server is running
    try:
        response = requests.get("http://localhost:1337/v1", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running!")
        else:
            print("❌ Server responded with unexpected status code")
            return
    except requests.exceptions.RequestException:
        print("❌ Could not connect to server. Make sure it's running on http://localhost:1337")
        return
    
    # Run tests
    tester = AgentAPITester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎯 Agent API is ready to use!")
        print("📖 Check AGENT_API_EXAMPLES.md for usage examples")
    else:
        print("\n🔧 Please check the server logs and fix any issues")

if __name__ == "__main__":
    main() 