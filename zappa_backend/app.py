import os
from flask import Flask, request, jsonify, session
from flask_cors import CORS
from llm_prompter import LLMPrompter
import pickle
import base64

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-this-in-production')
CORS(app, supports_credentials=True)  # Enable CORS with credentials support

# Initialize prompter with environment variables or defaults
def get_prompter():
    model_id = os.environ.get('MODEL_ID', 'amazon.titan-text-lite-v1')
    region = os.environ.get('AWS_REGION', 'us-east-1')
    return LLMPrompter(aws_region=region, model_id=model_id)

def get_session_prompter():
    """Get prompter from session or create new one"""
    if 'prompter_state' in session:
        try:
            # Deserialize prompter from session
            prompter_data = base64.b64decode(session['prompter_state'])
            prompter = pickle.loads(prompter_data)
            return prompter
        except Exception as e:
            print(f"Error loading prompter from session: {e}")
            # Fall back to new prompter
            return get_prompter()
    else:
        return get_prompter()

def save_session_prompter(prompter):
    """Save prompter to session"""
    try:
        # Serialize prompter to session
        prompter_data = pickle.dumps(prompter)
        session['prompter_state'] = base64.b64encode(prompter_data).decode('utf-8')
        session.permanent = True
    except Exception as e:
        print(f"Error saving prompter to session: {e}")

@app.route('/load_scenario', methods=['POST'])
def load_scenario():
    data = request.get_json()
    scenario_path = data.get('scenario_path')
    if not scenario_path:
        return jsonify({'error': 'Missing scenario_path'}), 400
    try:
        prompter = get_session_prompter()
        prompter.load_scenario(scenario_path)
        save_session_prompter(prompter)
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
    has_prompter = 'prompter_state' in session
    return jsonify({
        'has_prompter_state': has_prompter,
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
