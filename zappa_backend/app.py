import os
from flask import Flask, request, jsonify, session
from flask_cors import CORS
from llm_prompter import LLMPrompter
from conversation_state import ConversationState
import json
from uuid import uuid4

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-this-in-production')

# Session cookie config for cross-origin and secure usage
app.config['SESSION_COOKIE_SAMESITE'] = 'None'
app.config['SESSION_COOKIE_SECURE'] = False  # For local development over HTTP
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_NAME'] = 'language_chat_session'
app.config['PERMANENT_SESSION_LIFETIME'] = 60 * 60 * 24 * 7  # 7 days

# CORS config for frontend-backend communication (local dev: allow all origins)
CORS(
    app,
    supports_credentials=True,
    origins="*",
    allow_headers=[
        'Content-Type',
        'Authorization',
        'X-Requested-With',
    ],
    expose_headers=[
        'Set-Cookie',
    ]
)

# Initialize prompter with environment variables or defaults
def get_prompter():
    """Create a new prompter with default settings"""
    model_id = os.environ.get('MODEL_ID', 'amazon.titan-text-lite-v1')
    region = os.environ.get('AWS_REGION', 'us-east-1')
    
    state = ConversationState()
    return LLMPrompter(state, aws_region=region, model_id=model_id)

def get_session_prompter():
    """Get prompter from session or create new one"""
    if 'conversation_state' in session:
        try:
            # Deserialize conversation state from session
            state_data = session['conversation_state']
            conversation_state = ConversationState.from_dict(state_data)
            
            # Create prompter with session state and environment settings
            model_id = os.environ.get('MODEL_ID', 'amazon.titan-text-lite-v1')
            region = os.environ.get('AWS_REGION', 'us-east-1')
            return LLMPrompter(conversation_state, aws_region=region, model_id=model_id)
        except Exception as e:
            print(f"Error loading conversation state from session: {e}")
            # Fall back to new prompter
            return get_prompter()
    else:
        return get_prompter()

def save_session_prompter(prompter):
    """Save prompter's conversation state to session"""
    try:
        # Serialize only the conversation state (which is serializable)
        session['conversation_state'] = prompter.conversation_state.to_dict()
        session.permanent = True
        # Ensure a session_id is set for tracking
        if 'session_id' not in session:
            session['session_id'] = str(uuid4())
    except Exception as e:
        print(f"Error saving conversation state to session: {e}")

@app.route('/load_scenario', methods=['POST'])
def load_scenario():
    data = request.get_json()
    
    # Support both old format (scenario_path) and new format (scenario_name)
    scenario_name = data.get('scenario_name')
    scenario_path = data.get('scenario_path')
    
    if scenario_name:
        # Direct scenario name provided
        pass
    elif scenario_path:
        # Extract scenario name from path (e.g., "scenarios/friend.json" -> "friend")
        import os
        base_name = os.path.basename(scenario_path)
        scenario_name = os.path.splitext(base_name)[0]
    else:
        return jsonify({'error': 'Missing scenario_name or scenario_path'}), 400
    
    try:
        prompter = get_session_prompter()
        prompter.initialize_scenario(scenario_name)
        save_session_prompter(prompter)
        # Log request and session info for debugging
        print('--- Lambda Request Debug ---')
        print('Headers:', dict(request.headers))
        print('Cookies:', request.cookies)
        print('Session:', dict(session))
        print('---------------------------')
        return jsonify({'status': 'loaded', 'scenario': prompter.get_conversation_state()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/current_prompt', methods=['GET'])
def current_prompt():
    prompter = get_session_prompter()
    return jsonify({'prompt': prompter.get_current_prompt()})

@app.route('/student_response', methods=['POST'])
def student_response():
    data = request.get_json()
    response = data.get('student_response')
    if response is None:
        return jsonify({'error': 'Missing student_response'}), 400
    prompter = get_session_prompter()
    result = prompter.process_student_response(response)
    save_session_prompter(prompter)
    return jsonify(result)

@app.route('/reset', methods=['POST'])
def reset():
    prompter = get_session_prompter()
    prompter.reset_conversation()
    save_session_prompter(prompter)
    return jsonify({'status': 'reset', 'state': prompter.get_conversation_state()})

@app.route('/state', methods=['GET'])
def state():
    prompter = get_session_prompter()
    return jsonify(prompter.get_conversation_state())

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'service': 'aws-language-chat-buddy'})

@app.route('/session/clear', methods=['POST'])
def clear_session():
    """Clear all session data"""
    session.clear()
    return jsonify({'status': 'session_cleared'})

@app.route('/session/info', methods=['GET'])
def session_info():
    """Get session information"""
    has_conversation_state = 'conversation_state' in session
    return jsonify({
        'has_prompter_state': has_conversation_state,  # Keep same key for frontend compatibility
        'session_id': session.get('session_id', 'none')
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True)
