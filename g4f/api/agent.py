"""
LangChain Agent API for g4f
Provides agent functionality with tools, memory, and various agent types
"""

import time
import logging
from typing import Dict, List, Optional, Any
from contextlib import asynccontextmanager

from langchain.agents import (
    AgentExecutor, 
    create_react_agent,
    create_openai_functions_agent,
    create_structured_chat_agent,
    initialize_agent,
    AgentType
)
from langchain.agents.agent import AgentExecutor
from langchain_community.agent_toolkits.playwright.toolkit import PlayWrightBrowserToolkit
from langchain.agents.openai_functions_agent.base import OpenAIFunctionsAgent
from langchain.agents.react.base import DocstoreExplorer
from langchain.agents.self_ask_with_search.base import SelfAskWithSearchAgent
from langchain.agents.structured_chat.base import StructuredChatAgent
from langchain.agents.conversational_chat.base import ConversationalChatAgent
# ZeroShotAgent import removed - not available in this version
from langchain.chains.llm import LLMChain
from langchain.memory import ConversationBufferMemory, ConversationSummaryMemory
from langchain.prompts import PromptTemplate
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from langchain.tools import (
    Tool,
    BaseTool
)
from langchain_community.tools import (
    BaseTool
)
# Utilities removed - will be added later

from g4f.integration.langchain import ChatAI
from g4f.client import AsyncClient
from g4f.providers.response import BaseConversation, JsonConversation
from g4f.errors import ProviderNotFoundError, ModelNotFoundError, MissingAuthError, NoValidHarFileError

logger = logging.getLogger(__name__)

class AgentManager:
    """Manages LangChain agents with g4f integration"""
    
    def __init__(self):
        self.agents: Dict[str, AgentExecutor] = {}
        self.memories: Dict[str, Any] = {}
        self.conversations: Dict[str, Dict[str, BaseConversation]] = {}
        
    def get_available_tools(self) -> List[Tool]:
        """Get list of available tools"""
        tools = []
        
        # Tools removed - will be added later
        
        return tools
    
    def create_memory(self, memory_type: str = "conversation_buffer", **kwargs) -> Any:
        """Create memory instance"""
        if memory_type == "conversation_buffer":
            return ConversationBufferMemory(
                memory_key=kwargs.get("memory_key", "chat_history"),
                return_messages=kwargs.get("return_messages", True),
                input_key=kwargs.get("input_key", "input"),
                output_key=kwargs.get("output_key", "output")
            )
        elif memory_type == "conversation_summary":
            return ConversationSummaryMemory(
                llm=ChatAI(),
                memory_key=kwargs.get("memory_key", "chat_history"),
                return_messages=kwargs.get("return_messages", True),
                input_key=kwargs.get("input_key", "input"),
                output_key=kwargs.get("output_key", "output")
            )
        else:
            raise ValueError(f"Unsupported memory type: {memory_type}")
    
    def create_agent(self, 
                    agent_type: str = "zero-shot-react-description",
                    tools: Optional[List[str]] = None,
                    memory: Optional[bool] = False,
                    memory_config: Optional[Dict] = None,
                    **kwargs) -> AgentExecutor:
        """Create a LangChain agent"""
        
        # Get available tools
        available_tools = self.get_available_tools()
        
        # Filter tools based on request
        if tools:
            tool_names = [tool.name for tool in available_tools]
            filtered_tools = [tool for tool in available_tools if tool.name in tools]
            if len(filtered_tools) != len(tools):
                missing_tools = set(tools) - set(tool_names)
                logger.warning(f"Missing tools: {missing_tools}")
        else:
            filtered_tools = available_tools
        
        # Create LLM
        llm = ChatAI(**kwargs)
        
        # Create memory if requested
        memory_instance = None
        if memory and memory_config:
            memory_instance = self.create_memory(**memory_config)
        
        # Create agent based on type
        if agent_type == "zero-shot-react-description":
            agent = create_react_agent(llm, filtered_tools, verbose=kwargs.get("verbose", False))
        elif agent_type == "openai-functions":
            agent = create_openai_functions_agent(llm, filtered_tools, verbose=kwargs.get("verbose", False))
        elif agent_type == "structured-chat-zero-shot-react":
            agent = create_structured_chat_agent(llm, filtered_tools, verbose=kwargs.get("verbose", False))
        elif agent_type == "conversational-react-description":
            agent = initialize_agent(
                tools=filtered_tools,
                llm=llm,
                agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
                verbose=kwargs.get("verbose", False)
            )
        elif agent_type == "chat-zero-shot-react-description":
            agent = initialize_agent(
                tools=filtered_tools,
                llm=llm,
                agent=AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION,
                verbose=kwargs.get("verbose", False)
            )
        elif agent_type == "chat-conversational-react-description":
            agent = initialize_agent(
                tools=filtered_tools,
                llm=llm,
                agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
                verbose=kwargs.get("verbose", False)
            )
        else:
            # Default to zero-shot-react-description
            agent = create_react_agent(llm, filtered_tools, verbose=kwargs.get("verbose", False))
        
        # Create agent executor
        agent_executor = AgentExecutor.from_agent_and_tools(
            agent=agent,
            tools=filtered_tools,
            memory=memory_instance,
            verbose=kwargs.get("verbose", False),
            max_iterations=kwargs.get("max_iterations", 10),
            early_stopping_method=kwargs.get("early_stopping_method", "generate"),
            handle_parsing_errors=kwargs.get("handle_parsing_errors", True),
            return_intermediate_steps=kwargs.get("return_intermediate_steps", False)
        )
        
        return agent_executor
    
    async def run_agent(self, 
                       input_text: str,
                       conversation_id: Optional[str] = None,
                       config: Optional[Dict] = None) -> Dict[str, Any]:
        """Run an agent with the given input"""
        
        start_time = time.time()
        
        # Default configuration
        if config is None:
            config = {}
        
        # Create or get agent
        agent_key = f"{conversation_id}_{config.get('agent_type', 'default')}"
        
        if agent_key not in self.agents:
            self.agents[agent_key] = self.create_agent(**config)
        
        agent = self.agents[agent_key]
        
        try:
            # Run the agent
            result = await agent.ainvoke({"input": input_text})
            
            execution_time = time.time() - start_time
            
            return {
                "output": result.get("output", ""),
                "intermediate_steps": result.get("intermediate_steps", []),
                "conversation_id": conversation_id,
                "model": config.get("model"),
                "provider": config.get("provider"),
                "agent_type": config.get("agent_type", "zero-shot-react-description"),
                "execution_time": execution_time
            }
            
        except Exception as e:
            logger.exception(f"Error running agent: {e}")
            raise
    
    def get_memory(self, conversation_id: str) -> Optional[Any]:
        """Get memory for a conversation"""
        return self.memories.get(conversation_id)
    
    def clear_memory(self, conversation_id: str) -> bool:
        """Clear memory for a conversation"""
        if conversation_id in self.memories:
            del self.memories[conversation_id]
            return True
        return False
    
    def add_to_memory(self, conversation_id: str, input_text: str, output_text: str) -> bool:
        """Add interaction to memory"""
        if conversation_id not in self.memories:
            self.memories[conversation_id] = self.create_memory()
        
        memory = self.memories[conversation_id]
        memory.save_context({"input": input_text}, {"output": output_text})
        return True

# Global agent manager instance
agent_manager = AgentManager() 