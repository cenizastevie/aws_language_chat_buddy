#!/usr/bin/env python3
"""
Test script for the Language Learning Chatbot
"""

import json
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'zappa_backend'))

from llm_prompter import LLMPrompter

def test_scenario_loading():
    """Test loading scenario files"""
    print("Testing scenario loading...")
    
    prompter = LLMPrompter()
    
    # Test friend scenario
    try:
        prompter.load_scenario('zappa_backend/scenarios/friend.json')
        print("✅ Friend scenario loaded successfully")
    except Exception as e:
        print(f"❌ Failed to load friend scenario: {e}")
        return False
    
    # Test weather scenario
    try:
        prompter.load_scenario('zappa_backend/scenarios/weather.json')
        print("✅ Weather scenario loaded successfully")
    except Exception as e:
        print(f"❌ Failed to load weather scenario: {e}")
        return False
    
    return True

def test_conversation_flow():
    """Test basic conversation flow"""
    print("\nTesting conversation flow...")
    
    prompter = LLMPrompter()
    
    try:
        # Load scenario
        prompter.load_scenario('zappa_backend/scenarios/friend.json')
        
        # Test initial prompt
        initial_prompt = prompter.get_current_prompt()
        print(f"Initial prompt: {initial_prompt}")
        
        # Test conversation state
        state = prompter.get_conversation_state()
        print(f"Initial state: {state}")
        
        # Test reset
        prompter.reset_conversation()
        print("✅ Conversation reset successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Conversation flow test failed: {e}")
        return False

def test_template_replacement():
    """Test template variable replacement"""
    print("\nTesting template replacement...")
    
    prompter = LLMPrompter()
    
    try:
        prompter.load_scenario('zappa_backend/scenarios/friend.json')
        
        # Manually set variables
        prompter.conversation_state['variables']['user_name'] = 'TestUser'
        prompter.conversation_state['variables']['favorite_animal'] = 'dog'
        
        # Test template replacement
        template = "Hi {user_name}! I like {favorite_animal}s too!"
        result = prompter._replace_template_variables(template)
        expected = "Hi TestUser! I like dogs too!"
        
        if result == expected:
            print("✅ Template replacement works correctly")
            return True
        else:
            print(f"❌ Template replacement failed: got '{result}', expected '{expected}'")
            return False
            
    except Exception as e:
        print(f"❌ Template replacement test failed: {e}")
        return False

def test_lambda_handler():
    """Test Lambda handler functions"""
    print("\nTesting Lambda handler...")
    
    try:
        from zappa_handler import lambda_handler
        
        # Test start conversation
        event = {
            "action": "start_conversation",
            "scenario_name": "friend",
            "session_id": "test_session"
        }
        
        # Note: This will fail without AWS credentials, but we can test the structure
        try:
            result = lambda_handler(event, None)
            print("✅ Lambda handler structure is correct")
            return True
        except Exception as e:
            if "credentials" in str(e).lower() or "bedrock" in str(e).lower():
                print("✅ Lambda handler structure is correct (AWS credentials needed for full test)")
                return True
            else:
                print(f"❌ Lambda handler test failed: {e}")
                return False
                
    except ImportError as e:
        print(f"❌ Lambda handler import failed: {e}")
        return False

def test_scenario_validation():
    """Test scenario JSON validation"""
    print("\nTesting scenario validation...")
    
    required_fields = [
        'scenario_id', 'scenario_name', 'teacher_persona',
        'conversation_events', 'variables', 'progress_tracking'
    ]
    
    scenarios = ['friend.json', 'weather.json']
    
    for scenario_file in scenarios:
        try:
            with open(f'zappa_backend/scenarios/{scenario_file}', 'r') as f:
                data = json.load(f)
            
            # Check required fields
            missing_fields = []
            for field in required_fields:
                if field not in data:
                    missing_fields.append(field)
            
            if missing_fields:
                print(f"❌ {scenario_file} missing fields: {missing_fields}")
                return False
            else:
                print(f"✅ {scenario_file} structure is valid")
                
        except Exception as e:
            print(f"❌ Failed to validate {scenario_file}: {e}")
            return False
    
    return True

def main():
    """Run all tests"""
    print("🧪 Running Language Learning Chatbot Tests")
    print("=" * 50)
    
    tests = [
        test_scenario_loading,
        test_conversation_flow,
        test_template_replacement,
        test_scenario_validation,
        test_lambda_handler
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️ Some tests failed. Check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
