#!/usr/bin/env python3
"""
Test script for refresh functionality
"""

import asyncio
from pathlib import Path

from fs_mcp_server.main import handle_list_tools, handle_refresh_resources


async def test_refresh() -> None:
    """Test the refresh functionality"""

    print("Testing MCP Filesystem Server Refresh Functionality")
    print("=" * 60)

    # Test list_tools
    print("\n1. Testing list_tools:")
    tools = await handle_list_tools()
    print(f"Found {len(tools)} tools:")
    for tool in tools:
        print(f"  - {tool.name}: {tool.description}")

    # Test refresh_resources tool
    print("\n2. Testing refresh_resources tool:")
    result = await handle_refresh_resources("refresh_resources", {})
    print(f"Refresh result: {result[0].text}")

    # Create a new test file
    print("\n3. Creating new test file:")
    test_file = Path("storage/new_test.txt")
    with open(test_file, "w") as f:
        f.write("This is a new test file created during refresh test")
    print(f"Created: {test_file}")

    # Test refresh again
    print("\n4. Testing refresh after adding new file:")
    result = await handle_refresh_resources("refresh_resources", {})
    print(f"Refresh result: {result[0].text}")

    # Clean up
    test_file.unlink()
    print(f"Cleaned up: {test_file}")

    print("\nRefresh test completed successfully!")


if __name__ == "__main__":
    asyncio.run(test_refresh())
