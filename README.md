# Flashcards API with LangChain Agent Support

A comprehensive API server that provides access to various AI models and providers through g4f (GPT4Free), with enhanced LangChain agent capabilities.

## Features

### Core API Features
- **Chat Completions**: Standard chat completion endpoints
- **Image Generation**: Generate images using various providers
- **Audio Transcription**: Convert audio to text
- **Audio Speech**: Convert text to speech
- **File Upload**: Upload and manage cookies for authentication
- **Provider Management**: List and configure different AI providers

### 🚀 New LangChain Agent API
- **Multiple Agent Types**: Support for various LangChain agent types
- **Built-in Tools**: Search, Wikipedia, YouTube, arXiv, Python REPL, shell, web requests
- **Memory Management**: Conversation buffer and summary memory
- **Provider-Specific Agents**: Use different providers for agents
- **Conversation Persistence**: Maintain conversation context across requests

## Quick Start

### Option 1: Docker (Recommended)

1. Clone the repository:
```bash
git clone <repository-url>
cd flashcards-api
```

2. Configure environment:
```bash
cp env.example .env
# Edit .env with your API key and settings
```

3. Build and run with Docker:
```bash
docker-compose up -d
```

4. Verify deployment:
```bash
curl http://localhost:1337/v1
```

### Option 2: Local Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd flashcards-api
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Start the server:
```bash
python main.py
```

The server will start on `http://localhost:1337` by default.

### Docker Quick Commands

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild and restart
docker-compose up -d --build

# Run with specific profiles
docker-compose --profile cache up -d  # With Redis
docker-compose --profile proxy up -d  # With Nginx proxy
```

📖 **Docker Documentation**: See `DOCKER_DEPLOYMENT.md` for detailed Docker instructions.

### Basic Usage

#### Chat Completions
```bash
curl -X POST "http://localhost:1337/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-api-key" \
  -d '{
    "model": "gpt-4o",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

#### Agent API
```bash
curl -X POST "http://localhost:1337/v1/agent/run" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-api-key" \
  -d '{
    "input": "What is the weather like today?",
    "config": {
      "agent_type": "zero-shot-react-description",
      "tools": ["duckduckgo_search"]
    }
  }'
```

## API Endpoints

### Core Endpoints
- `GET /v1/models` - List available models
- `POST /v1/chat/completions` - Chat completions
- `POST /v1/images/generate` - Generate images
- `POST /v1/audio/transcriptions` - Transcribe audio
- `POST /v1/audio/speech` - Generate speech
- `GET /v1/providers` - List available providers

### Agent Endpoints
- `GET /v1/agent/tools` - Get available tools
- `POST /v1/agent/run` - Run an agent
- `POST /api/{provider}/agent/run` - Run agent with specific provider
- `POST /v1/agent/memory` - Manage agent memory

## Agent Types

1. **zero-shot-react-description** - Default agent type
2. **openai-functions** - Uses OpenAI function calling
3. **structured-chat-zero-shot-react** - Structured chat agent
4. **conversational-react-description** - Conversational agent with memory
5. **chat-zero-shot-react-description** - Chat-based zero-shot agent
6. **chat-conversational-react-description** - Chat-based conversational agent

## Available Tools

### Search Tools
- `duckduckgo_search` - Web search
- `wikipedia` - Wikipedia search
- `youtube_search` - YouTube search
- `arxiv_search` - Academic papers
- `pubmed_search` - Medical research

### Programming Tools
- `python_repl` - Execute Python code
- `shell` - Execute shell commands

### Web Tools
- `web_search` - GET requests
- `web_post` - POST requests

### Utility Tools
- `human_input` - Ask for human input

## Configuration

### Environment Variables
- `G4F_API_KEY` - API key for authentication
- `G4F_MODEL` - Default model
- `G4F_PROVIDER` - Default provider
- `G4F_MEDIA_PROVIDER` - Default media provider
- `G4F_PROXY` - Proxy configuration

### Server Options
```bash
python main.py --host 0.0.0.0 --port 1337 --debug
```

## Testing

Run the test suite to verify the agent API functionality:

```bash
python test_agent_api.py
```

## Documentation

- **API Examples**: See `AGENT_API_EXAMPLES.md` for comprehensive examples
- **Swagger UI**: Visit `http://localhost:1337/docs` for interactive API documentation
- **OpenAPI Spec**: Available at `http://localhost:1337/openapi.json`

## Examples

### Research Agent
```python
import requests

response = requests.post("http://localhost:1337/v1/agent/run", 
  headers={"Authorization": "Bearer your-key"},
  json={
    "input": "Research quantum computing developments",
    "config": {
      "agent_type": "structured-chat-zero-shot-react",
      "tools": ["duckduckgo_search", "wikipedia", "arxiv_search"],
      "verbose": True,
      "max_iterations": 15
    }
  }
)
```

### Programming Assistant
```python
response = requests.post("http://localhost:1337/v1/agent/run",
  headers={"Authorization": "Bearer your-key"},
  json={
    "input": "Create a web scraper in Python",
    "config": {
      "agent_type": "zero-shot-react-description",
      "tools": ["python_repl", "web_search"],
      "verbose": True
    }
  }
)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
- Check the documentation in `AGENT_API_EXAMPLES.md`
- Review the test suite in `test_agent_api.py`
- Open an issue on GitHub