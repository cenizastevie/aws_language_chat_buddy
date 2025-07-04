"""
Zappa handler for AWS Lambda deployment of the Language Learning Chatbot
"""

import json
import os
import logging
from llm_prompter import LLMPrompter

# Configure logging for Lambda
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Global prompter instance to reuse across Lambda invocations
prompter = None

def lambda_handler(event, context):
    """
    AWS Lambda handler for the language learning chatbot
    
    Expected event structure:
    {
        "action": "start_conversation" | "process_response" | "get_status" | "reset",
        "scenario_name": "friend" | "weather",
        "student_response": "student's message",
        "session_id": "unique session identifier"
    }
    """
    global prompter
    
    try:
        # Initialize prompter if not already done
        if prompter is None:
            aws_region = os.environ.get('AWS_REGION', 'us-east-1')
            model_id = os.environ.get('MODEL_ID', 'anthropic.claude-3-sonnet-20240229-v1:0')
            prompter = LLMPrompter(aws_region=aws_region, model_id=model_id)
        
        # Parse the event
        action = event.get('action', 'start_conversation')
        scenario_name = event.get('scenario_name', 'friend')
        student_response = event.get('student_response', '')
        session_id = event.get('session_id', 'default')
        
        # Handle different actions
        if action == 'start_conversation':
            return handle_start_conversation(scenario_name, session_id)
        
        elif action == 'process_response':
            return handle_process_response(student_response, session_id)
        
        elif action == 'get_status':
            return handle_get_status(session_id)
        
        elif action == 'reset':
            return handle_reset(session_id)
        
        else:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': f'Unknown action: {action}',
                    'valid_actions': ['start_conversation', 'process_response', 'get_status', 'reset']
                })
            }
    
    except Exception as e:
        logger.error(f"Error in lambda_handler: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e)
            })
        }

def handle_start_conversation(scenario_name: str, session_id: str):
    """Handle starting a new conversation"""
    global prompter
    
    try:
        # Load scenario
        scenario_path = f'scenarios/{scenario_name}.json'
        prompter.load_scenario(scenario_path)
        
        # Get initial prompt
        initial_prompt = prompter.get_current_prompt()
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'action': 'start_conversation',
                'session_id': session_id,
                'scenario_name': scenario_name,
                'prompt': initial_prompt,
                'status': 'conversation_started'
            })
        }
        
    except Exception as e:
        logger.error(f"Error starting conversation: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Failed to start conversation',
                'message': str(e)
            })
        }

def handle_process_response(student_response: str, session_id: str):
    """Handle processing student response"""
    global prompter
    
    try:
        if not student_response:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'Student response is required'
                })
            }
        
        # Process the response
        result = prompter.process_student_response(student_response)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'action': 'process_response',
                'session_id': session_id,
                'student_response': student_response,
                'result': result
            })
        }
        
    except Exception as e:
        logger.error(f"Error processing response: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Failed to process response',
                'message': str(e)
            })
        }

def handle_get_status(session_id: str):
    """Handle getting conversation status"""
    global prompter
    
    try:
        state = prompter.get_conversation_state()
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'action': 'get_status',
                'session_id': session_id,
                'state': state
            })
        }
        
    except Exception as e:
        logger.error(f"Error getting status: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Failed to get status',
                'message': str(e)
            })
        }

def handle_reset(session_id: str):
    """Handle resetting conversation"""
    global prompter
    
    try:
        prompter.reset_conversation()
        initial_prompt = prompter.get_current_prompt()
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'action': 'reset',
                'session_id': session_id,
                'prompt': initial_prompt,
                'status': 'conversation_reset'
            })
        }
        
    except Exception as e:
        logger.error(f"Error resetting conversation: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Failed to reset conversation',
                'message': str(e)
            })
        }

# For local testing
if __name__ == "__main__":
    # Test event
    test_event = {
        "action": "start_conversation",
        "scenario_name": "friend",
        "session_id": "test_session"
    }
    
    result = lambda_handler(test_event, None)
    print(json.dumps(result, indent=2))
