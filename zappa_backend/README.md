# AWS Language Chat Buddy - Zappa Backend

A Flask application for English language learning with AI-powered conversation scenarios, deployed using Zappa.

## Prerequisites

- Python 3.9+
- AWS CLI configured with appropriate credentials
- AWS account with Bedrock access

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure AWS credentials:**
   ```bash
   aws configure
   ```

3. **Update zappa_settings.json:**
   - Change the S3 bucket names to unique values
   - Update the AWS region if needed
   - Modify environment variables as needed

# Virtual Environment Setup

This project uses a Python virtual environment to manage dependencies.

## Windows Setup

Run the batch file to create and set up the virtual environment:
```cmd
setup_venv.bat
```

Or manually:
```cmd
python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
```

## Linux/Mac Setup

Run the shell script to create and set up the virtual environment:
```bash
chmod +x setup_venv.sh
./setup_venv.sh
```

Or manually:
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Activation

**Windows:**
```cmd
venv\Scripts\activate.bat
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

## Deactivation

```bash
deactivate
```

## Local Development

Run the Flask app locally:
```bash
python app.py
```

## Deployment

1. **Initialize Zappa (first time only):**
   ```bash
   zappa init
   ```

2. **Deploy to development:**
   ```bash
   zappa deploy dev
   ```

3. **Update existing deployment:**
   ```bash
   zappa update dev
   ```

4. **Deploy to production:**
   ```bash
   zappa deploy production
   ```

## API Endpoints

- `GET /health` - Health check
- `POST /load_scenario` - Load a conversation scenario
- `GET /current_prompt` - Get current conversation prompt
- `POST /student_response` - Submit student response
- `POST /reset` - Reset conversation
- `GET /state` - Get conversation state
- `POST /session/clear` - Clear session data
- `GET /session/info` - Get session information

## Session Management

The application uses Flask sessions to maintain conversation state per user. Each user's conversation progress is stored in their session, allowing multiple users to have independent conversations.

**Important Notes:**
- Sessions are maintained using cookies
- Make sure to include credentials in your requests for proper session handling
- Session data is serialized using pickle and base64 encoding
- Clear sessions when testing or switching between scenarios

## Environment Variables

- `MODEL_ID` - AWS Bedrock model ID (default: amazon.titan-text-lite-v1)
- `AWS_REGION` - AWS region (default: us-east-1)
- `SECRET_KEY` - Flask secret key for session management (required for production)

## Usage Example

```bash
# Load a scenario (with cookies for session)
curl -X POST https://your-api-url/load_scenario \
  -H "Content-Type: application/json" \
  -c cookies.txt \
  -d '{"scenario_path": "scenarios/friend.json"}'

# Get current prompt (using saved cookies)
curl -b cookies.txt https://your-api-url/current_prompt

# Submit student response (using saved cookies)
curl -X POST https://your-api-url/student_response \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"student_response": "Hello, my name is John"}'

# Clear session
curl -X POST https://your-api-url/session/clear -b cookies.txt
```

## AWS Permissions Required

The Lambda function needs permissions for:
- `bedrock:InvokeModel`
- CloudWatch Logs access
- S3 bucket access (for Zappa deployment)
