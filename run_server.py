#!/usr/bin/env python3
"""
Simple script to run the MCP filesystem server.
"""

import asyncio
import sys
from pathlib import Path

# Add the project directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from fs_mcp_server.main import main

if __name__ == "__main__":
    print("Starting MCP Filesystem Server...")
    print("Press Ctrl+C to stop")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer stopped.")
