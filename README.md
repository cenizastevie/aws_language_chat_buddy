# AWS Language Chat Buddy

A sophisticated language learning chatbot powered by AWS Bedrock and Claude AI. This application uses scenario-based templates to create interactive conversations that help students practice English while providing grammar correction and progress tracking.

## Features

- 🤖 **AI-Powered Conversations**: Uses AWS Bedrock with Claude for natural language processing
- 📝 **Grammar Correction**: Automatically detects and corrects grammar errors
- 📊 **Progress Tracking**: Tracks student progress through conversation scenarios
- 🎯 **Scenario-Based Learning**: Uses JSON templates for structured learning experiences
- 🔄 **Adaptive Responses**: Doesn't move to next question until requirements are met
- 🚀 **Serverless Deployment**: Ready for AWS Lambda deployment with Zappa

## Project Structure

```
aws_language_chat_buddy/
├── README.md
├── requirements.txt
├── config.py.template
├── example_usage.py
├── zappa_settings.json
└── zappa_backend/
    ├── llm_prompter.py          # Main chatbot logic
    ├── zappa_handler.py         # AWS Lambda handler
    └── scenarios/
        ├── friend.json          # Friend meeting scenario
        └── weather.json         # Weather conversation scenario
```

## Setup Instructions

### Prerequisites

1. **AWS Account**: You need an AWS account with access to AWS Bedrock
2. **AWS CLI**: Install and configure AWS CLI with appropriate credentials
3. **Python 3.9+**: Make sure you have Python 3.9 or later installed

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd aws_language_chat_buddy
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure AWS credentials**:
   ```bash
   aws configure
   ```

4. **Set up AWS Bedrock**:
   - Go to AWS Console → Bedrock → Model access
   - Request access to Claude models (anthropic.claude-3-sonnet-20240229-v1:0)
   - Wait for approval (usually takes a few minutes)

5. **Configure the application**:
   ```bash
   cp config.py.template config.py
   # Edit config.py with your AWS settings
   ```

## Usage

### Local Testing

Run the example script to test the chatbot locally:

```bash
python example_usage.py
```

### Programmatic Usage

```python
from zappa_backend.llm_prompter import LLMPrompter

# Initialize the prompter
prompter = LLMPrompter(aws_region='us-east-1')

# Load a scenario
prompter.load_scenario('zappa_backend/scenarios/friend.json')

# Start conversation
print(prompter.get_current_prompt())

# Process student response
result = prompter.process_student_response("My name is Maria")
print(result)
```

### AWS Lambda Deployment

1. **Configure Zappa**:
   ```bash
   # Edit zappa_settings.json with your S3 bucket name
   ```

2. **Deploy to development**:
   ```bash
   zappa deploy dev
   ```

3. **Update deployment**:
   ```bash
   zappa update dev
   ```

4. **Deploy to production**:
   ```bash
   zappa deploy production
   ```

### API Usage

Once deployed, you can interact with the API:

```bash
# Start a conversation
curl -X POST "https://your-api-url/dev" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "start_conversation",
    "scenario_name": "friend",
    "session_id": "user123"
  }'

# Process student response
curl -X POST "https://your-api-url/dev" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "process_response",
    "student_response": "My name is Maria",
    "session_id": "user123"
  }'
```

## How It Works

### Scenario Flow

1. **Load Scenario**: The system loads a JSON scenario template
2. **Present Prompt**: Shows the current conversation prompt to the student
3. **Evaluate Response**: When student responds, the system:
   - Checks grammar using AWS Bedrock
   - Extracts required information
   - Validates completeness
4. **Provide Feedback**: 
   - If correct: Positive feedback and move to next step
   - If incorrect: Correction with explanation and retry
5. **Progress Tracking**: Updates variables and progress state
6. **Repeat**: Continue until scenario completion

### Grammar Correction

The system uses AI to:
- Detect grammatical errors
- Provide corrected versions
- Explain mistakes in simple terms
- Encourage students to try again

### Variable Extraction

The system automatically extracts key information:
- Names, places, preferences
- Stores in conversation state
- Uses for template replacement in future prompts

## Scenario Templates

### Creating Custom Scenarios

Scenarios are defined in JSON format with the following structure:

```json
{
  "scenario_id": "unique_id",
  "scenario_name": "Descriptive Name",
  "teacher_persona": {
    "name": "Teacher Name",
    "role": "Role Description",
    "tone": "friendly, encouraging"
  },
  "conversation_events": [
    {
      "event_id": "event_name",
      "type": "teacher_initial_prompt",
      "text": "Welcome message"
    },
    {
      "event_id": "student_response",
      "type": "student_response_expectation",
      "instruction": "What student should do",
      "evaluation_focus": ["grammar_points", "vocabulary"]
    }
  ],
  "variables": {
    "variable_name": null
  },
  "progress_tracking": {
    "event_completed": false
  }
}
```

### Available Event Types

- `teacher_initial_prompt`: Initial greeting/instruction
- `teacher_guidance_and_role_setup`: Setup for role-play
- `role_play_prompt_*`: Character speaking to student
- `student_response_expectation`: Student should respond
- `teacher_feedback`: Feedback on student response
- `teacher_final_prompt`: Conclusion

## Configuration

### AWS Settings

- **AWS_REGION**: AWS region for Bedrock (default: us-east-1)
- **MODEL_ID**: Claude model to use (default: claude-3-sonnet)

### Model Options

- `anthropic.claude-3-haiku-20240307-v1:0`: Fastest, cheapest
- `anthropic.claude-3-sonnet-20240229-v1:0`: Balanced (recommended)
- `anthropic.claude-3-opus-20240229-v1:0`: Most capable, expensive

### Performance Tuning

- **MAX_TOKENS**: Maximum response length (default: 1000)
- **TEMPERATURE**: Response creativity (default: 0.3)
- **MAX_ATTEMPTS**: Retry attempts per question (default: 3)

## Troubleshooting

### Common Issues

1. **"Access denied" errors**: Check AWS Bedrock model access
2. **"Model not found"**: Verify model ID and region
3. **"Import errors"**: Ensure all dependencies are installed
4. **"JSON parsing errors"**: Check scenario file format

### Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions:
- Create an issue in the GitHub repository
- Check the troubleshooting section
- Review AWS Bedrock documentation
