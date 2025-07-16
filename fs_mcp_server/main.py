#!/usr/bin/env python3
"""
Filesystem MCP Server

A Model Context Protocol server that exposes filesystem resources.
Resources are accessible via URIs like: docstore://path/to/file
"""

import logging
from pathlib import Path

import mcp.server.stdio
import mcp.types as types
from mcp.server import Server
from pydantic import AnyUrl

from .config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("fs-mcp-server")

# Load configuration
config = Config()
storage_path = config.get_storage_path()
storage_path.mkdir(parents=True, exist_ok=True)

# URI scheme prefix
URI_SCHEME = "docstore://"

# Initialize the server
server = Server(config.get("server_name"))


@server.list_resources()
async def handle_list_resources() -> list[types.Resource]:
    """
    List all available filesystem resources.
    Each file in the storage directory becomes a resource.
    """
    resources = []

    if storage_path.exists():
        for file_path in storage_path.rglob("*"):
            if (
                file_path.is_file()
                and config.is_file_allowed(file_path)
                and config.is_file_size_allowed(file_path)
            ):

                # Create relative path from storage root
                rel_path = file_path.relative_to(storage_path)
                uri = f"{URI_SCHEME}{rel_path}"

                resources.append(
                    types.Resource(
                        uri=uri,
                        name=str(rel_path),
                        description=f"File: {rel_path}",
                        mimeType=_get_mime_type(file_path),
                    )
                )

    return resources


@server.call_tool()
async def handle_refresh_resources(
    name: str, arguments: dict
) -> list[types.TextContent]:
    """
    Refresh resources by re-scanning the filesystem.

    Args:
        name: The tool name (should be "refresh_resources")
        arguments: Tool arguments (unused)

    Returns:
        Status message about the refresh operation
    """
    if name != "refresh_resources":
        raise ValueError(f"Unknown tool: {name}")

    try:
        # Re-scan the filesystem by calling list_resources
        resources = await handle_list_resources()
        count = len(resources)
        logger.info(f"Refreshed {count} resources")

        return [
            types.TextContent(
                type="text",
                text=f"Successfully refreshed {count} resources from filesystem",
            )
        ]
    except Exception as e:
        logger.error(f"Error refreshing resources: {e}")
        return [
            types.TextContent(type="text", text=f"Error refreshing resources: {str(e)}")
        ]


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    List available tools.
    """
    return [
        types.Tool(
            name="refresh_resources",
            description="Refresh the list of available filesystem resources",
            inputSchema={"type": "object", "properties": {}, "required": []},
        )
    ]


@server.read_resource()
async def handle_read_resource(uri: AnyUrl) -> str:
    """
    Read a specific filesystem resource.

    Args:
        uri: The resource URI (e.g., docstore://path/to/file)

    Returns:
        The file contents as a string
    """
    if not str(uri).startswith(URI_SCHEME):
        raise ValueError(f"Unsupported URI scheme: {uri}")

    # Parse the URI to get the file path
    uri_str = str(uri)
    if not uri_str.startswith(URI_SCHEME):
        raise ValueError(f"Unsupported URI scheme: {uri_str}")

    # Extract the path after URI scheme
    rel_path = uri_str[len(URI_SCHEME) :]  # Remove URI scheme prefix
    file_path = storage_path / rel_path

    # Security check: ensure the file is within storage directory
    try:
        file_path.resolve().relative_to(storage_path.resolve())
    except ValueError as e:
        raise ValueError(
            f"Access denied: {rel_path} is outside storage directory"
        ) from e

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {rel_path}")

    if not file_path.is_file():
        raise ValueError(f"Not a file: {rel_path}")

    if not config.is_file_allowed(file_path):
        raise ValueError(f"File type not allowed: {rel_path}")

    if not config.is_file_size_allowed(file_path):
        raise ValueError(f"File too large: {rel_path}")

    try:
        with open(file_path, encoding="utf-8") as f:
            return f.read()
    except UnicodeDecodeError:
        # If it's a binary file, read it as bytes and return base64
        with open(file_path, "rb") as f:
            import base64

            content = base64.b64encode(f.read()).decode("utf-8")
            return f"Binary file (base64): {content}"


def _get_mime_type(file_path: Path) -> str:
    """Get MIME type based on file extension."""
    suffix = file_path.suffix.lower()
    mime_types = {
        ".txt": "text/plain",
        ".md": "text/markdown",
        ".json": "application/json",
        ".py": "text/x-python",
        ".js": "text/javascript",
        ".html": "text/html",
        ".css": "text/css",
        ".xml": "application/xml",
        ".yaml": "application/x-yaml",
        ".yml": "application/x-yaml",
    }
    return mime_types.get(suffix, "application/octet-stream")


async def main() -> None:
    """Run the server using stdio transport."""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream, write_stream, server.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
