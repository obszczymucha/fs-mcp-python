#!/usr/bin/env python3
"""
Test script for the filesystem MCP server.
This script tests the server functionality by directly calling the handler functions.
"""

import asyncio
import sys
from pathlib import Path

# Add the project directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from fs_mcp_server.main import (
    config,
    handle_list_resources,
    handle_read_resource,
    storage_path,
)


async def test_server() -> None:
    """Test the MCP server functionality."""
    print("Testing MCP Filesystem Server")
    print("=" * 40)

    # Test configuration
    print(f"Server name: {config.get('server_name')}")
    print(f"Storage path: {storage_path}")
    print(f"Storage path exists: {storage_path.exists()}")

    # List files in storage
    print("\nFiles in storage directory:")
    if storage_path.exists():
        for file_path in storage_path.rglob("*"):
            if file_path.is_file():
                rel_path = file_path.relative_to(storage_path)
                print(f"  - {rel_path}")

    # Test list_resources
    print("\nTesting list_resources:")
    try:
        resources = await handle_list_resources()

        if resources:
            print(f"Found {len(resources)} resources:")
            for resource in resources:
                print(f"  - {resource.uri} ({resource.mimeType})")
        else:
            print("No resources found")
    except Exception as e:
        print(f"Error in list_resources: {e}")
        return

    # Test read_resource
    if resources:
        print("\nTesting read_resource:")
        for resource in resources[:3]:  # Test first 3 resources
            try:
                content = await handle_read_resource(resource.uri)
                print(f"\n--- Content of {resource.uri} ---")
                if len(content) > 200:
                    print(content[:200] + "...")
                else:
                    print(content)
            except Exception as e:
                print(f"Error reading {resource.uri}: {e}")

    print("\nTest completed successfully!")


if __name__ == "__main__":
    asyncio.run(test_server())
