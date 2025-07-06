#!/usr/bin/env python3
"""
Startup script for the Flashcards API with LangChain Agent Support
"""

import argparse
import os
import sys
from g4f.api import run_api, AppConfig

def main():
    parser = argparse.ArgumentParser(description="Start the Flashcards API server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=1337, help="Port to bind to (default: 1337)")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--gui", action="store_true", help="Enable GUI mode")
    parser.add_argument("--demo", action="store_true", help="Enable demo mode")
    parser.add_argument("--timeout", type=int, default=600, help="Request timeout in seconds (default: 600)")
    parser.add_argument("--api-key", help="API key for authentication")
    parser.add_argument("--model", help="Default model to use")
    parser.add_argument("--provider", help="Default provider to use")
    parser.add_argument("--media-provider", help="Default media provider to use")
    parser.add_argument("--proxy", help="Proxy configuration")
    parser.add_argument("--ignore-cookies", action="store_true", help="Ignore cookie files")
    parser.add_argument("--ignored-providers", nargs="+", help="List of providers to ignore")
    
    args = parser.parse_args()
    
    # Set configuration from command line arguments
    config_updates = {}
    
    if args.api_key:
        config_updates["g4f_api_key"] = args.api_key
    if args.model:
        config_updates["model"] = args.model
    if args.provider:
        config_updates["provider"] = args.provider
    if args.media_provider:
        config_updates["media_provider"] = args.media_provider
    if args.proxy:
        config_updates["proxy"] = args.proxy
    if args.ignore_cookies:
        config_updates["ignore_cookie_files"] = True
    if args.ignored_providers:
        config_updates["ignored_providers"] = args.ignored_providers
    if args.gui:
        config_updates["gui"] = True
    if args.demo:
        config_updates["demo"] = True
    if args.timeout:
        config_updates["timeout"] = args.timeout
    
    # Apply configuration
    if config_updates:
        AppConfig.set_config(**config_updates)
    
    # Print startup information
    print("🚀 Starting Flashcards API with LangChain Agent Support")
    print("=" * 60)
    print(f"📍 Server: http://{args.host}:{args.port}")
    print(f"🔧 Debug: {args.debug}")
    print(f"🖥️  GUI: {args.gui}")
    print(f"🎯 Demo: {args.demo}")
    print(f"⏱️  Timeout: {args.timeout}s")
    
    if args.model:
        print(f"🤖 Default Model: {args.model}")
    if args.provider:
        print(f"🔌 Default Provider: {args.provider}")
    if args.media_provider:
        print(f"🎨 Media Provider: {args.media_provider}")
    
    print("=" * 60)
    print("📖 API Documentation: http://localhost:1337/docs")
    print("🔧 Agent API Examples: See AGENT_API_EXAMPLES.md")
    print("🧪 Test Suite: python test_agent_api.py")
    print("=" * 60)
    
    try:
        # Start the server
        run_api(
            host=args.host,
            port=args.port,
            debug=args.debug,
            use_colors=args.debug
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 