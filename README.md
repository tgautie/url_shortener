# URL Shortener API

A simple URL shortening service built with FastAPI and deployable to AWS Lambda.

## Features

- **Encode endpoint**: Shorten long URLs into compact codes
- **Decode endpoint**: Retrieve original URLs from short codes
- **In-memory storage**: Fast, simple state management
- **AWS Lambda ready**: Deploy with AWS SAM

## API Endpoints

### Health Check
```
GET /
```
Returns API status.

### Encode URL
```
POST /encode
Content-Type: application/json

{
  "url": "https://example.com/very/long/url"
}
```

Response (201):
```json
{
  "short_code": "a1b2c3d",
  "short_url": "/a1b2c3d",
  "original_url": "https://example.com/very/long/url"
}
```

### Get Original URL
```
GET /{short_code}
```

Response (200):
```json
{
  "original_url": "https://example.com/very/long/url"
}
```

## Local Development

### Prerequisites
- Python 3.11+
- pip

### Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

View interactive docs at `http://localhost:8000/docs`

## AWS Deployment

### Prerequisites
- AWS CLI configured with profile `tgautie-perso`
- AWS SAM CLI installed ([installation guide](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html))

### Deploy to AWS

1. **Build the application:**
```bash
sam build
```

2. **Deploy to AWS:**
```bash
sam deploy --guided --profile tgautie-perso
```

During the guided deployment, you'll be prompted for:
- **Stack Name**: e.g., `url-shortener-stack`
- **AWS Region**: e.g., `us-east-1`
- **Confirm changes before deploy**: Y
- **Allow SAM CLI IAM role creation**: Y
- **Disable rollback**: N
- **Save arguments to configuration file**: Y

3. **Get your API endpoint:**

After deployment, the API Gateway endpoint URL will be displayed in the outputs. It will look like:
```
https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/Prod/
```

### Subsequent Deployments

After the initial guided deployment:
```bash
sam build && sam deploy --profile tgautie-perso
```

### Delete the Stack

To remove all AWS resources:
```bash
sam delete --profile tgautie-perso
```

## Testing the Deployed API

```bash
# Health check
curl https://your-api-endpoint.amazonaws.com/Prod/

# Encode a URL
curl -X POST https://your-api-endpoint.amazonaws.com/Prod/encode \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.example.com/very/long/url"}'

# Get original URL (use the short_code from previous response)
curl https://your-api-endpoint.amazonaws.com/Prod/a1b2c3d
```

## Architecture

- **FastAPI**: Modern Python web framework
- **Mangum**: ASGI adapter for AWS Lambda
- **AWS Lambda**: Serverless compute
- **API Gateway**: HTTP API endpoint
- **In-memory storage**: Simple dictionary-based storage (note: state is lost on Lambda cold starts)

## Limitations

- **State persistence**: URLs are stored in memory and will be lost when the Lambda function is recycled
- **Collision handling**: Uses SHA256 hash truncation with collision detection
- **Scalability**: For production use, consider adding DynamoDB or Redis for persistent storage

## Project Structure

```
.
├── CLAUDE.md          # FastAPI development rules
├── README.md          # This file
├── main.py            # FastAPI application
├── requirements.txt   # Python dependencies
└── template.yaml      # AWS SAM template
```
