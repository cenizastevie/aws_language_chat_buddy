import json
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class ConversationState:
    """Minimal serializable conversation state for session storage"""
    scenario_name: str = ""
    current_event_index: int = 0
    variables: Dict[str, Any] = None
    attempts: int = 0
    created_at: str = ""
    
    def __post_init__(self):
        if self.variables is None:
            self.variables = {}
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
    
    def _load_scenario_data(self) -> Optional[Dict[str, Any]]:
        """Load scenario data from disk - not stored in session"""
        if not self.scenario_name:
            return None
        
        # Construct path to scenario file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        scenario_path = os.path.join(current_dir, 'scenarios', f'{self.scenario_name}.json')
        
        try:
            with open(scenario_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except Exception as e:
            print(f"Error loading scenario {self.scenario_name}: {str(e)}")
            return None
    
    def initialize_scenario(self, scenario_name: str) -> None:
        """Initialize a new scenario"""
        self.scenario_name = scenario_name
        self.current_event_index = 0
        self.attempts = 0
        
        # Load scenario data to initialize variables
        scenario_data = self._load_scenario_data()
        if scenario_data:
            self.variables = scenario_data.get('variables', {}).copy()
    
    def get_current_event(self) -> Optional[Dict[str, Any]]:
        """Get the current conversation event"""
        scenario_data = self._load_scenario_data()
        if not scenario_data:
            return None
        
        events = scenario_data.get('conversation_events', [])
        if self.current_event_index >= len(events):
            return None
        
        return events[self.current_event_index]
    
    def advance_to_event(self, event_id: int) -> bool:
        """Jump to a specific event by ID"""
        scenario_data = self._load_scenario_data()
        if not scenario_data:
            return False
        
        events = scenario_data.get('conversation_events', [])
        for i, event in enumerate(events):
            if event.get('event_id') == event_id:
                self.current_event_index = i
                self.attempts = 0
                return True
        return False
    
    def get_event_by_id(self, event_id: int) -> Optional[Dict[str, Any]]:
        """Get an event by its ID"""
        scenario_data = self._load_scenario_data()
        if not scenario_data:
            return None
        
        events = scenario_data.get('conversation_events', [])
        for event in events:
            if event.get('event_id') == event_id:
                return event
        return None
    
    def advance_to_next_event(self) -> None:
        """Move to the next conversation event"""
        self.current_event_index += 1
        self.attempts = 0
    
    def increment_attempts(self) -> None:
        """Increment attempt counter for current event"""
        self.attempts += 1
    
    def update_variables(self, new_variables: Dict[str, Any]) -> None:
        """Update conversation variables"""
        for key, value in new_variables.items():
            if key in self.variables:
                self.variables[key] = value
    
    def replace_template_variables(self, template: str) -> str:
        """Replace template variables with actual values"""
        result = template
        for var_name, var_value in self.variables.items():
            if var_value is not None:
                result = result.replace(f'{{{var_name}}}', str(var_value))
        return result
    
    def get_current_prompt(self) -> str:
        """Get the current prompt for the conversation"""
        scenario_data = self._load_scenario_data()
        if not scenario_data:
            return "No scenario loaded. Please load a scenario first."
        
        current_event = self.get_current_event()
        if not current_event:
            return "Conversation completed! Great job!"
        
        event_type = current_event.get('type', '')
        
        if event_type in ['teacher_initial_prompt', 'teacher_guidance_and_role_setup', 'teacher_final_prompt']:
            return current_event.get('text', '')
        
        elif event_type in ['role_play_prompt_alex', 'role_play_prompt_stacy']:
            # Handle template replacement
            text_template = current_event.get('text_template', current_event.get('text', ''))
            return self.replace_template_variables(text_template)
        
        elif event_type == 'student_response_expectation':
            return f"Please respond: {current_event.get('instruction', '')}"
        
        elif event_type == 'teacher_feedback':
            return current_event.get('text', current_event.get('instruction', ''))
        
        return "Continue the conversation..."
    
    def current_event_expects_input(self) -> bool:
        """Check if the current event expects student input"""
        current_event = self.get_current_event()
        if not current_event:
            return False
        return current_event.get('expecting_input', False)
    
    def validate_event_sequence(self) -> bool:
        """Validate that event IDs are sequential and match array indices"""
        scenario_data = self._load_scenario_data()
        if not scenario_data:
            return False
        
        events = scenario_data.get('conversation_events', [])
        for i, event in enumerate(events):
            if event.get('event_id') != i:
                print(f"Event ID mismatch: expected {i}, got {event.get('event_id')}")
                return False
        return True
    
    def is_conversation_complete(self) -> bool:
        """Check if the conversation is complete"""
        scenario_data = self._load_scenario_data()
        if not scenario_data:
            return False
        
        events = scenario_data.get('conversation_events', [])
        return self.current_event_index >= len(events)
    
    def reset_conversation(self) -> None:
        """Reset conversation to the beginning"""
        scenario_data = self._load_scenario_data()
        if scenario_data:
            self.variables = scenario_data.get('variables', {}).copy()
            self.current_event_index = 0
            self.attempts = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization - only minimal state"""
        return {
            'scenario_name': self.scenario_name,
            'current_event_index': self.current_event_index,
            'variables': self.variables,
            'attempts': self.attempts,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConversationState':
        """Create instance from dictionary"""
        return cls(
            scenario_name=data.get('scenario_name', ''),
            current_event_index=data.get('current_event_index', 0),
            variables=data.get('variables', {}),
            attempts=data.get('attempts', 0),
            created_at=data.get('created_at', '')
        )
    
    def get_state_summary(self) -> Dict[str, Any]:
        """Get a summary of the current state"""
        return {
            'scenario_name': self.scenario_name,
            'current_event_index': self.current_event_index,
            'variables': self.variables,
            'attempts': self.attempts,
            'is_complete': self.is_conversation_complete(),
            'created_at': self.created_at
        }
