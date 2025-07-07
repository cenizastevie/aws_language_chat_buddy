# AWS Language Chat Buddy

A full-stack language learning chatbot powered by AWS Bedrock (Claude/Titan) for LLM, a Zappa Flask backend for API/session/LLM logic, and a modern React frontend hosted on S3 + CloudFront. Scenario-based templates enable interactive English practice with grammar correction and progress tracking.

## Architecture Overview

- **Frontend:** Vite React app, hosted on Amazon S3 and served via CloudFront (infrastructure as code provided)
- **Backend:** Flask API (Zappa), deployed to AWS Lambda, manages sessions, scenario logic, and LLM calls (Claude/Titan via Bedrock)
- **LLM Integration:** AWS Bedrock (Claude and Titan models supported)
- **Infrastructure:** CloudFormation templates for S3/CloudFront hosting and deployment scripts for automation

## File Structure

```
aws_language_chat_buddy/
├── zappa_backend/                # Flask backend (Zappa, Bedrock integration)
│   ├── app.py                   # Flask app with session, endpoints, CORS
│   ├── llm_prompter.py          # LLM logic, Bedrock integration, scenario handling
│   ├── requirements.txt         # Backend dependencies
│   ├── zappa_settings.json      # Zappa deployment config
│   ├── scenarios/               # Scenario templates (JSON)
│   └── README.md
├── vite_react_frontend/         # Vite React frontend
│   ├── src/components/          # Chat and scenario UI components
│   ├── src/services/            # API service for backend communication
│   ├── App.jsx, main.jsx        # Main React entry points
│   ├── index.css                # Styling
│   ├── package.json, vite.config.js, .env.example, README.md
├── infrastructure/              # CloudFormation & deployment scripts
│   ├── frontend-infrastructure.json # Full-featured S3+CloudFront template
│   ├── simple-frontend.yaml         # Minimal S3+CloudFront template
│   ├── deploy.sh, deploy.bat, build-and-deploy.sh # Deployment scripts
│   └── README.md
├── README.md                    # Project overview (this file)
└── ...
```

## Deployment & Usage

### 1. Backend (Zappa Flask API)
- Configure AWS credentials and Bedrock access.
- Edit `zappa_backend/zappa_settings.json` for environment variables (model, secret key, etc).
- Deploy with Zappa:
  ```bash
  cd zappa_backend
  zappa deploy dev
  ```
- The backend exposes REST endpoints for chat, session, and scenario management.

### 2. Frontend (React)
- Configure API endpoint in `.env` (see `.env.example`).
- Build the frontend:
  ```bash
  cd vite_react_frontend
  npm install
  npm run build
  ```
- Deploy to S3/CloudFront using provided CloudFormation templates and scripts:
  - `infrastructure/frontend-infrastructure.json` (full-featured)
  - `infrastructure/simple-frontend.yaml` (minimal)
  - Use `deploy.sh`, `deploy.bat`, or `build-and-deploy.sh` for automation.

### Deploying with simple-frontend.yaml

A minimal deployment script for the static frontend using the `simple-frontend.yaml` CloudFormation template:

```bash
STACK_NAME=language-chat-frontend-simple
BUCKET_NAME=your-unique-s3-bucket-name

aws cloudformation deploy --template-file infrastructure/simple-frontend.yaml --stack-name aws-language-buddy-s3  --capabilities CAPABILITY_NAMED_IAM       

aws s3 sync vite_react_frontend/dist s3://$BUCKET_NAME --delete
```

- Replace `your-unique-s3-bucket-name` with a globally unique S3 bucket name.
- This script assumes you have already built the frontend (`npm run build`).
- You must have AWS CLI configured and permissions to deploy CloudFormation and upload to S3.

### 3. Infrastructure
- Launch CloudFormation stack for S3/CloudFront hosting.
- Upload built frontend assets to S3 bucket.
- Invalidate CloudFront cache as needed (handled by scripts).

## Features
- Scenario-based language practice (customizable via JSON)
- Real-time chat with grammar correction and progress tracking
- Supports both Claude and Titan LLMs via AWS Bedrock
- Session management for multi-turn conversations
- Modern, responsive React UI
- Infrastructure as code and automated deployment scripts

## Customization & Advanced Usage
- Add or edit scenarios in `zappa_backend/scenarios/`
- Customize CloudFront/S3 settings in CloudFormation templates
- Extend frontend UI or backend logic as needed

## License
MIT

---
For detailed setup, configuration, and troubleshooting, see the `README.md` files in each subdirectory and the `infrastructure/README.md` for deployment instructions.
