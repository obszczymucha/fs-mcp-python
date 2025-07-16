"""Configuration management for filesystem MCP server."""

import json
import os
from pathlib import Path
from typing import Any


class Config:
    """Configuration manager for the filesystem MCP server."""

    def __init__(self, config_path: str | None = None) -> None:
        """Initialize configuration."""
        if config_path is None:
            config_path = os.environ.get("FS_MCP_CONFIG", "config.json")

        self.config_path = Path(config_path)
        self._config = self._load_config()

    def _load_config(self) -> dict[str, Any]:
        """Load configuration from file or environment variables."""
        config = {
            "storage_path": "./storage",
            "server_name": "filesystem-mcp-server",
            "version": "1.0.0",
            "max_file_size": 10 * 1024 * 1024,  # 10MB
            "allowed_extensions": None,  # None means all extensions allowed
            "description": "MCP server for filesystem resources",
        }

        # Load from config file if it exists
        if self.config_path.exists():
            try:
                with open(self.config_path) as f:
                    file_config = json.load(f)
                    config.update(file_config)
            except (OSError, json.JSONDecodeError) as e:
                print(f"Warning: Could not load config file {self.config_path}: {e}")

        # Override with environment variables
        if os.environ.get("FS_MCP_STORAGE_PATH"):
            config["storage_path"] = os.environ["FS_MCP_STORAGE_PATH"]

        if os.environ.get("FS_MCP_SERVER_NAME"):
            config["server_name"] = os.environ["FS_MCP_SERVER_NAME"]

        if os.environ.get("FS_MCP_MAX_FILE_SIZE"):
            try:
                config["max_file_size"] = int(os.environ["FS_MCP_MAX_FILE_SIZE"])
            except ValueError:
                print("Warning: Invalid max file size in environment variable")

        return config

    def get(self, key: str, default: object = None) -> object:
        """Get configuration value."""
        return self._config.get(key, default)

    def get_storage_path(self) -> Path:
        """Get storage path as Path object."""
        return Path(self._config["storage_path"]).resolve()

    def is_file_allowed(self, file_path: Path) -> bool:
        """Check if file is allowed based on configuration."""
        allowed_extensions = self._config.get("allowed_extensions")
        if allowed_extensions is None:
            return True

        return file_path.suffix.lower() in allowed_extensions

    def is_file_size_allowed(self, file_path: Path) -> bool:
        """Check if file size is within limits."""
        max_size = self._config.get("max_file_size", 10 * 1024 * 1024)
        if not file_path.exists():
            return True

        return file_path.stat().st_size <= max_size

    def save_config(self) -> None:
        """Save current configuration to file."""
        try:
            with open(self.config_path, "w") as f:
                json.dump(self._config, f, indent=2)
        except OSError as e:
            print(f"Error saving config file: {e}")

    def update_storage_path(self, new_path: str) -> None:
        """Update storage path and save configuration."""
        self._config["storage_path"] = new_path
        self.save_config()
        print(f"Storage path updated to: {new_path}")

    def __str__(self) -> str:
        """String representation of config."""
        return json.dumps(self._config, indent=2)
