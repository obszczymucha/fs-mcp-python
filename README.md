# Filesystem MCP Server

A Model Context Protocol (MCP) server that exposes filesystem resources through standardized URIs like `docstore://path/to/file`.

## Features

- **Resource Access**: Access files using `docstore://` URIs
- **Configurable Storage**: Set local directory for file storage
- **Security**: Path traversal protection and file size limits
- **MIME Types**: Automatic MIME type detection
- **Binary Support**: Base64 encoding for binary files

## Installation

1. Install dependencies:
```bash
uv sync
```

2. Run the server:
```bash
uv run python -m fs_mcp_server.main
```

## Configuration

Configure the server using `config.json`:

```json
{
  "storage_path": "./storage",
  "server_name": "filesystem-mcp-server",
  "version": "1.0.0",
  "max_file_size": 10485760,
  "allowed_extensions": null,
  "description": "MCP server for filesystem resources"
}
```

### Configuration Options

- `storage_path`: Local directory to serve files from
- `server_name`: Name of the MCP server
- `max_file_size`: Maximum file size in bytes (default: 10MB)
- `allowed_extensions`: List of allowed file extensions (null = all allowed)

### Environment Variables

- `FS_MCP_CONFIG`: Path to config file
- `FS_MCP_STORAGE_PATH`: Override storage path
- `FS_MCP_SERVER_NAME`: Override server name
- `FS_MCP_MAX_FILE_SIZE`: Override max file size

## Usage

### Resource URIs

Files in the storage directory are accessible via URIs:

- `docstore://test.txt` → `{storage_path}/test.txt`
- `docstore://docs/readme.md` → `{storage_path}/docs/readme.md`

### Example Client Code

```python
import asyncio
from mcp.client import create_client

async def main():
    # Connect to the server
    client = await create_client("fs-mcp-server")
    
    # List available resources
    resources = await client.list_resources()
    print(f"Available resources: {len(resources)}")
    
    # Read a specific resource
    content = await client.read_resource("docstore://test.txt")
    print(f"Content: {content}")

asyncio.run(main())
```

## Testing

Run the included test scripts:

```bash
uv run python test_server.py
uv run python test_refresh.py
```

Run linting:

```bash
uv run ruff check
```

Format code:

```bash
uv run black .
```

## Security

The server includes several security features:

- Path traversal protection (files must be within storage directory)
- File size limits (configurable)
- File type filtering (optional)
- Binary file handling (base64 encoding)

## File Structure

```
fs-mcp-server/
├── fs_mcp_server/
│   ├── __init__.py
│   ├── main.py          # Main server implementation
│   └── config.py        # Configuration management
├── storage/             # Default file storage directory
│   ├── test.txt
│   ├── config.json
│   └── docs/
│       └── readme.md
├── config.json          # Server configuration
├── pyproject.toml       # Python project configuration
├── test_server.py       # Test script
└── README.md           # This file
```
