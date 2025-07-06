# LangChain Agent API Examples

This document provides examples of how to use the new LangChain Agent API with g4f.

## Overview

The Agent API provides LangChain agent functionality with the following features:
- Multiple agent types (zero-shot-react-description, openai-functions, structured-chat, etc.)
- Built-in tools (search, Wikipedia, YouTube, arXiv, Python REPL, shell, web requests)
- Memory management (conversation buffer, summary memory)
- Provider-specific agents
- Conversation persistence

## Available Endpoints

### 1. Get Available Tools
```bash
GET /v1/agent/tools
```

Returns a list of available tools that can be used with agents.

### 2. Run Agent
```bash
POST /v1/agent/run
POST /api/{provider}/agent/run
```

Runs a LangChain agent with the given input and configuration.

### 3. Manage Memory
```bash
POST /v1/agent/memory
```

Manages agent memory operations (get, clear, add).

## Examples

### Basic Agent Usage

#### Simple Agent Request
```bash
curl -X POST "http://localhost:1337/v1/agent/run" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-api-key" \
  -d '{
    "input": "What is the current weather in New York?",
    "config": {
      "agent_type": "zero-shot-react-description",
      "tools": ["duckduckgo_search"],
      "verbose": true
    }
  }'
```

#### Agent with Memory
```bash
curl -X POST "http://localhost:1337/v1/agent/run" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-api-key" \
  -d '{
    "input": "What did we talk about earlier?",
    "conversation_id": "conv_123",
    "config": {
      "agent_type": "conversational-react-description",
      "memory": true,
      "memory_config": {
        "memory_type": "conversation_buffer",
        "memory_key": "chat_history"
      },
      "tools": ["duckduckgo_search", "wikipedia"]
    }
  }'
```

#### Provider-Specific Agent
```bash
curl -X POST "http://localhost:1337/api/gemini/agent/run" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-api-key" \
  -d '{
    "input": "Write a Python function to calculate fibonacci numbers",
    "config": {
      "agent_type": "openai-functions",
      "tools": ["python_repl"],
      "max_iterations": 5
    }
  }'
```

### Advanced Agent Configurations

#### Research Agent
```bash
curl -X POST "http://localhost:1337/v1/agent/run" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-api-key" \
  -d '{
    "input": "Research the latest developments in quantum computing",
    "config": {
      "agent_type": "structured-chat-zero-shot-react",
      "tools": ["duckduckgo_search", "wikipedia", "arxiv_search"],
      "verbose": true,
      "max_iterations": 15,
      "return_intermediate_steps": true
    }
  }'
```

#### Programming Assistant
```bash
curl -X POST "http://localhost:1337/v1/agent/run" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-api-key" \
  -d '{
    "input": "Create a web scraper in Python that extracts data from a website",
    "config": {
      "agent_type": "zero-shot-react-description",
      "tools": ["python_repl", "web_search"],
      "verbose": true,
      "max_iterations": 10
    }
  }'
```

#### Multi-Modal Agent (with vision)
```bash
curl -X POST "http://localhost:1337/v1/agent/run" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-api-key" \
  -d '{
    "input": "Analyze this image and describe what you see",
    "config": {
      "agent_type": "openai-functions",
      "model": "gpt-4o",
      "provider": "openai",
      "tools": ["duckduckgo_search"],
      "verbose": true
    }
  }'
```

### Memory Management

#### Get Memory
```bash
curl -X POST "http://localhost:1337/v1/agent/memory" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-api-key" \
  -d '{
    "conversation_id": "conv_123",
    "action": "get"
  }'
```

#### Clear Memory
```bash
curl -X POST "http://localhost:1337/v1/agent/memory" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-api-key" \
  -d '{
    "conversation_id": "conv_123",
    "action": "clear"
  }'
```

#### Add to Memory
```bash
curl -X POST "http://localhost:1337/v1/agent/memory" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-api-key" \
  -d '{
    "conversation_id": "conv_123",
    "action": "add",
    "input": "What is the capital of France?",
    "output": "The capital of France is Paris."
  }'
```

## Available Tools

### Search Tools
- `duckduckgo_search`: Search the web for current information
- `wikipedia`: Search Wikipedia for information
- `youtube_search`: Search YouTube for videos
- `arxiv_search`: Search arXiv for academic papers
- `pubmed_search`: Search PubMed for medical research

### Programming Tools
- `python_repl`: Execute Python code
- `shell`: Execute shell commands

### Web Tools
- `web_search`: Search the web using GET requests
- `web_post`: Make POST requests to web APIs

### Utility Tools
- `human_input`: Ask for human input when needed

## Agent Types

### 1. zero-shot-react-description
Default agent type that can use tools without prior examples.

### 2. openai-functions
Uses OpenAI function calling format for tool usage.

### 3. structured-chat-zero-shot-react
Structured chat agent with zero-shot tool usage.

### 4. conversational-react-description
Conversational agent with memory support.

### 5. chat-zero-shot-react-description
Chat-based zero-shot agent.

### 6. chat-conversational-react-description
Chat-based conversational agent.

## Configuration Options

### AgentConfig
- `model`: The model to use (default: from AppConfig)
- `provider`: The provider to use (default: from AppConfig)
- `api_key`: API key for the provider
- `tools`: List of tool names to enable
- `agent_type`: Type of agent to create
- `verbose`: Enable verbose output
- `max_iterations`: Maximum number of iterations
- `early_stopping_method`: Method for early stopping
- `return_intermediate_steps`: Return intermediate steps
- `handle_parsing_errors`: Handle parsing errors gracefully
- `memory`: Enable memory
- `memory_key`: Key for memory storage
- `input_key`: Key for input
- `output_key`: Key for output

### MemoryConfig
- `memory_type`: Type of memory (conversation_buffer, conversation_summary)
- `max_token_limit`: Maximum tokens for memory
- `return_messages`: Return messages format
- `input_key`: Key for input
- `output_key`: Key for output
- `memory_key`: Key for memory storage

## Error Handling

The API returns appropriate HTTP status codes:
- `200`: Success
- `401`: Unauthorized (invalid API key)
- `404`: Not found (model/provider not found)
- `422`: Validation error
- `500`: Internal server error

## Python Client Example

```python
import requests
import json

class AgentClient:
    def __init__(self, base_url="http://localhost:1337", api_key=None):
        self.base_url = base_url
        self.headers = {"Content-Type": "application/json"}
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"
    
    def run_agent(self, input_text, config=None, conversation_id=None):
        data = {
            "input": input_text,
            "config": config,
            "conversation_id": conversation_id
        }
        
        response = requests.post(
            f"{self.base_url}/v1/agent/run",
            headers=self.headers,
            json=data
        )
        return response.json()
    
    def get_tools(self):
        response = requests.get(
            f"{self.base_url}/v1/agent/tools",
            headers=self.headers
        )
        return response.json()
    
    def manage_memory(self, conversation_id, action, input_text=None, output_text=None):
        data = {
            "conversation_id": conversation_id,
            "action": action
        }
        if input_text:
            data["input"] = input_text
        if output_text:
            data["output"] = output_text
            
        response = requests.post(
            f"{self.base_url}/v1/agent/memory",
            headers=self.headers,
            json=data
        )
        return response.json()

# Usage example
client = AgentClient(api_key="your-api-key")

# Run a simple agent
result = client.run_agent(
    "What is the weather like today?",
    config={
        "agent_type": "zero-shot-react-description",
        "tools": ["duckduckgo_search"]
    }
)
print(result["output"])

# Get available tools
tools = client.get_tools()
print(f"Available tools: {[tool['name'] for tool in tools['tools']]}")
```

## Best Practices

1. **Use appropriate agent types**: Choose the agent type based on your use case
2. **Limit tool usage**: Only enable necessary tools to reduce complexity
3. **Set reasonable iteration limits**: Prevent infinite loops
4. **Use conversation IDs**: For multi-turn conversations
5. **Handle errors gracefully**: Check response status codes
6. **Monitor execution time**: Use the returned execution_time field
7. **Clean up memory**: Clear memory when conversations are complete

## Troubleshooting

### Common Issues

1. **Tool not available**: Check if the tool is listed in `/v1/agent/tools`
2. **Provider not found**: Verify the provider name and API key
3. **Memory issues**: Ensure conversation_id is consistent
4. **Timeout errors**: Increase max_iterations or simplify the task
5. **Parsing errors**: Set handle_parsing_errors to true

### Debug Mode

Enable verbose output in the agent configuration to see detailed execution steps:

```json
{
  "config": {
    "verbose": true,
    "return_intermediate_steps": true
  }
}
``` 