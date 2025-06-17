# API Configuration Setup

## Environment Variables

To configure the backend API URL, create a `.env` file in the root directory with:

```bash
REACT_APP_API_BASE_URL=http://localhost:8000
```

## For Different Environments

### Development (default)
```bash
REACT_APP_API_BASE_URL=http://localhost:8000
```

### Production
```bash
REACT_APP_API_BASE_URL=https://your-production-api.com
```

### Staging
```bash
REACT_APP_API_BASE_URL=https://staging-api.your-domain.com
```

## API Endpoints

The chat component will make POST requests to one of two endpoints:

### 1. New Thread Creation
- **Endpoint**: `/query`
- **Method**: POST
- **Headers**: `Content-Type: application/json`
- **Body**: 
```json
{
  "question": "User's message"
}
```

### 2. Continue Existing Thread
- **Endpoint**: `/query/{thread_id}`
- **Method**: POST
- **Headers**: `Content-Type: application/json`
- **Body**: 
```json
{
  "question": "User's message"
}
```

## Expected Response Format

The backend should return a JSON response with this exact format:

```json
{
  "result": "AI response text here",
  "thread_id": "20250612_145429"
}
```

### Response Fields:
- **`result`** (required): The AI's response text
- **`thread_id`** (required): The thread identifier
  - For new threads: A newly generated thread ID
  - For existing threads: The same thread ID that was used in the request

## Error Handling

The frontend will gracefully handle:
- Network errors
- Server errors (4xx, 5xx)
- Malformed responses
- Connection timeouts

Error messages will be displayed to the user with options to retry. 