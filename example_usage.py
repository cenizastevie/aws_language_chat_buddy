#!/usr/bin/env python3
"""
Example usage of the LLM Prompter for language learning chatbot
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'zappa_backend'))

from llm_prompter import LLMPrompter

def main():
    """Main function to demonstrate chatbot usage"""
    
    # Initialize the prompter
    prompter = LLMPrompter()
    
    # Load a scenario
    scenario_path = os.path.join('zappa_backend', 'scenarios', 'friend.json')
    try:
        prompter.load_scenario(scenario_path)
        print("✅ Scenario loaded successfully!")
    except Exception as e:
        print(f"❌ Error loading scenario: {e}")
        return
    
    print("\n" + "="*50)
    print("🤖 Language Learning Chatbot")
    print("="*50)
    print("Type 'quit' to exit, 'reset' to restart scenario, 'status' to check progress")
    print("="*50)
    
    # Start conversation
    print("\n🎯 " + prompter.get_current_prompt())
    
    while True:
        try:
            # Get user input
            user_input = input("\n👤 You: ").strip()
            
            # Handle special commands
            if user_input.lower() == 'quit':
                print("\n👋 Goodbye! Keep practicing your English!")
                break
            elif user_input.lower() == 'reset':
                prompter.reset_conversation()
                print("\n🔄 Conversation reset!")
                print("\n🎯 " + prompter.get_current_prompt())
                continue
            elif user_input.lower() == 'status':
                state = prompter.get_conversation_state()
                print(f"\n📊 Progress:")
                print(f"   Scenario: {state['scenario_name']}")
                print(f"   Current Event: {state['current_event_index']}")
                print(f"   Variables: {state['variables']}")
                print(f"   Attempts: {state['attempts']}")
                continue
            
            if not user_input:
                print("Please say something!")
                continue
            
            # Process the response
            result = prompter.process_student_response(user_input)
            
            # Display results
            if result.get('status') == 'success':
                print(f"\n✅ {result.get('feedback', '')}")
                if result.get('next_prompt'):
                    print(f"\n🎯 {result['next_prompt']}")
                if result.get('variables_updated'):
                    print(f"📝 Updated info: {result['variables_updated']}")
                    
            elif result.get('status') == 'needs_correction':
                print(f"\n⚠️ {result.get('feedback', '')}")
                if result.get('corrected_response'):
                    print(f"💡 Correct version: {result['corrected_response']}")
                print(f"🔄 {result.get('next_prompt', 'Please try again.')}")
                print(f"📊 Attempt {result.get('attempt_count', 1)}")
                
            elif result.get('status') == 'continue':
                print(f"\n🎯 {result.get('next_prompt', '')}")
                
            elif result.get('message') == 'Conversation completed':
                print(f"\n🎉 {result.get('next_prompt', '')}")
                print("\n🏆 Congratulations! You've completed this scenario!")
                break
                
            else:
                print(f"\n❌ {result.get('error', 'Unknown error occurred')}")
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye! Keep practicing your English!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Please try again or type 'quit' to exit.")

if __name__ == "__main__":
    main()
