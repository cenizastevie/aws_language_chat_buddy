import json
import boto3
import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
import re
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResponseType(Enum):
    CORRECT = "correct"
    GRAMMAR_ERROR = "grammar_error"
    INCOMPLETE = "incomplete"
    INVALID = "invalid"

@dataclass
class EvaluationResult:
    response_type: ResponseType
    is_valid: bool
    extracted_variables: Dict[str, Any]
    feedback: str
    corrected_response: Optional[str] = None
    next_prompt: Optional[str] = None

class LLMPrompter:
    def __init__(self, aws_region: str = 'us-east-1', model_id: str = 'anthropic.claude-3-sonnet-20240229-v1:0'):
        """
        Initialize the LLM Prompter with AWS Bedrock client
        
        Args:
            aws_region: AWS region for Bedrock
            model_id: Model ID for the LLM
        """
        self.bedrock_client = boto3.client('bedrock-runtime', region_name=aws_region)
        self.model_id = model_id
        self.scenario_data = None
        self.conversation_state = {}
        self.current_event_index = 0
        
    def load_scenario(self, scenario_file_path: str) -> None:
        """Load scenario configuration from JSON file"""
        try:
            with open(scenario_file_path, 'r', encoding='utf-8') as file:
                self.scenario_data = json.load(file)
                self.conversation_state = {
                    'variables': self.scenario_data.get('variables', {}).copy(),
                    'progress_tracking': self.scenario_data.get('progress_tracking', {}).copy(),
                    'current_event_index': 0,
                    'attempts': 0
                }
                logger.info(f"Loaded scenario: {self.scenario_data.get('scenario_name', 'Unknown')}")
        except Exception as e:
            logger.error(f"Error loading scenario: {str(e)}")
            raise
    
    def _invoke_llm(self, prompt: str, max_tokens: int = 1000) -> str:
        """Invoke AWS Bedrock LLM with the given prompt"""
        try:
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": max_tokens,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
            
            response = self.bedrock_client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(body)
            )
            
            response_body = json.loads(response['body'].read())
            return response_body['content'][0]['text']
            
        except Exception as e:
            logger.error(f"Error invoking LLM: {str(e)}")
            raise
    
    def _create_grammar_check_prompt(self, student_response: str, expected_focus: List[str]) -> str:
        """Create a prompt for grammar checking and correction"""
        focus_areas = ", ".join(expected_focus)
        
        prompt = f"""
        You are an English language teacher helping a student learn English. 
        
        Student's response: "{student_response}"
        
        Focus areas for this exercise: {focus_areas}
        
        Please analyze the student's response and provide:
        1. Is the grammar correct? (Yes/No)
        2. If incorrect, provide the corrected version
        3. Brief explanation of any errors (keep it simple and encouraging)
        4. Rate the response as: CORRECT, GRAMMAR_ERROR, INCOMPLETE, or INVALID
        
        Format your response as JSON:
        {{
            "is_correct": boolean,
            "corrected_response": "corrected version if needed",
            "explanation": "brief explanation",
            "rating": "CORRECT|GRAMMAR_ERROR|INCOMPLETE|INVALID"
        }}
        """
        return prompt
    
    def _create_variable_extraction_prompt(self, student_response: str, current_event: Dict[str, Any]) -> str:
        """Create a prompt for extracting required variables from student response"""
        event_instruction = current_event.get('instruction', '')
        
        prompt = f"""
        You are helping extract information from a student's response in a language learning exercise.
        
        Student's response: "{student_response}"
        What we're looking for: {event_instruction}
        
        Please extract any relevant information and return it as JSON:
        {{
            "extracted_info": {{
                "key": "value pairs of extracted information"
            }},
            "confidence": "high|medium|low",
            "is_complete": boolean
        }}
        """
        return prompt
    
    def _evaluate_student_response(self, student_response: str, current_event: Dict[str, Any]) -> EvaluationResult:
        """Evaluate student response for grammar and completeness"""
        try:
            # Check grammar
            evaluation_focus = current_event.get('evaluation_focus', [])
            grammar_prompt = self._create_grammar_check_prompt(student_response, evaluation_focus)
            grammar_result = self._invoke_llm(grammar_prompt)
            
            # Parse grammar check result
            try:
                grammar_data = json.loads(grammar_result)
            except json.JSONDecodeError:
                logger.error(f"Failed to parse grammar check result: {grammar_result}")
                grammar_data = {
                    "is_correct": False,
                    "corrected_response": student_response,
                    "explanation": "Could not analyze response",
                    "rating": "INVALID"
                }
            
            # Extract variables if needed
            extracted_variables = {}
            if current_event.get('type') == 'student_response_expectation':
                extraction_prompt = self._create_variable_extraction_prompt(student_response, current_event)
                extraction_result = self._invoke_llm(extraction_prompt)
                
                try:
                    extraction_data = json.loads(extraction_result)
                    extracted_variables = extraction_data.get('extracted_info', {})
                except json.JSONDecodeError:
                    logger.error(f"Failed to parse extraction result: {extraction_result}")
            
            # Determine response type
            response_type = ResponseType(grammar_data['rating'].lower())
            is_valid = grammar_data['is_correct'] and response_type == ResponseType.CORRECT
            
            return EvaluationResult(
                response_type=response_type,
                is_valid=is_valid,
                extracted_variables=extracted_variables,
                feedback=grammar_data.get('explanation', ''),
                corrected_response=grammar_data.get('corrected_response'),
                next_prompt=None
            )
            
        except Exception as e:
            logger.error(f"Error evaluating student response: {str(e)}")
            return EvaluationResult(
                response_type=ResponseType.INVALID,
                is_valid=False,
                extracted_variables={},
                feedback="Sorry, I couldn't understand your response. Please try again.",
                corrected_response=None,
                next_prompt=None
            )
    
    def _generate_feedback_prompt(self, evaluation_result: EvaluationResult, teacher_persona: Dict[str, Any]) -> str:
        """Generate appropriate feedback based on evaluation result"""
        persona_tone = teacher_persona.get('tone', 'friendly and encouraging')
        
        if evaluation_result.response_type == ResponseType.CORRECT:
            feedback_prompt = f"""
            You are {teacher_persona.get('name', 'a teacher')} with a {persona_tone} personality.
            The student gave a correct response. Provide positive, encouraging feedback.
            Keep it brief and enthusiastic.
            """
        elif evaluation_result.response_type == ResponseType.GRAMMAR_ERROR:
            feedback_prompt = f"""
            You are {teacher_persona.get('name', 'a teacher')} with a {persona_tone} personality.
            The student made a grammar error. 
            
            Original response: "{evaluation_result.corrected_response}"
            Corrected version: "{evaluation_result.corrected_response}"
            
            Provide gentle correction with encouragement. Say the corrected version and ask them to try again.
            """
        else:
            feedback_prompt = f"""
            You are {teacher_persona.get('name', 'a teacher')} with a {persona_tone} personality.
            The student's response was incomplete or unclear.
            
            Provide gentle guidance and ask them to try again with more specific direction.
            """
        
        return self._invoke_llm(feedback_prompt)
    
    def _update_conversation_state(self, evaluation_result: EvaluationResult) -> None:
        """Update conversation state based on evaluation result"""
        if evaluation_result.is_valid:
            # Update variables
            for key, value in evaluation_result.extracted_variables.items():
                if key in self.conversation_state['variables']:
                    self.conversation_state['variables'][key] = value
            
            # Move to next event
            self.current_event_index += 1
            self.conversation_state['current_event_index'] = self.current_event_index
            self.conversation_state['attempts'] = 0
            
            # Update progress tracking
            current_event = self.scenario_data['conversation_events'][self.current_event_index - 1]
            event_id = current_event.get('event_id', '')
            if event_id + '_completed' in self.conversation_state['progress_tracking']:
                self.conversation_state['progress_tracking'][event_id + '_completed'] = True
        else:
            # Increment attempts
            self.conversation_state['attempts'] += 1
    
    def get_current_prompt(self) -> str:
        """Get the current prompt for the conversation"""
        if not self.scenario_data:
            return "No scenario loaded. Please load a scenario first."
        
        events = self.scenario_data['conversation_events']
        if self.current_event_index >= len(events):
            return "Conversation completed! Great job!"
        
        current_event = events[self.current_event_index]
        event_type = current_event.get('type', '')
        
        if event_type in ['teacher_initial_prompt', 'teacher_guidance_and_role_setup', 'teacher_final_prompt']:
            return current_event.get('text', '')
        
        elif event_type == 'role_play_prompt_alex' or event_type == 'role_play_prompt_stacy':
            # Handle template replacement
            text_template = current_event.get('text_template', current_event.get('text', ''))
            return self._replace_template_variables(text_template)
        
        elif event_type == 'student_response_expectation':
            return f"Please respond: {current_event.get('instruction', '')}"
        
        elif event_type == 'teacher_feedback':
            return current_event.get('text', current_event.get('instruction', ''))
        
        return "Continue the conversation..."
    
    def _replace_template_variables(self, template: str) -> str:
        """Replace template variables with actual values"""
        result = template
        for var_name, var_value in self.conversation_state['variables'].items():
            if var_value is not None:
                result = result.replace(f'{{{var_name}}}', str(var_value))
        return result
    
    def process_student_response(self, student_response: str) -> Dict[str, Any]:
        """Process student response and return next action"""
        if not self.scenario_data:
            return {
                'error': 'No scenario loaded',
                'next_prompt': 'Please load a scenario first.'
            }
        
        events = self.scenario_data['conversation_events']
        if self.current_event_index >= len(events):
            return {
                'message': 'Conversation completed',
                'next_prompt': 'Great job completing the scenario!'
            }
        
        current_event = events[self.current_event_index]
        
        # Only evaluate if this is a student response event
        if current_event.get('type') == 'student_response_expectation':
            evaluation_result = self._evaluate_student_response(student_response, current_event)
            
            if evaluation_result.is_valid:
                # Update state and move to next event
                self._update_conversation_state(evaluation_result)
                
                # Generate positive feedback
                feedback = self._generate_feedback_prompt(evaluation_result, self.scenario_data['teacher_persona'])
                
                return {
                    'status': 'success',
                    'feedback': feedback,
                    'next_prompt': self.get_current_prompt(),
                    'variables_updated': evaluation_result.extracted_variables
                }
            else:
                # Provide correction and stay on same event
                feedback = self._generate_feedback_prompt(evaluation_result, self.scenario_data['teacher_persona'])
                
                return {
                    'status': 'needs_correction',
                    'feedback': feedback,
                    'corrected_response': evaluation_result.corrected_response,
                    'next_prompt': 'Please try again.',
                    'attempt_count': self.conversation_state['attempts']
                }
        else:
            # Move to next event for non-student response events
            self.current_event_index += 1
            self.conversation_state['current_event_index'] = self.current_event_index
            
            return {
                'status': 'continue',
                'next_prompt': self.get_current_prompt()
            }
    
    def get_conversation_state(self) -> Dict[str, Any]:
        """Get current conversation state"""
        return {
            'scenario_name': self.scenario_data.get('scenario_name', '') if self.scenario_data else '',
            'current_event_index': self.current_event_index,
            'variables': self.conversation_state.get('variables', {}),
            'progress_tracking': self.conversation_state.get('progress_tracking', {}),
            'attempts': self.conversation_state.get('attempts', 0)
        }
    
    def reset_conversation(self) -> None:
        """Reset conversation to the beginning"""
        if self.scenario_data:
            self.conversation_state = {
                'variables': self.scenario_data.get('variables', {}).copy(),
                'progress_tracking': self.scenario_data.get('progress_tracking', {}).copy(),
                'current_event_index': 0,
                'attempts': 0
            }
            self.current_event_index = 0


# Example usage and testing
if __name__ == "__main__":
    # Example usage
    prompter = LLMPrompter()
    
    # Load a scenario
    prompter.load_scenario('scenarios/friend.json')
    
    # Start conversation
    print("Starting conversation...")
    print(prompter.get_current_prompt())
    
    # Simulate student responses
    test_responses = [
        "Yes, I'm ready!",
        "My name is Maria",
        "I like cats",
        "It is cute and soft"
    ]
    
    for response in test_responses:
        print(f"\nStudent: {response}")
        result = prompter.process_student_response(response)
        print(f"System: {result}")