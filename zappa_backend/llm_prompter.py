import json
import boto3
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
from conversation_state import ConversationState

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
    def __init__(self, conversation_state: ConversationState = None, aws_region: str = 'us-east-1', model_id: str = 'anthropic.claude-3-sonnet-20240229-v1:0'):
        """
        Initialize the LLM Prompter with conversation state
        
        Args:
            conversation_state: ConversationState instance (creates new if None)
            aws_region: AWS region for Bedrock
            model_id: Model ID for Bedrock
        """
        self.conversation_state = conversation_state or ConversationState()
        self.aws_region = aws_region
        self.model_id = model_id
        # Don't store bedrock_client as instance variable to avoid pickling issues
        
    def _get_bedrock_client(self):
        """Get bedrock client (created fresh each time to avoid pickling)"""
        return boto3.client('bedrock-runtime', region_name=self.aws_region)
        
    def initialize_scenario(self, scenario_name: str) -> None:
        """Initialize a new scenario"""
        try:
            self.conversation_state.initialize_scenario(scenario_name)
            # Validate event sequence
            if not self.conversation_state.validate_event_sequence():
                logger.warning(f"Event sequence validation failed for scenario: {scenario_name}")
            logger.info(f"Initialized scenario: {scenario_name}")
        except Exception as e:
            logger.error(f"Error initializing scenario: {str(e)}")
            raise
    
    def jump_to_event(self, event_id: int) -> bool:
        """Jump to a specific event by ID"""
        return self.conversation_state.advance_to_event(event_id)
    
    def get_current_event_info(self) -> Dict[str, Any]:
        """Get information about the current event"""
        current_event = self.conversation_state.get_current_event()
        if not current_event:
            return {'event_id': None, 'expecting_input': False, 'type': None}
        
        return {
            'event_id': current_event.get('event_id'),
            'expecting_input': current_event.get('expecting_input', False),
            'type': current_event.get('type'),
            'index': self.conversation_state.current_event_index
        }
    
    def _invoke_llm(self, prompt: str, max_tokens: int = 1000) -> str:
        """Invoke AWS Bedrock LLM with the given prompt, supporting both Claude and Titan."""
        bedrock_client = self._get_bedrock_client()
        try:
            model_id = self.model_id
            if model_id.startswith('amazon.titan-text'):
                # Titan Text models require 'inputText' and 'textGenerationConfig'
                body = json.dumps({
                    "inputText": prompt,
                    "textGenerationConfig": {
                        "maxTokenCount": max_tokens,
                        "temperature": 0.2
                    }
                })
                response = bedrock_client.invoke_model(
                    modelId=model_id,
                    body=body
                )
                response_body = json.loads(response['body'].read())
                return response_body['results'][0]['outputText']
            else:
                # Default: Anthropic Claude
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
                response = bedrock_client.invoke_model(
                    modelId=model_id,
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
            if current_event.get('expecting_input', False):
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
            self.conversation_state.update_variables(evaluation_result.extracted_variables)
            
            # Move to next event
            self.conversation_state.advance_to_next_event()
        else:
            # Increment attempts
            self.conversation_state.increment_attempts()
    
    def get_current_prompt(self) -> str:
        """Get the current prompt for the conversation"""
        return self.conversation_state.get_current_prompt()
    def process_student_response(self, student_response: str) -> Dict[str, Any]:
        """Process student response and return next action"""
        if not self.conversation_state.scenario_name:
            return {
                'error': 'No scenario loaded',
                'next_prompt': 'Please load a scenario first.'
            }
        
        if self.conversation_state.is_conversation_complete():
            return {
                'message': 'Conversation completed',
                'next_prompt': 'Great job completing the scenario!'
            }
        
        current_event = self.conversation_state.get_current_event()
        if not current_event:
            return {
                'error': 'No current event',
                'next_prompt': 'Please reload the scenario.'
            }
        
        # Only evaluate if this is a student response event
        if current_event.get('expecting_input', False):
            evaluation_result = self._evaluate_student_response(student_response, current_event)
            
            if evaluation_result.is_valid:
                # Update state and move to next event
                self._update_conversation_state(evaluation_result)
                
                # Load scenario data to get teacher persona
                scenario_data = self.conversation_state._load_scenario_data()
                teacher_persona = scenario_data.get('teacher_persona', {}) if scenario_data else {}
                
                # Generate positive feedback
                feedback = self._generate_feedback_prompt(evaluation_result, teacher_persona)
                
                return {
                    'status': 'success',
                    'feedback': feedback,
                    'next_prompt': self.get_current_prompt(),
                    'variables_updated': evaluation_result.extracted_variables
                }
            else:
                # Load scenario data to get teacher persona
                scenario_data = self.conversation_state._load_scenario_data()
                teacher_persona = scenario_data.get('teacher_persona', {}) if scenario_data else {}
                
                # Provide correction and stay on same event
                feedback = self._generate_feedback_prompt(evaluation_result, teacher_persona)
                
                return {
                    'status': 'needs_correction',
                    'feedback': feedback,
                    'corrected_response': evaluation_result.corrected_response,
                    'next_prompt': 'Please try again.',
                    'attempt_count': self.conversation_state.attempts
                }
        else:
            # Move to next event for non-student response events
            self.conversation_state.advance_to_next_event()
            
            return {
                'status': 'continue',
                'next_prompt': self.get_current_prompt()
            }
    
    def get_conversation_state(self) -> Dict[str, Any]:
        """Get current conversation state"""
        return self.conversation_state.get_state_summary()
    
    def reset_conversation(self) -> None:
        """Reset conversation to the beginning"""
        self.conversation_state.reset_conversation()

# Example usage and testing
if __name__ == "__main__":
    # Example usage
    from conversation_state import ConversationState
    
    # Create conversation state and prompter
    state = ConversationState()
    prompter = LLMPrompter(
        conversation_state=state,
        aws_region='us-east-1',
        model_id='amazon.titan-text-lite-v1'
    )
    
    # Initialize a scenario
    prompter.initialize_scenario('friend')
    
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